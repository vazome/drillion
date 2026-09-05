# Authoring a task

[CONTEXT.md](../CONTEXT.md) says what each word means. This file says how to **choose** a tier,
a difficulty, a track or a tag, and what the folder has to contain.
[CONTRIBUTING.md](../CONTRIBUTING.md) has the contract a submission is graded against.

## Choosing the vocabulary

**tier** — how far into the language a task reaches. Exactly one of three:

| tier | what belongs in it | today |
|---|---|---|
| `core` | the language and its standard library, and every coder needs it: syntax, data structures, files and text, errors, `itertools`, `pathlib` | 142 |
| `advanced` | still the standard library, but you can work a long while without it: `asyncio`, concurrency, generators, decorators, closures, `functools` | 17 |
| `packages` | solving it needs something `pip` installs: `requests`, `responses`, `boto3`, `moto`, `pytest`, `fastapi`, `langchain` | 15 |

Tier answers "can I run this with stock Python?", so `packages` wins whenever a task is both —
an `asyncio` task that stands up a FastAPI app to have something to await is `packages`, not
`advanced`. The test is what **the solution** needs: a library the learner's own code imports,
or that the task is plainly about. Imports below the machinery marker are the grader's and do
not count — 14 tasks `import pytest` down there for `pytest.approx` alone and are `core`, while
`084_fixtures` is `packages` because its `@pytest.fixture` is in the learner's region.

**difficulty** — how hard the task is to get **right the first time**: `easy`, `medium` or
`hard`. It is not how long the task takes. Thirty minutes of unsurprising typing is `easy`; six
lines you can only write once you have seen the trick is `hard`. Anchor the call on the task's
`## Rules` — rules are where the traps live — and grade a new task against the rubric all 174
were graded against: [difficulty-rubric.md](difficulty-rubric.md).
Today: 36 easy · 111 medium · 27 hard.

**track** — optional, at most one per task: a themed run through the catalogue that cuts across
tiers, for a sequence meant to be practised in order. No track is defined today. Leave the key
out unless the task belongs to such a run.

**tags** — what Python you practise. Lowercase, kebab-case, 1–3 per task, and one rule decides
every one of them:

> A tag names a **Python concept you can practise** — never the task's identity, never its story.

`recursion`, `dict-get`, `context-managers` and `bitwise` are tags: each names something you
could sit down and get better at, and something a *future* task could also be tagged with.
`flatten-array`, `phone-screens` and `take-home-task-2` are not. They name one task and could
never name another.

A tag on a single task is fine — 40 of the 80 are, because 174 tasks cannot cover every concept
twice. The test is not "does more than one task have it?" but "**could** another task have it?".
So reach for an existing tag before minting a synonym — `sets` not `set`, `strings` not
`str-stuff` — and when nothing fits, name the concept, not the task. `GET /api/catalogue`
returns the whole vocabulary under `tags`.

**focus** in `progress.json` is a single string, and the scheduler matches it against a task's
tier, track and tags alike (`scheduler.py:_facets`): `advanced` and `recursion` are both
valid. It restricts which *new* tasks are offered — reviews and the open catalogue ignore
it — and `POST /api/focus` sets it.

## The folder

One folder per task, `tasks/<NNN>_<name>/`; copy the shape of an existing one.

`<NNN>` is an ascending id, `001`–`175` with `087` retired, so the next task you add is `176`. It is an
identity and nothing else: it encodes no difficulty, no section and no provenance. Append, never
insert — `prereqs:` points at these numbers, so renumbering means rewriting other people's
frontmatter.

**`README.md`** — YAML frontmatter, then GitHub-flavoured Markdown:

```markdown
---
title: Counter — top N by frequency   # the concept first, then what you build with it
difficulty: medium                    # easy | medium | hard
tier: core                            # core | advanced | packages
track: <run-name>                     # optional, omit it unless the task is part of a run
minutes: 12                           # par time — the grader's input, never shown to the learner
prereqs: [18]                         # task numbers that gate it; [] when nothing does
tags: [counter, sorted]               # Python concepts, lowercase kebab-case
source: exercism/python practice/two-fer (MIT, adapted)   # optional
---
# Counter — top N by frequency
## Why / ## You get / ## You return / ## Rules / ## Read first
## Hints
### Hint 1 … ### Hint 2 … ### Hint 3
```

Write the keys in that order. `title`, `difficulty`, `tier`, `minutes` and `tags` are required;
no real task carries all eight keys. The title leads with the concept, never with a puzzle name:
Exercism's `bob` is `conditionals — classify a message into one of five replies`, and the puzzle
name survives in the slug and in `source:`. The number is **not** in the frontmatter — it is the
folder's leading digits, and the API exposes it as `topic`. The **spec** is everything from
`# title` up to `## Hints`; extra sections (`## Introduction`, `## Instructions`) may go anywhere
before it. Headings, lists, tables, fenced code, GitHub alerts (`> [!NOTE]`), Mermaid diagrams,
images and muted looping clips from `assets/` all render. For a task adapted from Exercism the
README carries **Exercism's Markdown verbatim** — never trimmed to make room for ours — plus
frontmatter `source:` and a closing attribution line.

**`task.py`** — code only, no docstring spec, no META, no HINTS:

```python
from collections import Counter        # the learner's imports, given code and solve()

def solve(lines, n):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══
from _lib import rng

def _gen(r): ...                        # builds inputs from a seeded random.Random
def _reference(lines, n): ...           # the correct implementation; tests compare yours to it
def test_solve(): ...                   # generated cases, plus canonical ones where they exist
```

**The region contract.** Everything above the marker line is the learner's: it is the text the
editor shows and the only text a save may replace. `solve` is the last statement in it; given
code (constants, exception classes, a toy app) goes above `solve`, never below. The machinery
(`_gen`, `_reference`, `test_*`) is never sent to the editor, and an edit that pastes the marker,
defines `_reference`/`_gen`/`test_*` or names `_reference` is refused.

## When a new task does not show up

A folder the catalogue cannot read is **skipped**, not reported: a half-written task must never
break the menu for the other 173. That makes a mistake look like a task that simply is not there.
Run `uv run drillion doctor` — it reports every rule the folder breaks, not just the first:

- a required key missing, empty, or misspelt (`tags: []` counts as missing);
- frontmatter that is not a closed `---` block, or is not valid YAML;
- `task.py` with no machinery marker line, or with no `solve()` as the last statement of the
  learner's region, or that does not parse;
- a hint count that is not **exactly 3** — `### Hint 1`, `### Hint 2`, `### Hint 3` under
  `## Hints`.

`uv run drillion selfcheck` splices `_reference` into every file and runs the tests; it must be
green before a task is trusted. But it only counts tasks the catalogue already accepted, so if it
still says `174/174` after you added one, `doctor` is where to look.

## Retired tags

Six were retired when the vocabulary landed. If an old branch or an old note still uses one:

| retired tag | where it went |
|---|---|
| `exercism` | `source:` — provenance is a field, not a concept you can practise (84 tasks carry one) |
| `core`, `data-structures` | `tier:` — the coarse grouping is its own key now |
| `whole-task` | `difficulty:` — it marked size, and size is not difficulty |
| `rsample` | retired with the track it named |
| `basics` | `functions` — the concept the tasks actually taught |
