"""The grading child for every kind but python: a manifest, a Helm chart, a Dockerfile, SQL
or a git repository.

`runner.run_manifest` copies this file into the sandbox's scratch directory and runs it with
two paths: the job to do, and the file to answer in. Everything it needs arrives as JSON,
since a kernel tier may deny reading the drillion package; `drillion.guard` is the one
import it tries, and on such a tier it goes without."""

import hashlib
import importlib.util
import json
import os
import random
import re
import shutil
import subprocess
import sys
from collections import Counter
from decimal import Decimal
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


NUMBER = re.compile(r"-?\d+(\.\d+)?([eE][-+]?\d+)?")
MAX_SHOWN = 20  # rows a result table shows before it says how many more
HIDDEN = (
    "This matches on the data shown, and returns {what} on a second dataset the grader "
    "keeps hidden. A value copied from the data shown, or a condition that only happens "
    "to fit it?"
)
HIDDEN_WHAT = {
    "none": "no result",
    "columns": "different columns",
    "count": "a different number of rows",
    "row": "different rows",
    "order": "the rows in a different order",
}


def sql_value(text):
    """What a value compares as: a Decimal when Postgres printed a number, its text if not."""
    if text is not None and NUMBER.fullmatch(text):
        return Decimal(text)
    return text


def _shown(row):
    return "(" + ", ".join("NULL" if v is None else v for v in row) + ")"


def differ(expected, got, ordered):
    """(what, message) for the first way `got` is not `expected`, or None when they agree."""
    if got is None:
        return "none", (
            "your SQL returned no rows at all: its last statement has to be a SELECT"
        )
    if got["fields"] != expected["fields"]:
        return "columns", (
            f"columns: expected {', '.join(expected['fields'])}; "
            f"got {', '.join(got['fields'])}"
        )
    if got["count"] != expected["count"]:
        return "count", f"expected {expected['count']} rows, got {got['count']}"
    want = [tuple(map(sql_value, row)) for row in expected["rows"]]
    have = [tuple(map(sql_value, row)) for row in got["rows"]]
    missing = Counter(want) - Counter(have)
    if missing:
        row = expected["rows"][want.index(next(iter(missing)))]
        return "row", f"a row the answer has and yours does not: {_shown(row)}"
    if ordered:
        for n, (w, h) in enumerate(zip(want, have), 1):
            if w != h:
                return "order", (
                    f"row {n}: expected {_shown(expected['rows'][n - 1])}, got "
                    f"{_shown(got['rows'][n - 1])}. The order matters here"
                )
    return None


def probe_differ(want, got):
    """What went differently when a probe ran after the learner's SQL, or None. A probe that
    must fail agrees on its SQLSTATE alone, since its message names what the learner chose."""
    if got is None:
        return "did not run"
    if "error" in want:
        if "error" not in got:
            return (
                f"expected an error with SQLSTATE {want['error']['code']}, "
                "and it succeeded"
            )
        if got["error"]["code"] != want["error"]["code"]:
            return (
                f"expected SQLSTATE {want['error']['code']}, got "
                f"{got['error']['code']}: {got['error']['message']}"
            )
        return None
    if "error" in got:
        return f"failed: {got['error']['message']} (SQLSTATE {got['error']['code']})"
    found = differ(want, got, ordered=False)
    return found and found[1]


def table(result):
    """A result as psql would print it, cut at MAX_SHOWN rows."""
    if result is None:
        return "(no result: the last statement returned no columns)"
    rows = [
        ["NULL" if v is None else v for v in row] for row in result["rows"][:MAX_SHOWN]
    ]
    widths = [
        max([len(f), *(len(row[i]) for row in rows)])
        for i, f in enumerate(result["fields"])
    ]

    def line(cells):
        return " | ".join(c.ljust(w) for c, w in zip(cells, widths)).rstrip()

    more = result["count"] - len(rows)
    tail = f"({result['count']} rows{f', {more} not shown' if more > 0 else ''})"
    return "\n".join(
        [
            line(result["fields"]),
            "-+-".join("-" * w for w in widths),
            *map(line, rows),
            tail,
        ]
    )


def line_of(text, position):
    """Postgres counts an error's position in characters from 1, across the whole script."""
    return text[: position - 1].count("\n") + 1


