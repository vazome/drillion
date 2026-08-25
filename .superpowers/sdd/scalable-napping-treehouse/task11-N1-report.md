# Task 11 — batch N1 report (native drills polish, 29 READMEs)

Edited README.md only. No `drill.py`, `progress.json`, `src/` or git state touched.
Frontmatter values unchanged everywhere; `## Why` wording preserved (unwrapped only).

## What changed, per file

| file | change |
| --- | --- |
| `exercises/001_fstrings/README.md` | unwrapped paragraphs; `## You get` literal fenced; rules block split into a bullet list + `python` call/result fence + `text` fence showing the printed table |
| `exercises/002_slicing/README.md` | five-key rules block → GFM table; example → `python` fence with `# ->` result; paragraphs unwrapped |
| `exercises/004_ordefault/README.md` | rules → bullet list; two examples → one `python` fence; "`port or 8080` fails this test" → `> [!WARNING]` |
| `exercises/005_enumzip/README.md` | example → `python` fence; "no manual counter / no `range(len(...))`" → `> [!TIP]` (test does not punish it, it is a discipline rule) |
| `exercises/006_unpacking/README.md` | six-key rules block → GFM table; example → `python` fence; "slicing would pass, do it with star-unpacking anyway" → `> [!TIP]` |
| `exercises/007_mutabledefault/README.md` | buggy/fixed descriptions → bullet list; prediction example → `python` fence; snippets kept verbatim |
| `exercises/008_closures/README.md` | `n=3, x=10 -> (...)` → `solve(3, 10)  # -> ...` fence; paragraphs unwrapped; inline code backticked |
| `exercises/009_sortkey/README.md` | `## Read first` → markdown link list with titles; example → `python` fence; `## You get` literal fenced |
| `exercises/010_comprehension/README.md` | example → `python` fence; Hint 2 skeleton fenced as `text` |
| `exercises/011_generators/README.md` | example → `python` fence using `next(g)`; the laziness/`inspect.isgenerator` paragraph → `> [!WARNING]` (the test really checks it) |
| `exercises/012_decorators/README.md` | rules bullets flattened into a proper list; `calls` result line given `# ->`; `## Read first` → link list |
| `exercises/013_contextmanager/README.md` | example fence given `# ->` results; "the exception must still reach the caller" → `> [!WARNING]`; `## Read first` → link list |
| `exercises/014_classes/README.md` | rules → bullet list (repr f-string inlined as code span); example results → `# ->`; "do not store `total_cpu`" → `> [!WARNING]` (test bumps replicas) |
| `exercises/015_dataclasses/README.md` | field block → `python` fence; example → `solve([...])  # -> [...]` fence; `## You get` literal fenced |
| `exercises/016_typehints/README.md` | params/nullable/ret block → bullet list; signature + return example → one `python` fence; nullable-return + declaration-order trap → `> [!WARNING]`; `## Read first` → link list (6 links) |
| `exercises/017_functools/README.md` | rules → bullet list; example results → `# ->`; the `__name__`/`__doc__` paragraph → `> [!WARNING]` (test asserts both) |
| `exercises/018_dictget/README.md` | example → `python` fence; paragraphs unwrapped; inline code backticked |
| `exercises/019_counter/README.md` | paragraphs unwrapped; `## You get` line-shape fenced; example → `python` fence with a real 3-line log and `# ->` result |
| `exercises/020_defaultdict/README.md` | grouping example → `python` fence with `# ->` result; paragraphs unwrapped |
| `exercises/021_deque/README.md` | example → `solve(iter([...]), 1)  # -> [...]` fence; "`lines` is an ITERATOR, no `len()`/slicing" → `> [!WARNING]` (test passes `iter(...)`) |
| `exercises/022_sets/README.md` | example → `python` fence; `## Read first` → link list |
| `exercises/023_itertools/README.md` | `solve(pages, 3) -> ...` → `# ->` comment; the groupby-on-unsorted trap → `> [!WARNING]`; `## You get` literal fenced |
| `exercises/025_copy/README.md` | `## You get` literal fenced; paragraphs unwrapped; snippet kept verbatim |
| `exercises/026_filelines/README.md` | sample log → `text` fence; result → `solve(path)  # -> [...]`; "pretend the file is 40 GB, no `.read()`" → `> [!TIP]` |
| `exercises/027_pathlib/README.md` | tree → `text` fence; return dict → `python` fence plus a GFM table for the three keys' meanings |
| `exercises/028_join/README.md` | example → `python` fence; paragraphs unwrapped |
| `exercises/029_regex/README.md` | sample log line → `text` fence; result → `python` fence; greedy-`.*` trap → `> [!WARNING]`; `## Read first` → link list |
| `exercises/030_json/README.md` | payload and printed output → `json` fences; summary → `python` fence; "indexing an absent optional key must not crash" → `> [!WARNING]` |
| `exercises/031_yamlflat/README.md` | config sample → `yaml` fence; result → `python` fence; parse rules → bullet list; the type-conversion rules → GFM table |

