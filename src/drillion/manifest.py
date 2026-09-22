"""Grading a manifest: the brief a sitting is graded against, and how it is produced.

`grade.py` is task-authored Python. It is loaded and run only inside the sandboxed child
that `sandbox.run_script` starts, and it talks back in JSON. The server never imports it."""

import hashlib
import json
import math
import os
import re
import stat
import string
import subprocess
import tempfile
from pathlib import Path

import yaml

from . import sandbox, tools
from .catalogue import DOCKER, MANIFEST, solution

MAX_BRIEF_BYTES = 8192
MAX_RESULT_BYTES = 64 << 10
MAX_SPEC_CHARS = 65536
SCALARS = (str, int, float, bool)
BRIEF_SECONDS = 30
GRADE_SECONDS = 60
VALIDATOR_SECONDS = 30

# Runs inside the sandbox, with the grader path, seed, output path and module name as argv.
# `drillion.guard` first because on the guard tier its audit hook is the only confinement
# there is, and it installs on import. A kernel tier denies the read instead, which is the
# same answer by a stronger route, so failing to find it is not an error here.
_BRIEF_SOURCE = """
try:
    import drillion.guard
except ImportError, OSError:
    pass

import importlib.util, json, random, sys

path, seed, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
spec = importlib.util.spec_from_file_location(sys.argv[4], path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
text = json.dumps(module.brief(random.Random(seed)))
with open(out, "w", encoding="utf-8") as stream:
    stream.write(text)
"""


class Rejected(Exception):
    """Nothing was graded, and nothing about the learner's answer is known. Every one of
    these is infrastructure or a task-authoring bug, so the API answers them with a 503
    carrying the message rather than with a failing test."""


class ToolMissing(Rejected):
    """The external grader is not installed. Never a learner's mistake."""


def _validated(raw):
    """A brief is a flat mapping of string keys to finite scalars. Anything else is a
    task-authoring bug, and one that would otherwise reach a template or an assert."""
    if not isinstance(raw, dict):
        raise Rejected("brief() must return a mapping")
    for key, value in raw.items():
        if not isinstance(key, str) or not key.isidentifier():
            raise Rejected(f"brief key {key!r} is not a plain name")
        if not isinstance(value, SCALARS):
            raise Rejected(f"brief value for {key!r} is not a scalar")
        if isinstance(value, float) and not math.isfinite(value):
            raise Rejected(f"brief value for {key!r} is not a finite number")
    return raw


def grader_revision(meta):
    """Which generator produced a stored brief, so a later run can say whether an upgrade
    has moved the question underneath it. Every file it takes to make one is hashed, each
    by its own digest so nothing shifts between them: `grade.py`, the answer key, and every
    file the task ships around the learner's, named, since editing one changes the question
    too."""
    digest = hashlib.sha256()
    for path in (meta["dir"] / "grade.py", solution(meta)):
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    for path in chart_files(meta):
        digest.update(hashlib.sha256(path.encode()).digest())
        digest.update(hashlib.sha256((shipped(meta) / path).read_bytes()).digest())
    return digest.hexdigest()[:12]


def shipped(meta):
    """The folder a task ships around the learner's file: a Helm chart, or the build
    context a Dockerfile is written for."""
    return meta["dir"] / ("context" if meta.get("kind") == DOCKER else "chart")


def chart_files(meta):
    """Every file `shipped` holds, by its path inside it; [] for a task with none.
    `Chart.yaml` and the values come first, then the rest in path order, which is the order
    the learner's tabs show them in."""
    chart = shipped(meta)
    if not chart.is_dir():
        return []
    first = {"Chart.yaml": 0, "values.yaml": 1, "values.schema.json": 2}
    # the image compiles every shipped .py, so a context's app.py gains a __pycache__
    paths = [
        p.relative_to(chart).as_posix()
        for p in chart.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    ]
    return sorted(paths, key=lambda p: (first.get(p, len(first)), p))


def module_name(slug):
    """A unique module name per task, so two graders cannot share state in selfcheck."""
    return f"drillion_grade_{slug}"


def generate_brief(meta, seed):
    """The requirements for one sitting, produced by the task's own code, in the sandbox.

    The child shares its `sys.argv`, so the grader can write the output file itself instead
    of returning from `brief()`. What comes back is validated either way."""
    grader = meta["dir"] / "grade.py"
    with tempfile.TemporaryDirectory(
        dir=sandbox.scratch_root(), ignore_cleanup_errors=True
    ) as scratch:
        scratch = Path(scratch)
        script = scratch / "_brief.py"
        script.write_text(_BRIEF_SOURCE, encoding="utf-8")
        out = scratch / "brief.json"
        try:
            result = sandbox.run_script(
                [
                    str(script),
                    str(grader),
                    str(seed),
                    str(out),
                    module_name(meta["dir"].name),
                ],
                scratch,
                BRIEF_SECONDS,
            )
        except subprocess.TimeoutExpired:
            raise Rejected("brief() did not finish") from None
        if result.returncode != 0:
            raise Rejected(f"brief() failed: {result.stderr.strip()[-500:]}")
        return _read_brief(out)


