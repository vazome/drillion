# Task 11 — batch N2 report (native drills polish, 29 READMEs)

Scope: README.md only, in the 29 folders listed in `/tmp/task11-N2.md`. No `drill.py`, no
`progress.json`, no `src/`, no git state changes. Frontmatter values are byte-identical to HEAD in
all 29 files (checked with a diff of the frontmatter blocks). Every file keeps `# <title>`, its
`## Why` meaning, and `## Hints` last with exactly `### Hint 1..3`.

Applied throughout: hard-wrapped paragraphs unwrapped; every call/result example fenced as
```python with the result as a trailing `# ->` comment; rule lists that were really key → value
turned into GFM tables; test-punished rules turned into `> [!WARNING]`; multi-parameter
`## You get` blocks split into one paragraph per parameter so they no longer collapse into a single
run-on paragraph; identifiers backticked. No raw HTML, no bare URLs, no Mermaid needed.

## What changed, per file

- `032_csv` — CSV sample/result block → python fence; trailing prose rules → bullet list.
- `033_datetime` — timestamp sample and result dict fenced; tie-breaking rule ("ties → earliest") → `> [!WARNING]`; naive-timestamp note unwrapped.
- `034_percentile` — examples reformatted to `# ->` comments; the run-on "Rules:" sentence → bullet list.
- `035_subprocess` — the result dict and the `["false"]` case merged into one python fence; three-rule list kept as a list.
- `036_env` — the env-var block → a Variable/Type/Default table; return value fenced; the "DATABASE_URL has no default, let the KeyError escape" paragraph → `> [!WARNING]`.
- `037_argparse` — argument declarations → an Argument/Declaration table; command line fenced as ```bash; `parse_args` example fenced; "return the parser, do not parse" → `> [!WARNING]`.
- `038_logging` — argument block → table; build order → numbered list; level-filter example → python fence.
- `039_exitcodes` — exit codes → a Code/Meaning/When table; the four sample invocations → one python fence; "return an int, do not call sys.exit" → `> [!WARNING]`.
- `040_shutil` — the four staging steps → numbered list; the report dict → python fence keyed on `solve(root)`.
- `042_hashlib` — result dict fenced; basename/lowercase-hex rules → bullets; "read as BYTES, open in rb" → `> [!WARNING]`.
- `043_except` — example → python fence; "no bare `except:`" → `> [!WARNING]`.
- `044_customexc` — check order kept as a list, return-pair description → bullets, example → python fence.
- `045_retry` — rules → bullet list with the delay formula in its own fence; the sleep/jitter scenario → python fence with the scenario as comments.
- `046_deadline` — rules → bullet list; both scenarios (success and timeout) → one python fence.
- `047_idempotent` — the five add/update/remove cases → a Case/Action/Recorded table; example → python fence; two prose `->` arrows normalised to `→`.
- `048_requests` — four graded requirements → bullet list; example result → `# ->` comment; the 2xx/4xx/`raise_for_status` paragraph (and "don't test `status_code == 200`") → `> [!WARNING]`.
- `049_pagination` — page shape and the three-call walkthrough → python fences; rules → bullet list.
- `050_ratelimit` — response shapes fenced; the per-status decision list → a Response/Action table; the three-attempt scenario → python fence.
- `051_session` — url template fenced; shared headers → a Header/Value table; example → `# ->` comment; "the Session comes back and every request must come from it" → `> [!WARNING]`.
- `052_realpagination` — title line italicised like its siblings; the FastAPI-substitution note → `> [!NOTE]`; body sample, `Link` header (```http) and `response.links` fenced; page walkthrough → python fence; the three failure modes → bullet list.
- `053_hmac` — argument and step lists → bullets; examples → `# ->` comments; "Why not `==`" / "Why the raw bytes" given bold lead-ins.
- `054_threadpool` — `work=len` example → `solve(len, [...], 2)  # -> [2, 1, 4]`; rules → bullet list.
- `055_concurrency` — the kind/count rule → a Workload/Label table; example → python fence; `## Read first` → link list with titles.
- `056_asyncio` — `## Read first` → link list (gather anchor given a note); "the test fails a sequential loop" → `> [!WARNING]`.
- `059_mock` — the five steps → a numbered list with the return dict fenced inside step 4; example → `# ->` comments; "patch where it is used" → `> [!WARNING]`; `## Read first` → link list.
- `060_responses_mocking` — spec dict fenced; the four required registrations → a Method/URL/Status/Body table; `fetch_inventory` result → python fence; mock-strictness rules → bullet list.
- `061_whattotest` — the kind → verdict rule → table; example → python fence; the four rationale paragraphs given bold lead-ins; `## Read first` → link list.
- `068_boto3basics` — return-tuple description → bullets; example tuple → python fence; "a bigger page does not get you the whole bucket / read only" → `> [!WARNING]`.
- `069_s3audit` — the two exposure checks → a numbered list with the AllUsers URI and the `ClientError` code fenced inside each item; result list → python fence.

## Verification

```
$ uv run python - <<'PY'
from study.catalogue import exercises
SLUGS = [... the 29 batch slugs ...]
ex = exercises()
for slug in SLUGS:
    row = ex[slug]
    assert len(row["hints"]) == 3 and "## Why" in row["spec_md"]
    assert row["title"] and row["minutes"] and row["tags"]
print(f"OK — {len(SLUGS)}/{len(SLUGS)} batch slugs in exercises(), 3 hints each, ## Why present; catalogue total = {len(ex)}")
PY
OK — 29/29 batch slugs in exercises(), 3 hints each, ## Why present; catalogue total = 104
```

```
$ uv run study selfcheck
104/104 ok
```

Extra lint over the 29 files: no bare URLs (`^- http`), no raw HTML tags, `## Hints` is the last
`##` heading everywhere, exactly three `### Hint` headings each, and no `->` left outside a fence
(the two in `047_idempotent` were prose about dict shape and became `→`).

Frontmatter diff against HEAD: zero changes in all 29 files. `git status` shows no `drill.py`,
`progress.json` or `src/` modifications from this batch.

## Concerns

- The batch brief's last sentence names a special case, `101_explain_takehome` (questions with
  lettered options → `### Q1` headings). That slug is **not** in this batch's list of 29 drills, so
  it was left untouched — it looks like an instruction meant for the batch that owns topic 101.
  Worth confirming some batch has it.
- `055_concurrency`, `056_asyncio`, `059_mock` and `061_whattotest` carry migrated take-home notes
  whose text is a fragment (`**Take-home:** "why async here?"`, `**Take-home:** Task 3 judgement`).
  Meaning must not change, so they were left as they are; they may read oddly in the spec pane.
- Two `## Read first` entries had no note in the source (`docs.python.org/.../concurrency.html`,
  `asyncio.gather`). A short factual note was added so the link list is uniform; nothing was removed.