Conventions applied uniformly: every call/result example is a fenced `python` block with the
result as a trailing `# ->` comment; existing `TAKE-HOME` callouts (009, 012, 013, 016, 022, 029)
left as `> [!NOTE] **Take-home:**`; `## Read first` bare URLs replaced by
`- [link text](url) — note` bullets (009, 012, 013, 016, 022, 029); hard-wrapped ~72-column
paragraphs unwrapped; no raw HTML, no mermaid added; `## Hints` remains last with exactly
`### Hint 1..3`.

Two prose `->` arrows that were *mappings*, not call results, became `→` rather than fences:
`016` ("parameter name → resolved annotation") and `030` (`"status"` → `"phase"`).

## Verification

```
$ uv run python - <<'PY'
from study.catalogue import exercises
SLUGS = [... the 29 N1 slugs ...]
ex = exercises()
for s in SLUGS:
    assert s in ex, f"{s} MISSING from catalogue"
    d = ex[s]
    assert len(d["hints"]) == 3, f"{s}: {len(d['hints'])} hints"
    assert "## Why" in d["spec_md"], f"{s}: no ## Why"
    for k in ("title", "minutes", "tags"):
        assert d.get(k), f"{s}: missing {k}"
print(f"OK — all {len(SLUGS)} N1 slugs in exercises(), len(hints) == 3, '## Why' in spec_md")
PY
OK — all 29 N1 slugs in exercises(), len(hints) == 3, '## Why' in spec_md
```

```
$ uv run study selfcheck
104/104 ok
```

An extra lint pass over the 29 files confirmed: no unclosed fences, no bare URLs outside
fences, no `->` prose notation outside fences, no raw HTML tags (the `<service>`/`<id>`/
`(?P<name>...)` occurrences in 011, 013 and 029 are inside inline code spans), exactly three
`### Hint` headings each, and no `##` section after `## Hints`.

`git status` shows only `M exercises/<slug>/README.md` for the 29 N1 slugs (other modified
paths belong to the sibling batches running concurrently).

## Concerns

- The N1 assignment note mentions a special case for `101_explain_takehome` ("render each
  question as `### Q1` with lettered options as a list"), but that slug is **not** in the N1
  drill list (which is 001–031 native drills, 29 of them). I left `101_explain_takehome`
  untouched — it looks like the instruction belongs to whichever batch owns the 1xx range.
  Worth confirming somebody picks it up.
- `019_counter` is listed both as the *model* native README in the common instructions and as a
  file to polish in N1. I polished it (it was still pre-pass: hard-wrapped, unfenced example),
  matching the shape shown in the content-format spec's own `019_counter` sample. If later
  batches were told to copy the on-disk 019 verbatim as a model, they now see the polished one,
  which should be the better reference anyway.
- `> [!TIP]` is used (005, 006, 026) for rules the tests do *not* punish but the drill insists
  on ("no `range(len(...))`", "slicing would pass — use unpacking anyway", "don't call
  `.read()`"). The common instructions only define NOTE (take-home) and WARNING
  (test-punished); TIP is a supported GitHub alert per the format spec, so this keeps WARNING
  meaning "the test will fail you".
