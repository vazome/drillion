"""The grading child for every kind but python: a manifest, a Helm chart or a Dockerfile.

`runner.run_manifest` copies this file into the sandbox's scratch directory and runs it with
two paths: the job to do, and the file to answer in. Everything it needs arrives as JSON,
since a kernel tier may deny reading the drillion package; `drillion.guard` is the one
import it tries, and on such a tier it goes without."""

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

import yaml

# what Helm rendered for the run being judged, so every answer can show it
CURRENT = {"rendered": ""}


def answer(ok, diagnostics=(), report="", broken=None) -> NoReturn:
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
    """What the learner wrote, or the reason it is not yet a manifest. These come before
    the validator because kubeconform has nothing useful to say about any of them. A task
    whose grader defines `check_many` asks for several objects in one file, `---`-separated,
    and then every document has to be a mapping."""
    if not text.strip():
        answer(
            False, [(None, "task.yaml is empty: write the manifest before submitting")]
        )
    try:
        docs = list(yaml.safe_load_all(text))
    except yaml.YAMLError as exc:
        answer(False, [(None, f"task.yaml is not valid YAML: {exc}")])
    # Kubernetes reads `field: null` as a field left out, so the grader sees it that way too
    docs = [unset(doc) for doc in docs]
    if many:
        for i, doc in enumerate(docs, 1):
            if not isinstance(doc, dict):
                answer(False, [(None, f"document {i} is not a mapping")])
    elif len(docs) != 1:
        answer(False, [(None, f"expected one document, found {len(docs)}")])
    elif not isinstance(docs[0], dict):
        answer(
            False, [(None, "the document must be a mapping, not a list or a scalar")]
        )
    return docs


def no_detail(entry):
    """A rejected resource with no per-field errors: the validator stopped before it could
    compare anything. "could not find schema" is the one of those that is as easily a gap
    in what drillion packages as a typo, and from here the two are the same string."""
    msg = entry.get("msg", "invalid")
    if "could not find schema" in msg:
        return (
            msg
            + ". Check the spelling of `kind:` and `apiVersion:`; if they are right "
            "then drillion packages no schema for that kind, which is ours to fix and not "
            "your mistake"
        )
    return msg


