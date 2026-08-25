# Task 11 — batch X report (the 17 Exercism drills)

Every README rebuilt to the "Exercism drills — keep their content, add ours" shape:
frontmatter unchanged → `# <title>` → `## Why` (ours, unwrapped) → `## Introduction`
(Exercism `introduction.md`, verbatim) → `## Instructions` (Exercism `instructions.md`
+ `instructions.append.md`, verbatim) → `## You get` / `## You return` (ours, now stating
how this repo's `solve` differs from Exercism's stub) → `## Rules` (ours, only what the
tests pin down) → `## Read first` (concept `links.json` for the concept drills, hand-picked
anchors kept) → attribution line → `## Hints` with exactly three `### Hint N`.

Exercism Markdown was mechanically transformed (`/tmp/t11/xform.py`, throwaway): headings
demoted so they nest under our `##` sections, `~~~~exercism/note` blocks turned into
`> [!NOTE]` GitHub alerts with their link-reference definitions hoisted out of the quote so
they still resolve, `<br>` lines dropped (no raw HTML). No sentence, code fence, table or
heading of Exercism's was dropped — verified mechanically, see below.

## What changed per file

| file | change |
| --- | --- |
| `exercises/200_guidos_gorgeous_lasagna/README.md` | + full `basics` Introduction and the 5-task Instructions; `You return` is now a key/what-it-holds table, examples refenced as `answers["…"](30)  # -> 10`; Rules note that task 5 (docstrings) is not graded; Read first = `concepts/basics/links.json` (10 links) + the two hand-picked anchors; Hints 1–2 fold in Exercism's per-task hints (naming/assignment, magic numbers, one operator per task, "call a function you defined previously") |
| `exercises/203_ghost_gobble_arcade_game/README.md` | + `bools` Introduction and the 4-rule Instructions; `You return` now a key/parameters/returns table; Rules note real `True`/`False` and positional order; Read first = `concepts/bools/links.json` (8 links); Hints 1–2 fold in "don't worry how the arguments are derived" and the Boolean-operators nudge |
| `exercises/206_currency_exchange/README.md` | + `numbers` Introduction and the **full** 6-task Instructions; `You get` note says this drill is Exercism tasks **1–3**, tasks 4–6 live in `207`; Rules repeat that split; table for the three functions; Read first = `concepts/numbers/links.json`; Hints 1–2 fold in the division/subtraction/multiplication hints |
| `exercises/207_currency_exchange/README.md` | same full Instructions, `You get` note says this drill is Exercism tasks **4–6**; `> [!WARNING]` on the graded return types (`int` for `get_number_of_bills`/`exchangeable_value`, float leftover); Hints 1–2 fold in Exercism's `//` vs `int()` note, the modulo hint and the actual-rate recipe |
| `exercises/209_meltdown_mitigation/README.md` | + `conditionals` Introduction (its own `# Conditionals` title kept as `### Conditionals`) and the 3-task Instructions; the two band lists became two tables; `> [!WARNING]` on the `<` vs `<=` boundaries the tests sit on; Read first = `concepts/conditionals/links.json`; Hints 1–2 fold in "any number of elif as branches", `else` as the catch-all, and the linter/common-variable advice |
| `exercises/212_black_jack/README.md` | + the long `comparisons` Introduction (operator table, chaining, identity, membership) and the **full** 6-task Instructions; `You get` note says this drill is Exercism tasks **1–3**; Rules pin the tuple-on-tie return; Read first = `concepts/comparisons/links.json`; Hints 1–2 fold in `==`/`in`/`int()` and "if we already have an ace in hand…" |
| `exercises/213_black_jack/README.md` | same Introduction + full Instructions, `You get` note says tasks **4–6** and points at the `# given — do not edit` `value_of_card`; Rules keep Exercism's "check for an ace and a ten-card, do not sum"; Hints 1–2 fold in the chaining hint, the split-pairs `A` note and "an `A` scored at 11 never allows doubling down" |
| `exercises/300_two_fer/README.md` | + Introduction and Instructions (Exercism's Name/Dialogue table kept as-is); note that the stub is `two_fer(name="you")` vs our `solve(name="you")`; examples refenced with trailing-comment results |
| `exercises/301_leap/README.md` | + Introduction (its `~~~~exercism/note` YouTube link became a `> [!NOTE]`) and Instructions; `> [!WARNING]` that the tests use `is True` / `is False`; Read first turned into linked bullets |
| `exercises/302_raindrops/README.md` | + Introduction and Instructions + `instructions.append.md` (the `%` / `math.fmod` / `divmod` discussion) as `### How this Exercise is Structured in Python`; rules list became a divides-by/result table; `> [!WARNING]` on fixed word order and the string fallback; Hint 1 folds in the "compare the remainder to zero" note |
| `exercises/303_bob/README.md` | + Introduction and the five-reply Instructions; the reply rules list became a table; `> [!WARNING]` that replies are compared character for character; Read first bare URLs turned into linked bullets; examples refenced |
| `exercises/304_reverse_string/README.md` | + Introduction and Instructions; example fence gained the `子猫` case and trailing-comment results; Hint 3's bare block is now a `python` fence with `# ->` results |
| `exercises/305_isogram/README.md` | + Instructions (Exercism ships **no** `introduction.md` for isogram, so there is no `## Introduction` — intentional); `> [!WARNING]` on `is True` / `is False`; Hint 1 folds in "spaces and hyphens are allowed to appear multiple times" |
| `exercises/306_pangram/README.md` | + Introduction (its note block, including the nested "The quick brown fox" quote, became a `> [!NOTE]`) and Instructions; `> [!WARNING]` on `is True` / `is False`; Read first linked |
| `exercises/307_anagram/README.md` | + the typewriter Introduction and Instructions; `You get` example is now a real Python list literal; `> [!WARNING]` that order and original spelling are compared with `==`; Hint 3 refenced |
| `exercises/308_hamming/README.md` | + Introduction, Instructions and `instructions.append.md` (`### Exception messages`); the error message is now a `raise ValueError("Strands must be of equal length.")` fence plus a `> [!WARNING]` that the message text is matched; Hints 1–2 fold in Exercism's raise-statement wording |
| `exercises/309_rna_transcription/README.md` | + Introduction (RNAi note → `> [!NOTE]`) and Instructions (its own note → `> [!NOTE]`); the `G -> C` rules block became a DNA/RNA table; Hint 3 refenced with `# ->` results |

## Verification

```
$ uv run python - <<'PY'
… asserts each batch-X slug is in exercises(), len(hints) == 3, spec_md has ## Why …
PY
200_guidos_gorgeous_lasagna      hints=3  '## Why' in spec_md=True  spec=17958 chars
203_ghost_gobble_arcade_game     hints=3  '## Why' in spec_md=True  spec=6321 chars
206_currency_exchange            hints=3  '## Why' in spec_md=True  spec=9936 chars
207_currency_exchange            hints=3  '## Why' in spec_md=True  spec=10717 chars
209_meltdown_mitigation          hints=3  '## Why' in spec_md=True  spec=10472 chars
212_black_jack                   hints=3  '## Why' in spec_md=True  spec=18112 chars
213_black_jack                   hints=3  '## Why' in spec_md=True  spec=18052 chars
300_two_fer                      hints=3  '## Why' in spec_md=True  spec=3160 chars
301_leap                         hints=3  '## Why' in spec_md=True  spec=2857 chars
302_raindrops                    hints=3  '## Why' in spec_md=True  spec=4749 chars
303_bob                          hints=3  '## Why' in spec_md=True  spec=3541 chars
304_reverse_string               hints=3  '## Why' in spec_md=True  spec=2570 chars
305_isogram                      hints=3  '## Why' in spec_md=True  spec=2515 chars
306_pangram                      hints=3  '## Why' in spec_md=True  spec=3260 chars
307_anagram                      hints=3  '## Why' in spec_md=True  spec=4278 chars
308_hamming                      hints=3  '## Why' in spec_md=True  spec=4916 chars
309_rna_transcription            hints=3  '## Why' in spec_md=True  spec=3455 chars

all 17 batch-X slugs present; catalogue has 104 drills
```

The same run also asserts, per slug: `## Instructions`, `## You get`, `## You return`,
`## Rules`, `## Read first` present; `spec_md` starts with `# <title>`; the attribution
line is in the spec; `## Hints` did not leak into the spec; no raw HTML and no
prose-inlined `->` outside code fences.

```
$ uv run study selfcheck
104/104 ok
```

Extra mechanical checks (throwaway scripts, nothing committed):

- **Exercism content coverage** — every non-blank, non-heading line of every
  `introduction.md`, `instructions.md` and `instructions.append.md` for the 17 exercises
  appears in the matching README (blockquote prefixes normalised): `missing lines: 0`.
- **Heading coverage** — every Exercism heading other than the merged file titles
  (`# Introduction`, `# Instructions`, `# Instructions append`) is present, demoted:
  `lost headings: 0`.
- **Level-2 headings per file** are exactly
  `Why | Introduction | Instructions | You get | You return | Rules | Read first | Hints`
  (305_isogram has no `Introduction`, because Exercism ships none for it).
- **Frontmatter** byte-identical to `HEAD` for all 17 files.
- `git status` shows no `drill.py`, `progress.json` or `src/` change from this batch.

## Concerns

1. **Attribution placement.** `task11-X.md` says the `*Adapted from …*` line must be the
   *last line of the file*; `task11-common.md` (binding) says `## Hints` is last with
   exactly three `### Hint N` sub-sections **and nothing else under it**. Those conflict —
   a trailing attribution lands inside Hint 3's text as the parser splits it, and would be
   served to the learner as part of an unlocked hint. I followed the binding common rule
   and the pre-pass model (`303_bob`): the attribution is the last line of the **spec**,
   immediately before `## Hints`. Easy to flip if the controller prefers the batch wording.
2. **Long specs.** `200`, `212` and `213` now carry Exercism's full concept introductions
   (18 KB of spec Markdown each; the `comparisons` intro alone is most of it) plus the full
   6-task Instructions in both halves of each split pair, as instructed. The spec pane
   scrolls, per the format spec, but these are an order of magnitude longer than the native
   drills — worth a look once the renderer exists.
3. **`~~~~exercism/*` blocks** are not GFM; the format spec allows GitHub alerts, so they
   were rewritten as `> [!NOTE]` / `> [!WARNING]` with wording untouched. Link reference
   definitions that lived inside those blocks were hoisted just below the quote so they
   resolve document-wide.
4. **Reference-style links** from Exercism (`[text][ref]` + definitions at the end of the
   source file) were kept as-is inside `## Introduction` / `## Instructions`, which is safe
   because the whole spec is rendered as one document. In `## Hints` — which the API serves
   as three separate strings — every folded-in Exercism link was inlined instead, so no hint
   can render a dangling `[ref]`.
5. `206`/`207` and `212`/`213` each contain the other half's Instructions verbatim, as
   required. The `> [!NOTE]` in `## You get` and the first bullet of `## Rules` both state
   which numbered tasks the drill actually grades, so a learner reading the Instructions
   does not start writing the other drill's functions.