def _param(value):
    """A row value as sqlrun binds it: JSON for a dict or list, ISO for a date."""
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return value.isoformat() if hasattr(value, "isoformat") else value


def _nodes(plan):
    """Every node type in an EXPLAIN (FORMAT JSON) plan, so a check can ask for WindowAgg."""
    found, stack = set(), [json.loads(plan)[0]["Plan"]] if plan else []
    while stack:
        node = stack.pop()
        found.add(node["Node Type"])
        stack += node.get("Plans", [])
    return found


def _datasets(grade, brief, seed):
    """The rows of the data shown and of the hidden dataset, ready to bind."""
    return [
        {
            table_: [{c: _param(v) for c, v in row.items()} for row in rows]
            for table_, rows in grade.rows(
                random.Random(f"{name}:{seed}"), brief
            ).items()
        }
        for name in ("rows", "hidden")
    ]


def _run_passes(s, passes):
    """sqlrun's four passes, or an answer: a learner's SQL that never finishes or stops
    PGlite is theirs to fix, since `selfcheck` has already shown the key finishes."""
    Path("sqlrun.mjs").write_text(s["runner"], encoding="utf-8")
    Path("sqljob.json").write_text(
        json.dumps({"pglite": s["pglite"], "schema": s["schema"], "passes": passes}),
        encoding="utf-8",
    )
    try:
        subprocess.run(
            [s["node"], *s["flags"], "sqlrun.mjs", "sqljob.json", "sqlout.json"],
            capture_output=True,
            text=True,
            check=False,
            timeout=job["validator_seconds"],
        )
    except subprocess.TimeoutExpired:
        said = (
            f"your SQL did not finish within {job['validator_seconds']}s: look for a "
            "WITH RECURSIVE that never stops, or a join with no condition"
        )
        answer(False, [(None, said, "task.sql")])
    except OSError as exc:
        answer(False, broken=f"PGlite did not run: {exc}")
    try:
        return json.loads(Path("sqlout.json").read_text(encoding="utf-8"))["passes"]
    except OSError, ValueError:
        # Node's own dying words are a V8 stack, and the sandbox's memory cap is the cause
        said = (
            "your SQL stopped PGlite, most likely by running out of memory: look for a "
            "query that returns or builds millions of rows, such as a join with no "
            "condition"
        )
        answer(False, [(None, said, "task.sql")])


def _hidden_rules(s, key, mine):
    """The hidden dataset says only which part differed, never its rows."""
    if e := mine.get("error"):
        # its message can carry hidden rows, through RAISE if nothing else
        said = f"On a second dataset the grader keeps hidden, your SQL fails with SQLSTATE {e['code']}"
        answer(False, [(None, said)])
    if key["result"] is not None and (
        found := differ(key["result"], mine["result"], s["ordered"])
    ):
        answer(False, [(None, HIDDEN.format(what=HIDDEN_WHAT[found[0]]))])
    for name, want in key["probes"].items():
        if probe_differ(want, mine["probes"].get(name)):
            said = (
                f"{name}: right on the data shown, wrong on a second dataset the "
                "grader keeps hidden"
            )
            answer(False, [(None, said)])


def _selfcheck_rules(key, hidden):
    """A query task whose key cannot tell a real answer from a hard-coded one is broken."""
    if key["result"] is None:
        return
    if not key["result"]["count"] or not hidden["result"]["count"]:
        answer(False, [(None, "the answer key returns no rows on one of the datasets")])
    if Counter(map(tuple, key["result"]["rows"])) == Counter(
        map(tuple, hidden["result"]["rows"])
    ):
        said = (
            "the answer key returns the same rows on both datasets, so a hard-coded "
            "answer passes"
        )
        answer(False, [(None, said)])


