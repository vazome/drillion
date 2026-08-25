"""One-off: turn the flat `exercises/ex_<NNN>_<name>.py` drills into one folder each.

Run once, from the repo root, then delete this file. Every drill becomes
`exercises/<NNN>_<name>/` holding `README.md` (YAML frontmatter + Markdown
guidance, converted from META / the solve docstring / READ FIRST / HINTS) and
`drill.py` (the learner's region, the machinery marker, the machinery). The keys
in `progress.json` lose their `ex_` prefix. Nothing is thrown away: text the
converter cannot classify lands under `## Rules` unchanged, and it says so.
"""

import ast
import inspect
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, "src")
from study.region import MARKER

ROOT = Path(__file__).parent
EX = ROOT / "exercises"
LABELS = [("WHY:", "## Why"), ("YOU GET:", "## You get"), ("YOU RETURN:", "## You return")]
RULES = re.compile(r"^─+ (.+?) ─+$")            # "exact rules" in 103 of 104
OLD_MARKER = re.compile(r"^# ─+\s+below here is the machinery\s+─+$")
BULLET = re.compile(r"^\s{0,3}([-*]|\w{1,3}[.)]) ")
CODEISH = re.compile(r"^\s*([\w.]+\(|>>> |(def|class|import|from|for|if|while|with|return|print|"
                     r"assert|await|async|try|raise|yield|lambda|del)\b)")
unclassified = []


# ---------------------------------------------------------------- markdown
def _kinds(lines):
    """Mark each line CODE or not: an indented run that is not a list continuation."""
    kinds, bullet = [], None
    for line in lines:
        indent = len(line) - len(line.lstrip(" "))
        if not line.strip():
            bullet, kind = None, False
        elif BULLET.match(line):
            bullet, kind = indent, False
        elif indent >= 4:
            kind = bullet is None
        else:
            bullet, kind = None, False
        kinds.append(kind)
    return kinds


def markdown(text):
    """A docstring section as Markdown: prose kept verbatim, indented runs fenced."""
    lines = text.split("\n")
    kinds = _kinds(lines)
    out, i = [], 0
    while i < len(lines):
        if not kinds[i]:
            out.append(lines[i])
            i += 1
            continue
        end = i                                  # the run, trailing blank lines excluded
        for j in range(i, len(lines)):
            if kinds[j]:
                end = j
            elif lines[j].strip():
                break
        block = lines[i:end + 1]
        pad = min(len(ln) - len(ln.lstrip(" ")) for ln in block if ln.strip())
        lang = "python" if any(CODEISH.match(ln) for ln in block) else ""
        out += ["", f"```{lang}", *[ln[pad:] for ln in block], "```", ""]
        i = end + 1
    return "\n".join(out).strip("\n")


def _tidy(md):
    """No run of blank lines longer than one — outside the fences, where they count."""
    parts = md.split("```")
    parts[::2] = [re.sub(r"\n{3,}", "\n\n", p) for p in parts[::2]]
    return "```".join(parts).strip("\n") + "\n"


def _lede(doc):
    """The module docstring under the title: italic when it is one line, plain when
    it is a paragraph or two (emphasis cannot span a blank line)."""
    doc = inspect.cleandoc(doc)
    return f"*{doc}*" if "\n" not in doc else doc


# ---------------------------------------------------------------- the old file
def _assign(tree, name):
    return next(n for n in tree.body
                if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == name)


def sections(doc, slug):
    """The solve docstring split by its labels; anything unlabelled joins the rules."""
    lines = inspect.cleandoc(doc).split("\n")
    found, rest = {}, []
    label = None
    for line in lines:
        hit = next((md for old, md in LABELS if line.startswith(old)), None)
        if hit:
            label = hit                      # 4 drills say YOU GET: twice, once per argument
            found.setdefault(label, []).extend(
                ["", line.split(":", 1)[1].lstrip()] if label in found
                else [line.split(":", 1)[1].lstrip()])
        elif RULES.match(line.strip()):
            named = RULES.match(line.strip()).group(1)
            label = "## Rules"
            found[label] = [] if named == "exact rules" else [f"**{named.capitalize()}**", ""]
            if named != "exact rules":
                unclassified.append(f"{slug} (rules block named {named!r})")
        elif label:
            found[label].append(line)
        else:
            rest.append(line)                    # nothing before WHY: in any of the 104
    if rest and any(ln.strip() for ln in rest):
        unclassified.append(f"{slug} (unlabelled lines)")
        found.setdefault("## Rules", []).extend(["", *rest])
    return {k: "\n".join(v).strip("\n") for k, v in found.items()}


