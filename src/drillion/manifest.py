"""Grading a manifest: the brief a sitting is graded against, and how it is produced.

`grade.py` is task-authored Python. It is loaded and run only inside the sandboxed child
that `sandbox.run_script` starts, and it talks back in JSON. The server never imports it."""

import hashlib
import json
import math
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path

import yaml

from . import sandbox, tools
from .settings import settings

MAX_BRIEF_BYTES = 8192
MAX_SPEC_CHARS = 65536
SCALARS = (str, int, float, bool)
BRIEF_SECONDS = 30

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
    has moved the question underneath it. Both files it takes to make one are hashed, each
    by its own digest so nothing shifts between them."""
    digest = hashlib.sha256()
    for name in ("grade.py", "solution.yaml"):
        digest.update(hashlib.sha256((meta["dir"] / name).read_bytes()).digest())
    return digest.hexdigest()[:12]


def module_name(slug):
    """A unique module name per task, so two graders cannot share state in selfcheck."""
    return f"drillion_grade_{slug}"


def generate_brief(meta, seed):
    """The requirements for one sitting, produced by the task's own code, in the sandbox.

    The child shares its `sys.argv`, so the grader can write the output file itself instead
    of returning from `brief()`. What comes back is validated either way."""
    grader = meta["dir"] / "grade.py"
    with tempfile.TemporaryDirectory(
        dir=settings.root, ignore_cleanup_errors=True
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
    """Read back what the child wrote, as the one file object the size check looked at.

    The child owns the scratch directory, so it can unlink `out` and leave a symlink or a
    fifo in its place. `O_NOFOLLOW` keeps the parent from becoming a confused deputy for a
    file the sandbox denies the child, `O_NONBLOCK` keeps a fifo from wedging this thread,
    and `fstat` measures the fd rather than the name, so nothing can be swapped in between."""
    try:
        fd = os.open(out, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError:
        raise Rejected("brief() wrote nothing") from None
    with open(fd, encoding="utf-8") as stream:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise Rejected("brief() wrote something that is not a plain file")
        if info.st_size > MAX_BRIEF_BYTES:
            raise Rejected("brief() wrote too much")
        try:
            return _validated(json.loads(stream.read()))
        except ValueError as exc:
            raise Rejected(f"brief() is not valid JSON: {exc}") from None


def render(template, brief):
    """Plain-text substitution for a README. Doubled braces stay literal, as in str.format.

    Every way a placeholder can go wrong is a task-authoring bug, so they all come back as
    `Rejected`: a missing name, a malformed spec, and the attribute and index traversal that
    `{name.title}` and `{replicas[0]}` ask for. The length bound is here because a width like
    `{name:>1000000000}` allocates in the one process that has no `RLIMIT_AS`."""
    try:
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


def render_solution(meta, brief):
    """Render this sitting's reference with each placeholder as a typed YAML scalar."""
    template = (meta["dir"] / "solution.yaml").read_text(encoding="utf-8")
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


# Written into a scratch dir and collected by pytest like any other test, so a manifest
# verdict comes out of the same sandboxed runner as a python one. Every literal brace in
# the generated code is doubled: the template goes through `str.format`.
_HARNESS = '''
import importlib.util, json, subprocess, sys
from pathlib import Path

import yaml

BRIEF = json.loads({brief!r})


def _shape(text, many):
    """What the learner wrote, or the reason it is not yet a manifest. These come before
    the validator because kubeconform has nothing useful to say about any of them. A task
    whose grader defines `check_many` asks for several objects in one file, `---`-separated,
    and then every document has to be a mapping."""
    if not text.strip():
        raise AssertionError("task.yaml is empty: write the manifest before submitting")
    docs = list(yaml.safe_load_all(text))
    if many:
        for i, d in enumerate(docs, 1):
            if not isinstance(d, dict):
                raise AssertionError(f"document {{i}} is not a mapping")
    elif len(docs) != 1:
        raise AssertionError(f"expected one document, found {{len(docs)}}")
    elif not isinstance(docs[0], dict):
        raise AssertionError("the document must be a mapping, not a list or a scalar")
    return docs


def _no_detail(entry):
    """A rejected resource with no per-field errors: the validator stopped before it could
    compare anything. "could not find schema" is the one of those that is as easily a gap
    in what drillion packages as a typo, and from here the two are the same string."""
    msg = entry.get("msg", "invalid")
    if "could not find schema" in msg:
        return (
            f"task.yaml: {{msg}}. Check the spelling of `kind:` and `apiVersion:`; if they "
            "are right then drillion packages no schema for that kind, which is ours to "
            "fix and not your mistake"
        )
    return f"task.yaml: {{msg}}"


def _readable(out):
    """kubeconform's verdict in the learner's words. A run that printed no report at all
    failed to start rather than failed to validate, so its own output is what is shown.

    `msg` is boilerplate naming the schema's install path; the field that is actually wrong
    is in `validationErrors`, so that is what is read when the validator got that far."""
    try:
        report = json.loads(out.stdout)
    except ValueError:
        return (out.stderr or out.stdout).strip()[-1000:]
    lines = []
    for entry in report.get("resources", []):
        if entry.get("status") in ("statusValid", "statusSkipped"):
            continue
        found = entry.get("validationErrors") or []
        lines += [
            f"{{bad.get('path', 'task.yaml')}}: {{bad.get('msg', 'invalid')}}"
            for bad in found
        ]
        if not found:
            lines.append(_no_detail(entry))
    return "\\n".join(lines) or "the manifest is not valid against the schema"


def test_manifest():
    text = Path({learner!r}).read_text(encoding="utf-8")
    spec = importlib.util.spec_from_file_location({module!r}, {grader!r})
    grade = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(grade)
    many = hasattr(grade, "check_many")
    docs = _shape(text, many)
    out = subprocess.run(
        [{tool!r}, "-strict", "-kubernetes-version", {kube!r},
         "-schema-location", {schemas!r}, "-output", "json", {learner!r}],
        capture_output=True, text=True, timeout=30,
    )
    assert out.returncode == 0, _readable(out)
    if many:
        grade.check_many(docs, BRIEF)
    else:
        grade.check(docs[0], BRIEF)
'''


def harness(meta, brief, learner=None):
    """The generated test for one manifest sitting. Never regenerates the brief: the
    requirements were written down when the sitting opened, and they are passed in.

    `learner` is the file to grade, and defaults to the learner's own. A self-check grades
    the answer key instead, and passes the path it rendered it to."""
    tool = tools.installed(tools.KUBECONFORM)
    if tool is None:
        raise ToolMissing("kubeconform is not installed: run `drillion doctor --fetch`")
    return _HARNESS.format(
        brief=json.dumps(brief),
        learner=str(learner or meta["path"]),
        tool=str(tool),
        kube=tools.KUBERNETES_VERSION,
        schemas=tools.schema_location(),
        module=module_name(meta["dir"].name),
        grader=str(meta["dir"] / "grade.py"),
    )


def fingerprint(meta):
    """What decided this verdict: the grader, the validator and the schemas alike.

    The etag says what the learner wrote. This says what judged it, which is why the
    validator version and the schema digest are in here and not only `grade.py`."""
    pin = tools.pin_for(tools.KUBECONFORM)
    h = hashlib.sha256()
    for part in (
        grader_revision(meta),
        pin.version,
        pin.binary_sha256,
        tools.KUBERNETES_VERSION,
        tools.schema_digest(),
    ):
        h.update(part.encode())
        h.update(b"\0")
    return "m1:" + h.hexdigest()[:12]
