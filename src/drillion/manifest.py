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
from .catalogue import DOCKER, solution
from .settings import settings

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


# Run by `sandbox.run_script` with two paths: the job to do, and the file to answer in.
# It is a plain string, never a template: everything it needs arrives as JSON, so a task's
# own braces are nothing to escape.
GRADE_SOURCE = """
try:
    import drillion.guard
except (ImportError, OSError):
    pass

import importlib.util, json, re, shutil, subprocess, sys
from pathlib import Path

import yaml

job = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
out = Path(sys.argv[2])
# what Helm rendered for the run being judged, so every answer can show it
CURRENT = {"rendered": ""}


def answer(ok, diagnostics=(), report="", broken=None):
    out.write_text(
        json.dumps(
            {
                "ok": ok,
                "diagnostics": [
                    {
                        "path": d[0],
                        "message": d[1],
                        "file": d[2] if len(d) > 2 else None,
                        "line": d[3] if len(d) > 3 else None,
                    }
                    for d in diagnostics
                ],
                "report": report[-4000:],
                "rendered": CURRENT["rendered"][-16000:],
                "broken": broken,
            }
        ),
        encoding="utf-8",
    )
    sys.exit(0)


def unset(node):
    if isinstance(node, dict):
        return {k: unset(v) for k, v in node.items() if v is not None}
    if isinstance(node, list):
        return [unset(v) for v in node]
    return node


def shape(text, many):
    '''What the learner wrote, or the reason it is not yet a manifest. These come before
    the validator because kubeconform has nothing useful to say about any of them. A task
    whose grader defines `check_many` asks for several objects in one file, `---`-separated,
    and then every document has to be a mapping.'''
    if not text.strip():
        answer(False, [(None, "task.yaml is empty: write the manifest before submitting")])
    try:
        docs = list(yaml.safe_load_all(text))
    except yaml.YAMLError as exc:
        answer(False, [(None, "task.yaml is not valid YAML: %s" % exc)])
    # Kubernetes reads `field: null` as a field left out, so the grader sees it that way too
    docs = [unset(doc) for doc in docs]
    if many:
        for i, doc in enumerate(docs, 1):
            if not isinstance(doc, dict):
                answer(False, [(None, "document %d is not a mapping" % i)])
    elif len(docs) != 1:
        answer(False, [(None, "expected one document, found %d" % len(docs))])
    elif not isinstance(docs[0], dict):
        answer(False, [(None, "the document must be a mapping, not a list or a scalar")])
    return docs


def no_detail(entry):
    '''A rejected resource with no per-field errors: the validator stopped before it could
    compare anything. "could not find schema" is the one of those that is as easily a gap
    in what drillion packages as a typo, and from here the two are the same string.'''
    msg = entry.get("msg", "invalid")
    if "could not find schema" in msg:
        return (
            msg + ". Check the spelling of `kind:` and `apiVersion:`; if they are right "
            "then drillion packages no schema for that kind, which is ours to fix and not "
            "your mistake"
        )
    return msg


def validate(learner, where=""):
    '''kubeconform's verdict as diagnostics. A run that printed no report at all failed to
    start rather than failed to validate, so its own output is what is shown.

    `msg` is boilerplate naming the schema's install path; the field that is actually wrong
    is in `validationErrors`, so that is what is read when the validator got that far.'''
    try:
        done = subprocess.run(
            [job["tool"], "-strict", "-kubernetes-version", job["kubernetes"],
             "-schema-location", job["schemas"], "-output", "json", learner],
            capture_output=True, text=True, timeout=job["validator_seconds"],
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        # the validator is drillion's to install and run; a learner cannot cause this
        answer(False, broken="the validator did not run: %s" % exc)
    raw = done.stdout + done.stderr
    if done.returncode == 0:
        return raw
    try:
        report = json.loads(done.stdout)
    except ValueError:
        answer(False, [(None, (done.stderr or done.stdout).strip()[-1000:])], raw)
    found = []
    for entry in report.get("resources", []):
        if entry.get("status") in ("statusValid", "statusSkipped"):
            continue
        errors = entry.get("validationErrors") or []
        found += [(bad.get("path"), where + bad.get("msg", "invalid")) for bad in errors]
        if not errors:
            found.append((None, where + no_detail(entry)))
    answer(False, found or [(None, "the manifest is not valid against the schema")], raw)


def helm(*args):
    try:
        return subprocess.run(
            [job["helm"]["tool"], *args], capture_output=True, text=True,
            timeout=job["validator_seconds"],
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        answer(False, broken="helm did not run: %s" % exc)


def helm_said(where, text):
    '''One of Helm's messages as a diagnostic: its `Error: ` and --debug advice dropped,
    the chart's name taken off each path so `web/templates/x.yaml:4` reads as the file the
    learner sees, and the file it names kept so the page can point at that tab.'''
    h = job["helm"]
    kept = [
        ln for ln in text.splitlines()
        if ln.strip() and ln.strip() != h["name"] + ":"
        and not ln.startswith(("Use --debug flag", "level="))
    ]
    message = "\\n".join(kept).strip().removeprefix("Error: ")
    message = message.replace(h["name"] + "/", "")
    named = [f for f in sorted(h["files"], key=len, reverse=True) if f in message]
    if not named and "specifications of the schema" in message:
        named = ["values.yaml"]  # the schema judges values, whichever file set them
    if not named:
        return (None, where + message)
    # `templates/x.yaml:17`, or a YAML parser's `line 4` about the learner's own values
    found = re.search(re.escape(named[0]) + r":(\\d+)", message)
    if found is None and named[0] == h["edits"] == "values.yaml":
        found = re.search(r"\\bline (\\d+)", message)
    return (None, where + message, named[0], int(found.group(1)) if found else None)


def lint_said(text):
    '''`helm lint` has no JSON: its ERROR and WARNING entries, each with the lines that
    continue it. INFO (`icon is recommended`) is advice about the chart, never a verdict.'''
    found, entry = [], None
    for ln in text.splitlines():
        if ln.startswith(("[ERROR] ", "[WARNING] ")):
            entry = [ln.split("] ", 1)[1]]
            found.append(entry)
        elif ln.startswith(("[INFO]", "==>", "level=", "Error: ")) or not ln.strip():
            entry = None
        elif entry is not None and "chart(s) linted" not in ln:
            entry.append(ln.strip())
    return [" ".join(e) for e in found]


def merged(defaults, given):
    '''The values Helm renders with: `given` over the chart's own, maps merged key by key
    and a null deleting the default, as `helm template -f` does it.'''
    out = dict(defaults)
    for key, value in given.items():
        if value is None:
            out.pop(key, None)
        elif isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = merged(out[key], value)
        else:
            out[key] = value
    return out


def grade_helm(grade):
    '''A Helm sitting: the chart with the learner's file in its hole, rendered once per
    `renders(brief)` entry and judged whole each time. A template that only works for one
    set of values fails the render that uses the other.'''
    h, brief = job["helm"], job["brief"]
    text = Path(job["learner"]).read_text(encoding="utf-8")
    if not text.strip():
        answer(False, [(None, "%s is empty: write it before submitting" % h["edits"], h["edits"])])
    chart = Path("chart")
    shutil.copytree(h["chart"], chart)
    target = chart / h["edits"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    renders = (
        grade.renders(brief) if hasattr(grade, "renders")
        else [{"release": brief.get("release", "demo"), "values": None}]
    )
    report, shown = "", None
    for i, r in enumerate(renders):
        where = ""
        if len(renders) > 1:
            given = json.dumps(r["values"], sort_keys=True)
            given = given if len(given) <= 160 else given[:157] + "..."
            where = "render %d of %d (release `%s`, values %s): " % (
                i + 1, len(renders), r["release"], given
            )
        given = []
        if r["values"] is not None:
            given = ["-f", "values-%d.json" % i]
            Path(given[1]).write_text(json.dumps(r["values"]), encoding="utf-8")
        kube = ["--kube-version", job["kubernetes"]]
        done = helm("template", r["release"], str(chart), *kube, *given)
        if done.returncode:
            answer(False, [helm_said(where, done.stderr or done.stdout)], done.stderr)
        CURRENT["rendered"] = done.stdout
        linted = helm("lint", str(chart), "--strict", *kube, *given)
        if linted.returncode:
            raw = linted.stdout + linted.stderr
            said = lint_said(raw) or [raw.strip()]
            answer(False, [helm_said(where, m) for m in said], raw)
        rendered = Path("rendered-%d.yaml" % i)
        rendered.write_text(done.stdout, encoding="utf-8")
        docs = [d for d in yaml.safe_load_all(done.stdout) if d is not None]
        if docs:
            report = validate(str(rendered), where)
        # read only now: Helm has accepted the file, so a broken one never gets this far
        own = chart / "values.yaml"
        defaults = yaml.safe_load(own.read_text(encoding="utf-8")) if own.is_file() else {}
        defaults = defaults or {}
        values = defaults if r["values"] is None else merged(defaults, r["values"])
        try:
            grade.check(docs, brief, {"release": r["release"], "values": values})
        except AssertionError as exc:
            answer(False, [(None, where + str(exc))], report)
        except Exception as exc:
            answer(False, report=report, broken="%s: %s" % (type(exc).__name__, exc))
        shown = shown if shown is not None else done.stdout
    CURRENT["rendered"] = shown or ""
    answer(True, report=report)


HEREDOC = re.compile(r"<<(-?)([\\"']?)(\\w+)\\2")


def dockerfile_steps(text):
    '''The Dockerfile as the builder reads it: one entry per instruction, its continuation
    lines joined and the comments among them dropped, a heredoc's body kept with it.'''
    lines, out, i = text.split("\\n"), [], 0
    while i < len(lines):
        start, line = i + 1, lines[i]
        i += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        while line.rstrip().endswith("\\\\") and i < len(lines):
            line = line.rstrip()[:-1]
            while i < len(lines) and lines[i].lstrip().startswith("#"):
                i += 1
            if i < len(lines):
                line += lines[i]
                i += 1
        for dash, _, end in HEREDOC.findall(line):
            while i < len(lines):
                body = lines[i]
                i += 1
                if (body.lstrip("\\t") if dash else body) == end:
                    break
                line += "\\n" + body
        cmd, _, rest = line.strip().partition(" ")
        rest, flags = rest.strip(), {}
        while rest.startswith("--"):
            flag, _, rest = rest.partition(" ")
            name, _, value = flag[2:].partition("=")
            flags[name] = value or True
            rest = rest.strip()
        try:
            form = json.loads(rest) if rest.startswith("[") else None
        except ValueError:
            form = None
        if not (isinstance(form, list) and all(isinstance(w, str) for w in form)):
            form = None
        out.append({
            "cmd": cmd.upper(), "args": rest, "flags": flags, "exec": form,
            "words": form if form is not None else rest.split(), "line": start,
        })
    return out


def dockerfile_stages(steps):
    '''The build stages, each FROM and the steps under it. The ARGs above the first FROM
    belong to no stage, so every stage carries them as `globals`.'''
    out, globals_ = [], []
    for step in steps:
        if step["cmd"] == "FROM":
            w = step["words"]
            out.append({
                "base": w[0] if w else "",
                "name": w[2] if len(w) > 2 and w[1].lower() == "as" else None,
                "line": step["line"],
                "globals": globals_,
                "steps": [],
            })
        elif out:
            out[-1]["steps"].append(step)
        else:
            globals_.append(step)
    return out


def context_misses(stages, context):
    '''Every COPY or ADD source that is not in the build context: the one way a Dockerfile
    fails to build that can be seen without building it.'''
    held = sorted(p.relative_to(context).as_posix() for p in context.rglob("*") if p.is_file())
    found = []
    for stage in stages:
        for step in stage["steps"]:
            if step["cmd"] not in ("COPY", "ADD") or "from" in step["flags"]:
                continue
            if "<<" in step["args"]:
                continue
            for src in step["words"][:-1]:
                pattern = src.strip("/").removeprefix("./")
                if "://" in src or pattern in ("", "."):
                    continue
                if ".." in Path(pattern).parts or not list(context.glob(pattern)):
                    found.append((
                        None,
                        "line %d: %s copies `%s`, and the build context has no such file. "
                        "It holds %s" % (
                            step["line"], step["cmd"], src,
                            ", ".join("`%s`" % h for h in held),
                        ),
                        "Dockerfile",
                        step["line"],
                    ))
    return found


def grade_docker(grade):
    '''A Dockerfile sitting: hadolint first, then every COPY source against the build
    context, then the task's `check()` over the parsed stages. Nothing is built.'''
    d, brief = job["docker"], job["brief"]
    text = Path(job["learner"]).read_text(encoding="utf-8")
    if not text.strip():
        answer(False, [(None, "Dockerfile is empty: write it before submitting", "Dockerfile")])
    Path("Dockerfile").write_text(text, encoding="utf-8")
    Path("hadolint.yaml").write_text(json.dumps(d["config"]), encoding="utf-8")
    try:
        done = subprocess.run(
            [d["tool"], "--no-color", "--disable-ignore-pragma", "-c", "hadolint.yaml",
             "-f", "json", "Dockerfile"],
            capture_output=True, text=True, timeout=job["validator_seconds"],
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        answer(False, broken="hadolint did not run: %s" % exc)
    try:
        found = json.loads(done.stdout)
    except ValueError:
        answer(False, broken="hadolint did not run: %s" % done.stderr.strip()[-500:])
    report = "\\n".join(
        "Dockerfile:%d %s %s: %s" % (f["line"], f["code"], f["level"], f["message"])
        for f in found
    )
    failing = [f for f in found if f["level"] in ("error", "warning")]
    if failing:
        answer(False, [
            (None, "line %d: %s (%s)" % (f["line"], f["message"], f["code"]), "Dockerfile", f["line"])
            for f in failing
        ], report)
    stages = dockerfile_stages(dockerfile_steps(text))
    missing = context_misses(stages, Path(d["context"]))
    if missing:
        answer(False, missing, report)
    try:
        grade.check(stages, brief)
    except AssertionError as exc:
        answer(False, [(None, str(exc))], report)
    except Exception as exc:
        answer(False, report=report, broken="%s: %s" % (type(exc).__name__, exc))
    answer(True, report=report)


spec = importlib.util.spec_from_file_location(job["module"], job["grader"])
grade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grade)
if job.get("docker"):
    grade_docker(grade)
if job.get("helm"):
    grade_helm(grade)
many = hasattr(grade, "check_many")
docs = shape(Path(job["learner"]).read_text(encoding="utf-8"), many)
report = validate(job["learner"])
try:
    if many:
        grade.check_many(docs, job["brief"])
    else:
        grade.check(docs[0], job["brief"])
except AssertionError as exc:
    answer(False, [(None, str(exc))], report)
except Exception as exc:
    # past the schema, anything but an assert is the grader failing to read this sitting's
    # brief: ours to fix, and it must not cost the learner an attempt
    answer(False, report=report, broken="%s: %s" % (type(exc).__name__, exc))
answer(True, report=report)
"""


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


def docker_fingerprint(meta):
    """What decided a Dockerfile verdict: the grader, hadolint and drillion's config for it."""
    pin = tools.pin_for(tools.HADOLINT)
    h = hashlib.sha256()
    for part in (
        grader_revision(meta),
        pin.version,
        pin.binary_sha256,
        json.dumps(HADOLINT_CONFIG, sort_keys=True),
    ):
        h.update(part.encode())
        h.update(b"\0")
    return "d1:" + h.hexdigest()[:12]


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
    h = hashlib.sha256()
    for part in parts:
        h.update(part.encode())
        h.update(b"\0")
    return ("h1:" if helm else "m1:") + h.hexdigest()[:12]