def grade_sql(grade):
    """A SQL sitting: the answer key, then the learner's SQL, each on the data shown and on
    a hidden second dataset, in one PGlite; then the probes, then the task's `check()`.
    The key's own failures are the task's bug and never the learner's."""
    s, brief = job["sql"], job["brief"]
    text = Path(job["learner"]).read_text(encoding="utf-8")
    if not text.strip():
        answer(
            False,
            [(None, "task.sql is empty: write your SQL before submitting", "task.sql")],
        )
    try:
        datasets = _datasets(grade, brief, s["seed"])
        probes = list(grade.probes(brief).items()) if hasattr(grade, "probes") else []
    except Exception as exc:
        answer(False, broken=f"{type(exc).__name__}: {exc}")
    passes = [
        {
            "rows": rows,
            "sql": sql,
            "probes": probes,
            "explain": s["explain"] and learner,
        }
        for sql, learner in ((s["key"], False), (text, True))
        for rows in datasets
    ]
    key, key_hidden, mine, mine_hidden = _run_passes(s, passes)
    for p in (key, key_hidden):
        if e := p.get("setup") or p.get("error"):
            answer(False, broken=f"the answer key does not run: {e['message']}")
        # a learner's count has to equal the key's, so a key inside the cut keeps theirs whole
        if any(
            r and "rows" in r and r["count"] > len(r["rows"])
            for r in (p["result"], *p["probes"].values())
        ):
            answer(
                False, broken="the answer key returns more than the 1000 rows compared"
            )
    if mine.get("setup"):
        answer(False, broken=f"the database did not load: {mine['setup']['message']}")
    if e := mine["error"]:
        line = line_of(text, e["position"]) if e["position"] else None
        where = f"line {line}: " if line else ""
        answer(
            False,
            [(None, f"{where}{e['message']} (SQLSTATE {e['code']})", "task.sql", line)],
        )
    if mine["result"] is not None:
        CURRENT["rendered"] = table(mine["result"])
    if s["explain"] and mine["result"] is not None and mine["plan"] is None:
        said = (
            "task.sql must hold your query alone for the grader to read its plan: "
            "remove the other statements"
        )
        answer(False, [(None, said, "task.sql")])
    if key["result"] is not None and (
        found := differ(key["result"], mine["result"], s["ordered"])
    ):
        answer(
            False,
            [(None, found[1])],
            f"Expected, on the data shown:\n{table(key['result'])}",
        )
    for name, want in key["probes"].items():
        got = mine["probes"].get(name)
        if said := probe_differ(want, got):
            answer(
                False,
                [(None, f"{name}: {said}")],
                ""
                if "error" in want
                else f"Expected, after the answer key:\n{table(want)}",
            )
    _hidden_rules(s, key_hidden, mine_hidden)
    if s["selfcheck"]:
        _selfcheck_rules(key, key_hidden)
    if hasattr(grade, "check"):
        result = {
            **(mine["result"] or {"fields": [], "rows": [], "count": 0}),
            "probes": mine["probes"],
            "nodes": _nodes(mine["plan"]),
        }
        try:
            grade.check(result, brief)
        except AssertionError as exc:
            answer(False, [(None, str(exc))])
        except Exception as exc:
            answer(False, broken=f"{type(exc).__name__}: {exc}")
    answer(True)


GIT_PROBES = ("operation", "refs", "deleted", "head", "status", "stash")
_REBASING = (
    "a rebase is still in progress: git rebase --continue, or git rebase --abort"
)
IN_PROGRESS = {
    "MERGE_HEAD": "a merge is still in progress: finish it with git commit, or back out with git merge --abort",
    "CHERRY_PICK_HEAD": "a cherry-pick is still in progress: git cherry-pick --continue, or --abort",
    "REVERT_HEAD": "a revert is still in progress: git revert --continue, or --abort",
    "rebase-merge": _REBASING,
    "rebase-apply": _REBASING,
    "BISECT_LOG": "a bisect is still in progress: end it with git bisect reset",
}


def _commits(repo, tips):
    """{sha: (content id, parents, tree, subject)} for every commit reachable from `tips`.
    A content id hashes the subject, the tree and the parents' content ids in order, so the
    same history made on another day, by someone else, has the same ids."""
    out = {}
    if not tips:
        return out
    text = repo.git(
        "log",
        "--topo-order",
        "--reverse",
        "--format=%H%x01%P%x01%T%x01%s%x00",
        *tips,
        "--",
    )
    for record in text.split("\0"):
        record = record.lstrip("\n")
        if not record:
            continue
        sha, parents, tree, subject = record.split("\x01", 3)
        parents = parents.split()
        h = hashlib.sha256(f"{subject}\0{tree}".encode())
        for p in parents:
            h.update(b"\0" + out[p][0].encode())
        out[sha] = (h.hexdigest()[:16], parents, tree, subject)
    return out