def validate(learner, where=""):
    """kubeconform's verdict as diagnostics. A run that printed no report at all failed to
    start rather than failed to validate, so its own output is what is shown.

    `msg` is boilerplate naming the schema's install path; the field that is actually wrong
    is in `validationErrors`, so that is what is read when the validator got that far."""
    try:
        done = subprocess.run(
            [
                job["tool"],
                "-strict",
                "-kubernetes-version",
                job["kubernetes"],
                "-schema-location",
                job["schemas"],
                "-output",
                "json",
                learner,
            ],
            capture_output=True,
            check=False,
            text=True,
            timeout=job["validator_seconds"],
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        # the validator is drillion's to install and run; a learner cannot cause this
        answer(False, broken=f"the validator did not run: {exc}")
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
        found += [
            (bad.get("path"), where + bad.get("msg", "invalid")) for bad in errors
        ]
        if not errors:
            found.append((None, where + no_detail(entry)))
    answer(
        False, found or [(None, "the manifest is not valid against the schema")], raw
    )


def helm(*args):
    try:
        return subprocess.run(
            [job["helm"]["tool"], *args],
            capture_output=True,
            check=False,
            text=True,
            timeout=job["validator_seconds"],
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        answer(False, broken=f"helm did not run: {exc}")


def helm_said(where, text):
    """One of Helm's messages as a diagnostic: its `Error: ` and --debug advice dropped,
    the chart's name taken off each path so `web/templates/x.yaml:4` reads as the file the
    learner sees, and the file it names kept so the page can point at that tab."""
    h = job["helm"]
    kept = [
        ln
        for ln in text.splitlines()
        if ln.strip()
        and ln.strip() != h["name"] + ":"
        and not ln.startswith(("Use --debug flag", "level="))
    ]
    message = "\n".join(kept).strip().removeprefix("Error: ")
    message = message.replace(h["name"] + "/", "")
    named = [f for f in sorted(h["files"], key=len, reverse=True) if f in message]
    if not named and "specifications of the schema" in message:
        named = ["values.yaml"]  # the schema judges values, whichever file set them
    if not named:
        return (None, where + message)
    # `templates/x.yaml:17`, or a YAML parser's `line 4` about the learner's own values
    found = re.search(re.escape(named[0]) + r":(\d+)", message)
    if found is None and named[0] == h["edits"] == "values.yaml":
        found = re.search(r"\bline (\d+)", message)
    return (None, where + message, named[0], int(found.group(1)) if found else None)


def lint_said(text):
    """`helm lint` has no JSON: its ERROR and WARNING entries, each with the lines that
    continue it. INFO (`icon is recommended`) is advice about the chart, never a verdict."""
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
    """The values Helm renders with: `given` over the chart's own, maps merged key by key
    and a null deleting the default, as `helm template -f` does it."""
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
    """A Helm sitting: the chart with the learner's file in its hole, rendered once per
    `renders(brief)` entry and judged whole each time. A template that only works for one
    set of values fails the render that uses the other."""
    h, brief = job["helm"], job["brief"]
    text = Path(job["learner"]).read_text(encoding="utf-8")
    if not text.strip():
        answer(
            False,
            [
                (
                    None,
                    "{} is empty: write it before submitting".format(h["edits"]),
                    h["edits"],
                )
            ],
        )
    chart = Path("chart")
    shutil.copytree(h["chart"], chart)
    target = chart / h["edits"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    renders = (
        grade.renders(brief)
        if hasattr(grade, "renders")
        else [{"release": brief.get("release", "demo"), "values": None}]
    )
    report, shown = "", None
    for i, r in enumerate(renders):
        where = ""
        if len(renders) > 1:
            given = json.dumps(r["values"], sort_keys=True)
            given = given if len(given) <= 160 else given[:157] + "..."
            where = (
                f"render {i + 1} of {len(renders)} "
                f"(release `{r['release']}`, values {given}): "
            )
        given = []
        if r["values"] is not None:
            given = ["-f", f"values-{i}.json"]
            Path(given[1]).write_text(json.dumps(r["values"]), encoding="utf-8")
        kube = ["--kube-version", job["kubernetes"]]
        done = helm("template", r["release"], str(chart), *kube, *given)
        # a render the task wants refused passes only when Helm stops, saying why
        refuses = r.get("refuses")
        if refuses is not None:
            said = done.stderr + done.stdout
            if not done.returncode:
                answer(
                    False,
                    [
                        (
                            None,
                            where + "these values rendered, and the chart "
                            f"should refuse them with a message saying {refuses!r}",
                        )
                    ],
                )
            if refuses not in said:
                answer(
                    False,
                    [
                        helm_said(
                            where,
                            "Helm refused these values, but its message "
                            f"does not say {refuses!r}: {said}",
                        )
                    ],
                    said,
                )
            continue
        if done.returncode:
            answer(False, [helm_said(where, done.stderr or done.stdout)], done.stderr)
        CURRENT["rendered"] = done.stdout
        linted = helm("lint", str(chart), "--strict", *kube, *given)
        if linted.returncode:
            raw = linted.stdout + linted.stderr
            said = lint_said(raw) or [raw.strip()]
            answer(False, [helm_said(where, m) for m in said], raw)
        rendered = Path(f"rendered-{i}.yaml")
        rendered.write_text(done.stdout, encoding="utf-8")
        docs = [d for d in yaml.safe_load_all(done.stdout) if d is not None]
        if docs:
            report = validate(str(rendered), where)
        # read only now: Helm has accepted the file, so a broken one never gets this far
        own = chart / "values.yaml"
        defaults = (
            yaml.safe_load(own.read_text(encoding="utf-8")) if own.is_file() else {}
        )
        defaults = defaults or {}
        values = defaults if r["values"] is None else merged(defaults, r["values"])
        try:
            grade.check(docs, brief, {"release": r["release"], "values": values})
        except AssertionError as exc:
            answer(False, [(None, where + str(exc))], report)
        except Exception as exc:
            answer(False, report=report, broken=f"{type(exc).__name__}: {exc}")
        shown = shown if shown is not None else done.stdout
    CURRENT["rendered"] = shown or ""
    answer(True, report=report)


HEREDOC = re.compile(r"<<(-?)([\"']?)(\w+)\2")


def dockerfile_steps(text):
    """The Dockerfile as the builder reads it: one entry per instruction, its continuation
    lines joined and the comments among them dropped, a heredoc's body kept with it."""
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        start, line = i + 1, lines[i]
        i += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        while line.rstrip().endswith("\\") and i < len(lines):
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
                if (body.lstrip("\t") if dash else body) == end:
                    break
                line += "\n" + body
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
        out.append(
            {
                "cmd": cmd.upper(),
                "args": rest,
                "flags": flags,
                "exec": form,
                "words": form if form is not None else rest.split(),
                "line": start,
            }
        )
    return out


class Stage(dict):
    """One build stage as `check()` receives it: `{"base", "name", "line", "globals",
    "steps"}`, and `all` to pick out one instruction's steps."""

    def all(self, cmd):
        """Every step of this stage that is a `cmd` instruction, in file order."""
        return [s for s in self["steps"] if s["cmd"] == cmd]


def dockerfile_stages(steps):
    """The build stages, each FROM and the steps under it. The ARGs above the first FROM
    belong to no stage, so every stage carries them as `globals`."""
    out, globals_ = [], []
    for step in steps:
        if step["cmd"] == "FROM":
            w = step["words"]
            out.append(
                Stage(
                    base=w[0] if w else "",
                    name=w[2] if len(w) > 2 and w[1].lower() == "as" else None,
                    line=step["line"],
                    globals=globals_,
                    steps=[],
                )
            )
        elif out:
            out[-1]["steps"].append(step)
        else:
            globals_.append(step)
    return out


def context_misses(stages, context):
    """Every COPY or ADD source that is not in the build context: the one way a Dockerfile
    fails to build that can be seen without building it."""
    held = sorted(
        p.relative_to(context).as_posix() for p in context.rglob("*") if p.is_file()
    )
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
                    found.append(
                        (
                            None,
                            f"line {step['line']}: {step['cmd']} copies `{src}`, and the build "
                            f"context has no such file. It holds "
                            + ", ".join(f"`{h}`" for h in held),
                            "Dockerfile",
                            step["line"],
                        )
                    )
    return found


def grade_docker(grade):
    """A Dockerfile sitting: hadolint first, then every COPY source against the build
    context, then the task's `check()` over the parsed stages. Nothing is built."""
    d, brief = job["docker"], job["brief"]
    text = Path(job["learner"]).read_text(encoding="utf-8")
    if not text.strip():
        answer(
            False,
            [(None, "Dockerfile is empty: write it before submitting", "Dockerfile")],
        )
    Path("Dockerfile").write_text(text, encoding="utf-8")
    Path("hadolint.yaml").write_text(json.dumps(d["config"]), encoding="utf-8")
    try:
        done = subprocess.run(
            [
                d["tool"],
                "--no-color",
                "--disable-ignore-pragma",
                "-c",
                "hadolint.yaml",
                "-f",
                "json",
                "Dockerfile",
            ],
            capture_output=True,
            check=False,
            text=True,
            timeout=job["validator_seconds"],
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        answer(False, broken=f"hadolint did not run: {exc}")
    try:
        found = json.loads(done.stdout)
    except ValueError:
        answer(False, broken=f"hadolint did not run: {done.stderr.strip()[-500:]}")
    report = "\n".join(
        f"Dockerfile:{f['line']} {f['code']} {f['level']}: {f['message']}"
        for f in found
    )
    failing = [f for f in found if f["level"] in ("error", "warning")]
    if failing:
        answer(
            False,
            [
                (
                    None,
                    f"line {f['line']}: {f['message']} ({f['code']})",
                    "Dockerfile",
                    f["line"],
                )
                for f in failing
            ],
            report,
        )
    stages = dockerfile_stages(dockerfile_steps(text))
    missing = context_misses(stages, Path(d["context"]))
    if missing:
        answer(False, missing, report)
    try:
        grade.check(stages, brief)
    except AssertionError as exc:
        answer(False, [(None, str(exc))], report)
    except Exception as exc:
        answer(False, report=report, broken=f"{type(exc).__name__}: {exc}")
    answer(True, report=report)


def grade_manifest(grade):
    """A manifest sitting: the shape of the file, kubeconform, then the task's `check()`,
    or `check_many` for a task that asks for several objects in one file."""
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
        # past the schema, anything but an assert is the grader failing to read this
        # sitting's brief: ours to fix, and it must not cost the learner an attempt
        answer(False, report=report, broken=f"{type(exc).__name__}: {exc}")
    answer(True, report=report)


GRADERS = {"helm": grade_helm, "docker": grade_docker}


if __name__ == "__main__":
    # before any task code, because on the guard tier its audit hook is all there is
    try:
        import drillion.guard  # noqa: F401
    except ImportError, OSError:
        pass

    job = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])
    spec = importlib.util.spec_from_file_location(job["module"], job["grader"])
    assert spec is not None and spec.loader is not None
    grade = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(grade)
    GRADERS.get(job["kind"], grade_manifest)(grade)
