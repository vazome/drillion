---
title: pathlib — plan the output tree a static site build would write
difficulty: medium
tier: core
minutes: 12
prereqs: [54]
tags: [pathlib, files-text]
---
# pathlib — plan the output tree a static site build would write

*`relative_to`, `with_suffix` and `as_posix` are the three moves that turn found paths into written ones.*

## Read first
- [pathlib](https://devdocs.io/python~3.14/library/pathlib) — `rglob`, `relative_to`, `with_suffix`, `parts`, `as_posix`
- [PurePath.as_posix](https://devdocs.io/python~3.14/library/pathlib#pathlib.PurePath.as_posix) — the path with forward slashes, whatever the OS

## Why
A static site generator reads a folder of Markdown and writes the matching folder of HTML. Before it writes anything, the build wants to say what it is about to produce, so the plan can be reviewed, diffed against the last build, and checked into a manifest that has to read the same on a Linux runner and a Windows laptop. Every page keeps its place in the tree and swaps its extension, and anything sitting in a `drafts` folder is not published at all.

## You get
`root` — a string with the path to the source folder, like `"/tmp/site_xyz"`. It holds Markdown files at any depth, other files that are not pages, and some `drafts` folders. The test builds the tree and hands you the path; you never build it yourself.

## You return
a sorted list of strings: the path each page would be written to, relative to the output root.

## Rules
For every `*.md` file anywhere under `root`:

- keep its position in the tree, expressed **relative to `root`** — never the absolute path
- swap the `.md` extension for `.html`
- write it with forward slashes, on every operating system
- skip it entirely when any folder on the way to it is named `drafts`

Return the list sorted.

```text
root/
  index.md
  guides/setup.md
  guides/drafts/wip.md
  guides/notes.txt
```

```python
solve(root)
# -> ["guides/setup.html", "index.html"]
```

> [!WARNING]
> Joining and slicing the path as a string is what this task exists to replace. On Windows the separator is `\`, so a manifest built by chopping strings sorts and compares differently depending on which machine ran the build. Ask the path object for its pieces and for its POSIX form, and the difference disappears.

## Hints
### Hint 1
Three questions, each one a method on a `Path`. Where is this file relative to the root? What is it called with a different extension? What are the folder names along the way, so you can look for `drafts` among them? Search the whole tree, not just the top.
### Hint 2
`Path(root).rglob("*.md")` finds them all. `p.relative_to(root)` drops the shared prefix and leaves the part that matters. `.with_suffix(".html")` swaps the extension on the last component. `.parts` is the tuple of components, which is where you check for `"drafts"` — do it on the **relative** path, or a folder named `drafts` further up outside the root would hide the whole site. `.as_posix()` gives the string.
### Hint 3
Different data, same moves:

```python
from pathlib import Path

root = Path("/srv/site")
page = root / "guides" / "v2" / "setup.md"
rel = page.relative_to(root)
print(rel.parts)                       # ('guides', 'v2', 'setup.md')
print(rel.with_suffix(".html"))        # guides/v2/setup.html
print(rel.with_suffix(".html").as_posix())   # 'guides/v2/setup.html' on Windows too
print("drafts" in rel.parts)           # False
```

`with_suffix` replaces the extension rather than appending one, so it is safe on a name that already has one.