def git_snapshot(repo, bare=False):
    """What the default probes read from one repository, as plain data."""
    refs = {}
    listing = repo.git(
        "for-each-ref",
        "--format=%(refname)%00%(objectname)%00%(objecttype)%00%(*objectname)%00%(*objecttype)",
    )
    for line in listing.splitlines():
        name, obj, kind, peeled, peeled_kind = line.split("\0")
        target, kind = (peeled, peeled_kind) if peeled else (obj, kind)
        if name != "refs/stash" and kind == "commit":
            refs[name] = target
    shot = {"refs": refs, "commits": _commits(repo, sorted(set(refs.values())))}
    if bare:
        return shot
    gitdir = Path(repo.git("rev-parse", "--absolute-git-dir").strip())
    status = repo.git(
        "status", "--porcelain=v1", "-z", "--no-renames", "--untracked-files=all"
    )
    return shot | {
        "head": repo.git("symbolic-ref", "-q", "HEAD", check=False).strip() or None,
        "status": sorted(e for e in status.split("\0") if e),
        "operation": next(
            (m for f, m in IN_PROGRESS.items() if (gitdir / f).exists()), None
        ),
        "stash": len(
            repo.git(
                "log", "--walk-reflogs", "--format=%H", "refs/stash", "--", check=False
            ).split()
        ),
    }


def git_state(_git, root):
    """{"": the repository, " on origin": its server, when it has one} under `root`."""
    root = Path(root)
    out = {"": git_snapshot(_git.Repo(root / "repo"))}
    if (root / "origin.git").is_dir():
        out[" on origin"] = git_snapshot(_git.Repo(root / "origin.git"), bare=True)
    return out


def _label(name, where):
    for prefix, said in (
        ("refs/heads/", ""),
        ("refs/tags/", "tag "),
        ("refs/remotes/", ""),
    ):
        if name.startswith(prefix):
            return f"{said}{name[len(prefix) :]}{where}"
    return f"{name}{where}"


def _ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _line(shot, name):
    """`name`'s first-parent line, oldest first, as (content id, parents, tree, subject)."""
    out, sha = [], shot["refs"][name]
    while sha:
        entry = shot["commits"][sha]
        out.append(entry)
        sha = entry[1][0] if entry[1] else None
    return out[::-1]


def _ref_difference(name, mine, key, where):
    label = _label(name, where)
    if name not in mine["refs"]:
        return f"{label} is missing"
    a, b = _line(mine, name), _line(key, name)
    for i, (x, y) in enumerate(zip(a, b)):
        if x[0] == y[0]:
            continue
        if x[3] != y[3]:
            return (
                f'{label}: its {_ordinal(i + 1)} commit is "{x[3]}", expected "{y[3]}"'
            )
        if x[2] != y[2]:
            return f'{label}: "{x[3]}" does not hold the files it should'
        if len(x[1]) != len(y[1]):
            return f'{label}: "{x[3]}" should {"be" if len(y[1]) > 1 else "not be"} a merge commit'
        return f'{label}: "{x[3]}" merges a different history than it should'
    n = abs(len(a) - len(b))
    commits = f"{n} commit{'s' if n != 1 else ''}"
    if len(a) > len(b):
        return f'{label} has {commits} too many, starting with "{a[len(b)][3]}"'
    return f'{label} is missing {commits}, starting with "{b[len(a)][3]}"'


def _cid(shot, name):
    sha = shot["refs"].get(name)
    return shot["commits"][sha][0] if sha else None


