# Task 11 batch N3b — report

Native drills polish, 9 files: 093_message_dig, 094_await_under_lock, 095_semaphore, 096_async_cm,
097_lazy_init_lock, 098_fixtures, 099_asgi_test, 100_rerank, 101_explain_takehome.

## Per-file changes

- `exercises/093_message_dig/README.md` — italicised the whole-task intro line; fenced the payload
  literal, the `payload["choices"]...` snippet, the return shape and the worked example (`python`,
  with a real `solve(payload)` call and `# ->` result); rebuilt the badly-wrapped "Rules" prose
  (fragments were half inside stray code fences) into a clean bullet list, one bullet per output
  key; split the trailing "do not modify payload" / "narrate the path" sentence into a
  `> [!WARNING]` (test-punished mutation check) and a `> [!TIP]` (discipline). No `## Read first`
  existed in the source — none added.
- `exercises/094_await_under_lock/README.md` — turned the broken mid-sentence code fences in
  "You get" into a normal bullet list (`q`, `pool`, `embed`, `conn.fetch`); moved the ordering
  sentence out of "Rules" into a `> [!WARNING]` (test checks event order, not wall-clock); converted
  the four bare `- https://...` Read-first lines to `- [text](url) — note`; Hint 3's "SAY IT IN THE
  INTERVIEW: '...'" became **Say it in the interview:** + a blockquote, verbatim wording kept.
- `exercises/095_semaphore/README.md` — Read-first links converted to markdown link form; Hint 3
  interview line converted to bold label + blockquote. Rules/You-get were already clean lists, left
  as-is.
- `exercises/096_async_cm/README.md` — "You get" broken fences turned into a bullet list (`rows`,
  `max_size`); moved the max_size=1 re-entry/wait-not-raise sentence out of "Rules" into
  `> [!WARNING]` (exactly the kind of ordering/behaviour trap the tests punish); Read-first links
  converted; Hint 3 converted to blockquote.
- `exercises/097_lazy_init_lock/README.md` — "You get" broken fence turned into one bullet; Read-first
  links converted; Hint 3 converted to blockquote. Rules list (double-checked-locking rules) left as
  a list — not an input→output table.
- `exercises/098_fixtures/README.md` — numbered "You return" list kept as an ordered list; split the
  monkeypatch-vs-globals rule into a plain Rules bullet plus a `> [!WARNING]` for the
  test-punished "teardown must restore originals" clause; Read-first links converted (including the
  two RealPython/pytest doc anchors); Hint 3 converted to blockquote.
- `exercises/099_asgi_test/README.md` — Read-first links converted; moved the `params={}` → 422
  "do not special-case it" rule into a `> [!WARNING]` (a trap the tests check); Hint 3 converted to
  blockquote.
- `exercises/100_rerank/README.md` — "You get" converted from broken-fence prose to a clean bullet
  list; worked example turned into a real fenced `solve(query, rows, k=2)` call with `# ->` result
  (verified against `drill.py`'s signature `solve(query, rows, k)`); Read-first links converted;
  Hint 3 converted to blockquote.
- `exercises/101_explain_takehome/README.md` — special case per assignment: the ten lettered
  questions became `### Q1` … `### Q10` under `## Rules`, each with its four options as a plain
  bullet list (`a)`/`b)`/`c)`/`d)`), every word of the questions and options kept verbatim; added a
  fenced `solve()` example in "You return" whose answer dict was checked against `drill.py`'s
  `_reference()` (`{1: "b", 2: "c", 3: "b", 4: "b", 5: "c", 6: "b", 7: "c", 8: "b", 9: "b", 10: "b"}`
  — matches exactly); Read-first bare URLs converted to `- [text](url)`; Hint 3's
  "SAY IT IN THE INTERVIEW (the whole story in 6 sentences)" converted to bold label + blockquote,
  wording unchanged.

Common transforms applied across all 9: bare `- https://...` Read-first lines → `- [text](url) — note`;
"SAY IT IN THE INTERVIEW: '...'" in Hint 3 → `**Say it in the interview:**` + blockquote (no GFM
alert type fit a first-person quoted answer better than a plain blockquote); broken mid-sentence
code fences (artifacts of the original hard-wrapped docstring) unwrapped into normal prose/lists;
ordering/mutation rules the tests actually punish moved into `> [!WARNING]`; `> [!NOTE]` **Take-home:**
lines kept unchanged. No `drill.py` touched. No frontmatter values changed.

## Verification

```
$ uv run python - <<'PY'
from study import catalogue
slugs = ["093_message_dig","094_await_under_lock","095_semaphore","096_async_cm",
         "097_lazy_init_lock","098_fixtures","099_asgi_test","100_rerank","101_explain_takehome"]
exs = catalogue.exercises()
for s in slugs:
    assert s in exs, f"MISSING {s}"
    e = exs[s]
    assert len(e["hints"]) == 3, f"{s} hints={len(e['hints'])}"
    assert "## Why" in e["spec_md"], f"{s} missing Why"
    print(s, "OK", len(e["hints"]), "hints")
print("ALL OK")
PY
093_message_dig OK 3 hints
094_await_under_lock OK 3 hints
095_semaphore OK 3 hints
096_async_cm OK 3 hints
097_lazy_init_lock OK 3 hints
098_fixtures OK 3 hints
099_asgi_test OK 3 hints
100_rerank OK 3 hints
101_explain_takehome OK 3 hints
ALL OK

$ uv run study selfcheck
104/104 ok
```

`git status --porcelain` for the batch shows only the 9 README.md files modified, nothing else.

## Concerns

None. One judgement call worth flagging: `093_message_dig` has no `## Read first` section in the
source and I did not add one (common instructions say never delete guidance, not to invent new
content); all other 8 files had one and kept it, reformatted as markdown links.