def _read_brief(out):
    return _validated(_read_json(out, MAX_BRIEF_BYTES, "brief()"))


def _read_json(out, cap, what):
    """Read back what a child wrote, as the one file object the size check looked at.

    The child owns the scratch directory, so it can unlink `out` and leave a symlink or a
    fifo in its place. The lstat/open/fstat identity check prevents following a replacement,
    `O_NOFOLLOW` rejects a symlink at open and `O_NONBLOCK` keeps a fifo from wedging this
    thread."""
    try:
        before = os.lstat(out)
        if not stat.S_ISREG(before.st_mode):
            raise Rejected(f"{what} wrote something that is not a plain file")
        fd = os.open(out, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError:
        raise Rejected(f"{what} wrote nothing") from None
    with open(fd, encoding="utf-8") as stream:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or not os.path.samestat(before, info):
            raise Rejected(f"{what} wrote something that is not a plain file")
        if info.st_size > cap:
            raise Rejected(f"{what} wrote too much")
        try:
            return json.loads(stream.read())
        except ValueError as exc:
            raise Rejected(f"{what} is not valid JSON: {exc}") from None


def render(template, brief):
    """Plain-text substitution for a README. Doubled braces stay literal, as in str.format.

    A placeholder is a bare name and nothing else. Every other shape is a task-authoring
    bug and comes back as `Rejected` before anything is formatted: a conversion, attribute
    or index traversal like `{name.title}` or `{replicas[0]}`, and above all a format spec,
    since a width like `{name:>1000000000}` allocates in the one process that has no
    `RLIMIT_AS`."""
    try:
        for _, field, spec, conversion in string.Formatter().parse(template):
            if field is not None and (not field.isidentifier() or spec or conversion):
                raise Rejected(
                    f"the spec template has a placeholder {{{field}}} that is "
                    "not a plain name"
                )
        filled = template.format(**brief)
    except (LookupError, ValueError, AttributeError, TypeError, MemoryError) as exc:
        raise Rejected(f"the spec template does not match the brief: {exc}") from None
    if len(filled) > MAX_SPEC_CHARS:
        raise Rejected("the filled spec is too long")
    return filled


_WHOLE_SCALAR = re.compile(
    r"^(?P<lead>[^\S\n]*(?:- )?(?:[\w.-]+:[^\S\n]+)?)\{(\w+)\}[^\S\n]*$"
)
_ANY_PLACEHOLDER = re.compile(r"(?<!\{)\{(\w+)\}")


def render_solution(meta, brief, parse=True):
    """Render this sitting's reference with each placeholder as a typed YAML scalar.

    `parse=False` is for an answer key that is a Helm template: it is not YAML until Helm
    renders it, so it is only checked for placeholders, and a template has none."""
    template = solution(meta).read_text(encoding="utf-8")
    out = []
    for number, line in enumerate(template.split("\n"), 1):
        match = _WHOLE_SCALAR.match(line)
        if match:
            key = match.group(2)
            if key not in brief:
                raise Rejected(
                    f"solution.yaml line {number}: no brief value for {key!r}"
                )
            out.append(match.group("lead") + _scalar(brief[key]))
        elif _ANY_PLACEHOLDER.search(line):
            raise Rejected(
                f"solution.yaml line {number}: a placeholder must be a whole value; "
                "build the combined value in brief() instead"
            )
        else:
            out.append(line)
    rendered = "\n".join(out)
    if not parse:
        return rendered
    try:
        # an answer key may hold several objects, `---`-separated, so validate them all
        list(yaml.safe_load_all(rendered))
    except yaml.YAMLError as exc:
        raise Rejected(f"the rendered solution is not valid YAML: {exc}") from None
    return rendered


def _scalar(value):
    """One YAML value with its type and quoting intact."""
    return (
        yaml.safe_dump(value, default_flow_style=True, width=1 << 30)
        .strip()
        .removesuffix("\n...")
    )


# `grading.py` as text: the runner writes it into the scratch directory and runs it there
GRADE_SOURCE = (Path(__file__).parent / "grading.py").read_text(encoding="utf-8")


def helm_job(meta):
    """What the child needs to put a Helm task's chart together and render it."""
    tool = tools.installed(tools.HELM)
    if tool is None:
        raise ToolMissing("helm is not installed: run `drillion doctor --fetch`")
    chart = meta["dir"] / "chart"
    name = yaml.safe_load((chart / "Chart.yaml").read_text(encoding="utf-8"))["name"]
    return {
        "tool": str(tool),
        "chart": str(chart),
        "name": name,
        "edits": meta["edits"],
        "files": [meta["edits"], *chart_files(meta)],
    }


# drillion's own hadolint config: errors and warnings fail, info is advice. Pinning every
# apt or apk package version is switched off, since a pinned Debian version leaves the
# mirror and few teams follow it. Part of a Dockerfile verdict's fingerprint.
HADOLINT_CONFIG = {"failure-threshold": "warning", "ignored": ["DL3008", "DL3018"]}


def docker_job(meta):
    """What the child needs to lint a Dockerfile and check it against its build context."""
    tool = tools.installed(tools.HADOLINT)
    if tool is None:
        raise ToolMissing("hadolint is not installed: run `drillion doctor --fetch`")
    return {
        "tool": str(tool),
        "context": str(shipped(meta)),
        "config": HADOLINT_CONFIG,
    }


def job(meta, brief, learner=None, helm=None, docker=None):
    """Everything the child needs to grade one sitting, as plain data.

    `learner` is the file to grade, and defaults to the learner's own. A self-check grades
    the answer key instead, and passes the path it rendered it to. `helm` is `helm_job`'s
    answer for a Helm task and `docker` is `docker_job`'s for a Dockerfile task; a manifest
    has neither. A Dockerfile needs no kubeconform, so it is not asked for one."""
    tool = tools.installed(tools.KUBECONFORM)
    if tool is None and docker is None:
        raise ToolMissing("kubeconform is not installed: run `drillion doctor --fetch`")
    return {
        "kind": meta.get("kind", MANIFEST),
        "helm": helm,
        "docker": docker,
        "learner": str(learner or meta["path"]),
        "grader": str(meta["dir"] / "grade.py"),
        "module": module_name(meta["dir"].name),
        "brief": brief,
        "tool": str(tool) if tool else None,
        "kubernetes": tools.KUBERNETES_VERSION,
        "schemas": tools.schema_location(),
        "validator_seconds": VALIDATOR_SECONDS,
    }


def read_result(out):
    """The child's verdict, checked before anything downstream trusts it. A grader that
    could not read this sitting's brief is infrastructure, never a wrong answer."""
    result = _read_json(out, MAX_RESULT_BYTES, "the grader")
    if not isinstance(result, dict) or not isinstance(result.get("ok"), bool):
        raise Rejected("the grader did not say whether the manifest passed")
    if result.get("broken"):
        raise Rejected(
            f"this task's grader could not read this sitting's requirements "
            f"({result['broken']}). Your work is saved and no attempt was spent; run "
            "`drillion doctor`."
        )
    diagnostics = [
        {
            "path": d.get("path"),
            "message": str(d.get("message", "")),
            **({"file": str(d["file"])} if d.get("file") else {}),
            **({"line": d["line"]} if isinstance(d.get("line"), int) else {}),
        }
        for d in result.get("diagnostics", [])
        if isinstance(d, dict)
    ]
    return (
        result["ok"],
        diagnostics,
        str(result.get("report", "")),
        str(result.get("rendered") or ""),
    )


def _fingerprint(prefix, parts):
    """`prefix` and 12 hex of the parts' hash, each part ended by a NUL so none can shift
    into the next. Stored with every pass, so the bytes hashed must never change."""
    h = hashlib.sha256()
    for part in parts:
        h.update(part.encode())
        h.update(b"\0")
    return prefix + h.hexdigest()[:12]


def docker_fingerprint(meta):
    """What decided a Dockerfile verdict: the grader, hadolint and drillion's config for it."""
    pin = tools.pin_for(tools.HADOLINT)
    return _fingerprint(
        "d1:",
        (
            grader_revision(meta),
            pin.version,
            pin.binary_sha256,
            json.dumps(HADOLINT_CONFIG, sort_keys=True),
        ),
    )


def fingerprint(meta, helm=False):
    """What decided this verdict: the grader, the validator and the schemas alike.

    The etag says what the learner wrote. This says what judged it, which is why the
    validator version and the schema digest are in here and not only `grade.py`. A Helm
    verdict is Helm's too, under its own prefix so no manifest fingerprint moves."""
    pin = tools.pin_for(tools.KUBECONFORM)
    parts = [
        grader_revision(meta),
        pin.version,
        pin.binary_sha256,
        tools.KUBERNETES_VERSION,
        tools.schema_digest(),
    ]
    if helm:
        chart = tools.pin_for(tools.HELM)
        parts += [chart.version, chart.binary_sha256]
    return _fingerprint("h1:" if helm else "m1:", parts)