def git_difference(mine, key, start, skip, where=""):
    """The first way `mine` is not the answer key's repository, in the learner's words, or
    None. `start` is the key's repository before its commands ran, for the refs they
    deleted. A server has only refs to compare."""
    if mine is None:
        return f"there is no origin{where}" if where else "there is no repository"
    local = not where
    if local and "operation" not in skip and mine["operation"] and not key["operation"]:
        return mine["operation"]
    if "refs" not in skip:
        for name in sorted(key["refs"]):
            if _cid(mine, name) != _cid(key, name):
                return _ref_difference(name, mine, key, where)
    if "deleted" not in skip:
        for name in sorted(set(start["refs"]) - set(key["refs"])):
            if name in mine["refs"]:
                return f"{_label(name, where)} should be gone"
    if not local:
        return None
    if "head" not in skip and mine["head"] != key["head"]:

        def on(head):
            return _label(head, "") if head else "a detached commit"

        return f"HEAD is on {on(mine['head'])}, expected {on(key['head'])}"
    if "status" not in skip and mine["status"] != key["status"]:

        def listed(entries):
            return ", ".join(entries) or "nothing to commit"

        return (
            "the working tree or the staging area is not as it should be: "
            f"expected {listed(key['status'])}, found {listed(mine['status'])}"
        )
    if "stash" not in skip and mine["stash"] != key["stash"]:
        n = mine["stash"]
        return f"the stash holds {n} entr{'y' if n == 1 else 'ies'}, expected {key['stash']}"
    return None


def git_extra(_git, grade, brief, mine_root, key_root):
    """The task's own probes, `{sentence: argv}`, run in both repositories: the sentence of
    the first that differs, or None."""
    probes = grade.probes(brief) if hasattr(grade, "probes") else {}
    mine, key = _git.Repo(Path(mine_root) / "repo"), _git.Repo(Path(key_root) / "repo")
    for sentence, argv in probes.items():
        if mine.git(*argv, check=False) != key.git(*argv, check=False):
            return f"{sentence} is not as it should be"
    return None


def _typed(script, where):
    """Run commands in a repository as bash would, stopping at the first that fails:
    (whether they all ran, what the failing one said)."""
    try:
        done = subprocess.run(
            ["bash", "-e", "-c", script],
            cwd=where,
            capture_output=True,
            text=True,
            check=False,
            timeout=job["validator_seconds"],
        )
    except subprocess.TimeoutExpired:
        return False, "the commands did not finish"
    return done.returncode == 0, (done.stderr or done.stdout).strip()[-500:]


def _graph(_git, root):
    return _git.Repo(Path(root) / "repo").git(
        "log", "--graph", "--all", "--format=%s", "--", check=False
    )


def grade_git(grade):
    """A git sitting: the answer key built in scratch from `setup()` and `solution.sh`,
    then the learner's repository read in place and compared with it, probe by probe,
    then the task's own probes and `check()`."""
    g, brief = job["git"], job["brief"]
    sys.path.insert(0, g["tasks"])
    import _git

    sitting = Path(g["sitting"]) if g["sitting"] else None
    os.environ.update(g["env"])
    ceilings = {str(Path.cwd().parent)} | ({str(sitting.parent)} if sitting else set())
    os.environ["GIT_CEILING_DIRECTORIES"] = ":".join(sorted(ceilings))
    skip = set(getattr(grade, "SKIP", ()))
    key = _git.build(Path("key"), grade.setup, brief)
    start = git_state(_git, key)
    ran, said = _typed(g["key"], key / "repo")
    if not ran:
        answer(False, broken=f"solution.sh stopped: {said}")
    if sitting is None:
        sitting = _git.build(Path("mine"), grade.setup, brief)
        if g["script"] is not None:
            ran, said = _typed(g["script"], sitting / "repo")
            if not ran:
                answer(False, [(None, f"the commands stopped: {said}")])
    report = _graph(_git, sitting)
    theirs, keys = git_state(_git, sitting), git_state(_git, key)
    for where in keys:
        why = git_difference(theirs.get(where), keys[where], start[where], skip, where)
        if why:
            answer(False, [(None, why)], report)
    why = git_extra(_git, grade, brief, sitting, key)
    if why:
        answer(False, [(None, why)], report)
    if hasattr(grade, "check"):
        try:
            grade.check(_git.Repo(sitting / "repo"), brief)
        except AssertionError as exc:
            answer(
                False, [(None, str(exc) or "a rule of this task is not met")], report
            )
    answer(True, report=report)


GRADERS = {
    "helm": grade_helm,
    "docker": grade_docker,
    "sql": grade_sql,
    "git": grade_git,
}


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