def read_first(tree, lines):
    """The `# READ FIRST:` comment block: ([url-and-note, ...], take-home, heading note)."""
    entries, take, note = [], None, ""
    for raw in lines[tree.body[0].end_lineno:]:      # the block sits under the module docstring
        if not raw.startswith("#"):
            break
        line = raw[1:]
        text = line.strip()
        if text.startswith("READ FIRST"):            # one block carries a note in its heading
            note = text.removeprefix("READ FIRST").strip(" :")
            continue
        if not text or text.startswith("SOURCE:"):
            continue
        if text.startswith("TAKE-HOME:"):
            take = text.removeprefix("TAKE-HOME:").strip()
        elif len(line) - len(line.lstrip(" ")) > 3 and entries:   # a wrapped note
            entries[-1] += " " + text
        else:
            entries.append(text)
    return entries, take, note


def convert(path):
    src = path.read_text()
    tree = ast.parse(src)
    lines = src.split("\n")
    slug = path.stem.removeprefix("ex_")
    meta = ast.literal_eval(_assign(tree, "META").value)
    hints = ast.literal_eval(_assign(tree, "HINTS").value)
    head, tail = _assign(tree, "META"), _assign(tree, "HINTS")
    body = "\n".join(lines[head.end_lineno:tail.lineno - 1]).strip("\n")

    # --- drill.py: the region above the marker, the machinery below it
    fn = next(n for n in ast.parse(body).body
              if isinstance(n, ast.FunctionDef) and n.name == "solve")
    doc = fn.body[0]
    blines = body.split("\n")
    region = "\n".join(blines[:doc.lineno - 1] + blines[doc.end_lineno:]).strip("\n")
    used = {n.id for n in ast.walk(ast.parse(region)) if isinstance(n, ast.Name)}
    keep, move = [], []
    for node in tree.body[:tree.body.index(head)]:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        text = "\n".join(lines[node.lineno - 1:node.end_lineno])
        (keep if any((a.asname or a.name.split(".")[0]) in used for a in node.names)
         else move).append(text)
    rest = [ln for ln in lines[tail.end_lineno:] if not OLD_MARKER.match(ln)]
    machinery = "\n".join(rest).strip("\n")
    # a blank line under the marker keeps it out of ruff's import block, so isort
    # can sort the machinery imports without dragging the marker down with one
    drill = "\n\n\n".join(x for x in ["\n".join(keep), region] if x)
    drill += "\n\n\n" + MARKER + "\n\n" + "\n".join(move)
    drill += "\n\n\n" + machinery + "\n"

    # --- README.md
    fm = {"title": meta["title"], "minutes": meta["minutes"],
          "prereqs": meta["prereqs"], "tags": meta["tags"]}
    if meta.get("practices"):
        fm["practices"] = meta["practices"]
    source = next((ln[len("# SOURCE:"):].strip() for ln in lines if ln.startswith("# SOURCE:")),
                  None)
    if source:
        fm["source"] = source
    sec = sections(ast.get_docstring(fn), slug)
    md = ["---",
          yaml.safe_dump(fm, sort_keys=False, allow_unicode=True,
                         default_flow_style=None, width=10_000).strip(),
          "---",
          f"# {meta['title']}",
          "",
          _lede(ast.get_docstring(tree))]
    for heading in ("## Why", "## You get", "## You return", "## Rules"):
        md += ["", heading, markdown(sec[heading])]
    links, take, note = read_first(tree, lines)
    if links:
        md += ["", "## Read first", *([note, ""] if note else []), *[f"- {ln}" for ln in links]]
    if take:
        md += ["", "> [!NOTE]", f"> **Take-home:** {take}"]
    if source:
        md += ["", "*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*"]
    md += ["", "## Hints"]
    for n, hint in enumerate(hints, 1):
        md += [f"### Hint {n}", markdown(hint)]   # a hint is a plain string, not a docstring

    folder = EX / slug
    folder.mkdir(exist_ok=True)
    subprocess.run(["git", "mv", str(path), str(folder / "drill.py")], check=True, cwd=ROOT)
    (folder / "drill.py").write_text(drill)
    (folder / "README.md").write_text(_tidy("\n".join(md)))


def main():
    files = sorted(EX.glob("ex_*.py"))
    for path in files:
        convert(path)
    state = json.loads((ROOT / "progress.json").read_text())
    rename = (lambda d: {k.removeprefix("ex_"): v for k, v in d.items()})
    state["cards"], state["open"] = rename(state["cards"]), rename(state["open"])
    state["archive"] = rename(state["archive"])
    for entry in state["log"]:
        entry["slug"] = entry["slug"].removeprefix("ex_")
    (ROOT / "progress.json").write_text(json.dumps(state, indent=1))
    print(f"{len(files)} drills → folders")
    print("unclassified docstring lines:", sorted(set(unclassified)) or "none")


if __name__ == "__main__":
    main()
