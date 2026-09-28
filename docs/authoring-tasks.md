# Authoring a task

[CONTEXT.md](../CONTEXT.md) says what each word means. This file says how to **choose** a tier,
a difficulty, a track or a tag, and what the folder has to contain.
[CONTRIBUTING.md](../CONTRIBUTING.md) has the contract a submission is graded against.

## Choosing the vocabulary

**tier** — how far into the language a task reaches. Exactly one of three:

| tier | what belongs in it | today |
|---|---|---|
| `core` | the language and its standard library, and every coder needs it: syntax, data structures, files and text, errors, `itertools`, `pathlib` | 186 |
| `advanced` | still the standard library, but you can work a long while without it: `asyncio`, concurrency, generators, decorators, closures, `functools`, the object model past `@property` | 65 |
| `packages` | solving it needs something `pip` installs: `requests`, `responses`, `boto3`, `moto`, `pytest`, `fastapi`, `langchain` | 16 |

Tier answers "can I run this with stock Python?", so `packages` wins whenever a task is both —
an `asyncio` task that stands up a FastAPI app to have something to await is `packages`, not
`advanced`. The test is what **the solution** needs: a library the learner's own code imports,
or that the task is plainly about. Imports below the machinery marker are the grader's and do
not count — 30 tasks `import pytest` down there for `pytest.raises` or `pytest.approx` and are
tiered on the solution, while
`120_fixtures` is `packages` because its `@pytest.fixture` is in the learner's region.

**difficulty** — how hard the task is to get **right the first time**: `easy`, `medium` or
`hard`. It is not how long the task takes. Thirty minutes of unsurprising typing is `easy`; six
lines you can only write once you have seen the trick is `hard`. Anchor the call on the task's
`## Rules` — rules are where the traps live — and grade a new task against the rubric the rest
were graded against: [difficulty-rubric.md](difficulty-rubric.md).
Today: 54 easy · 219 medium · 65 hard.

**track** — one per task: a themed run through the catalogue that cuts across tiers. The home
screen offers each track as a pill, and picking one sets the **focus**. A Python task that names
none is on `python`; the Kubernetes manifests say `track: kubernetes`, the Argo CD ones
`track: argocd`, the Helm charts `track: helm`, the Dockerfiles `track: docker`, the GitHub
Actions workflows `track: github-actions`, and the SQL tasks `track: sql`. Name a track only when
the task belongs to a run other than `python`, and give the run a logo in `web/public/tracks/`.

**tags** — what you practise. Lowercase, kebab-case, 1–3 per task, and one rule decides
every one of them:

> A tag names a **concept you can practise** — never the task's identity, never its story.

`recursion`, `dict-get`, `context-managers` and `bitwise` are tags: each names something you
could sit down and get better at, and something a *future* task could also be tagged with.
`flatten-array`, `phone-screens` and `take-home-task-2` are not. They name one task and could
never name another. The same holds on the infra tracks: `probes`, `multi-stage` and
`layer-cache` are tags, `statefulset` and `distroless` are not; on `sql`, `joins`,
`window-functions` and `constraints` are tags, and `DISTINCT ON` is not. A task never repeats its
track as a tag, since focus and the catalogue already match the track.

Every tag has at least two tasks, and a new tag should arrive with two contrasting contexts.
Contrasting means the same idea solves a different kind of problem, not one task retold
with new nouns. Pair related concepts when one honest task needs both; do not add a tag merely
because its syntax appears incidentally. Reach for an existing tag before minting a synonym —
`sets` not `set`, `strings` not `str-stuff` — and when nothing fits, name the concept, not the
task. `GET /api/catalogue` returns the whole vocabulary under `tags`. `drillion doctor` refuses
a task with more than three tags and a tag no second task carries.

**focus** in `progress.sqlite3` is a single string, and the scheduler matches it against a task's
tier, track and tags alike (`scheduler.py:_facets`): `advanced` and `recursion` are both
valid. It restricts which *new* tasks are offered — reviews and the open catalogue ignore
it — and `POST /api/focus` sets it.

## The folder

One folder per task, `tasks/<NNN>_<name>/`; copy the shape of an existing one.

`<NNN>` is the task's place in the curriculum, `001`–`385` with no gaps, so the next task you add is
`386`. It encodes no difficulty and no provenance, but it does encode order: a task's prereqs are
always numbers below its own, and `doctor` will not let that stop being true. Append, never insert —
inserting means rewriting every number after it, and [ADR-0006](adr/0006-the-fundamentals-come-first.md)
says the two renumberings drillion has had are the last two.

**`README.md`** — YAML frontmatter, then GitHub-flavoured Markdown:

```markdown
---
title: Counter — top N by frequency   # the concept first, then what you build with it
difficulty: medium                    # easy | medium | hard
tier: core                            # core | advanced | packages
track: <run-name>                     # optional, a Python task without one is on `python`
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

Write the keys in that order. `title`, `difficulty`, `minutes` and `tags` are required, and so
is `tier` for a Python task;
no real task carries all eight keys. The title leads with the concept, never with a puzzle name:
Exercism's `bob` is `conditionals — classify a message into one of five replies`, and the puzzle
name survives in the slug and in `source:`. The number is **not** in the frontmatter — it is the
folder's leading digits, and the API exposes it as `topic`. The **spec** is everything from
`# title` up to `## Hints`; extra sections (`## Introduction`, `## Instructions`) may go anywhere
before it. Headings, lists, tables, fenced code, GitHub alerts (`> [!NOTE]`) and images from `assets/`
all render. Mermaid diagrams and video clips do not: no task uses one yet, and
`web/src/ds/SpecText.jsx` says what to add back when one does. For a task adapted from Exercism the
README carries **Exercism's Markdown verbatim** — never trimmed to make room for ours — plus
frontmatter `source:` and a closing attribution line.

`source:` is provenance, and it does not care which half was borrowed. Some sources have no
problem statement at all, only reference implementations: there drillion takes the code and
writes the words, the opposite way round from Exercism. One test covers both directions
([ADR 0009](adr/0009-borrowed-code-is-a-source-like-borrowed-words.md)): if what you borrowed is
a **substantial portion** of what you shipped — their prose as the spec, or their implementation
as `_reference()` — the task carries `source:`, the closing attribution line and a `NOTICE`
entry. If it is not, it carries none of them. Reaching for `graphlib.TopologicalSorter` after
reading someone's topological sort is not an adaptation of it. Code in the CPython documentation
is Zero-Clause BSD and needs no attribution either way; the prose around it is not, so adapt the
example and write the words fresh.

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

## Manifest tasks

A task whose frontmatter says `kind: manifest` asks for a Kubernetes manifest instead of Python.
It takes no `tier`, and its folder holds four files instead of two:

- **`README.md`** — the same frontmatter and sections as any task. `## You return` and `## Rules`
  may name `{placeholders}` from the brief, filled in when a sitting opens; `## Why` and
  `## You get` are shown before one opens, so they may not. A literal brace is doubled, and a
  placeholder is a bare name: no `{name!r}`, `{name:>8}` or `{name.title}`.
- **`task.yaml`** — the learner's whole file. It ships empty.
- **`grade.py`** — `brief(r)` returns a flat mapping of names to strings, numbers or booleans,
  drawn from the `random.Random` it is handed. `check(doc, brief)` asserts on one parsed
  document; a task that asks for several `---`-separated objects defines `check_many(docs,
  brief)` instead, and asserts the document count first. Both run only after the pinned
  kubeconform has accepted the file against the packaged schemas, so they check the task's
  requirements, not the schema. Each assert message is what the learner reads. Anything but an
  `AssertionError` is reported as a grader fault and costs the learner nothing.
- **`solution.yaml`** — the answer key, with each `{placeholder}` a whole YAML value so it keeps
  its type.

A sitting's brief is stored when it opens, and a grader upgraded later keeps grading the brief
it stored: a new `grade.py` must still accept every mapping an older `brief()` could return.
Every rule the README states needs a row in `tests/test_graders.py` that breaks it and fails.

A manifest task may ask for Argo CD's objects too: an Application, ApplicationSet or
AppProject, or Argo Rollouts' Rollout and AnalysisTemplate. Their schemas are generated from
the CRDs at the tags `_schemas/manifest.json` records and packaged beside Kubernetes', so the
same kubeconform run judges both, and a kind with no packaged schema fails `doctor`. Give such
a task `track: argocd`. An ApplicationSet's Go template braces are doubled in `## You return`
and `## Rules`, and a templated value (`'{{.env}}-checkout'`) comes from the brief, so the
answer key's placeholder stays a whole value. A **diagnosis** task puts what `argocd app get`
and `kubectl` printed in `## You get`, written by hand in the tools' shape and saying so, beside
the manifest as git has it; its brief is empty, since the evidence names fixed objects, and
`check()` compares the answer with the fixed manifest.

## Helm tasks

A task whose frontmatter says `kind: helm` is a chart with one file missing, and the learner
writes that file. `edits` names it: `values.yaml` to practise installing a chart, or one
`templates/<name>.yaml` (or a `templates/_<name>.tpl` of helpers) to practise writing one. Everything a manifest task has, it has too, plus
the chart:

- **`chart/`**: `Chart.yaml` and every other file of the chart, shown read-only in tabs beside
  the learner's. `chart/<edits>` must not exist: the learner's `task.yaml` goes there when the
  chart is rendered. A values task can ship a `values.schema.json`, and Helm then refuses a
  misspelt key or a wrong type before anything renders.
- **`grade.py`**: `brief(r)` as for a manifest, and `check(docs, brief, render)`, which runs
  once per render on every document Helm produced (an empty render reaches it as `[]`).
  `render` is `{"release": ..., "values": ...}`, the values being what Helm used: the chart's
  own `values.yaml` with the render's merged over it. A template task also defines
  `renders(brief)`, a list of those two keys, with a different release and different values
  each time, so a template that types in what it should read fails the render that uses
  another. A values task renders once, as `brief["release"]`. A render with a third key,
  `refuses`, is one the chart must stop: it passes only when Helm fails and its message
  contains that text, and `check()` never sees it.
- **`solution.yaml`**: for a values task, the answer key with `{placeholders}`, as for a
  manifest. For a template task, the template itself, served as written: no placeholders,
  since the whole point is that it works for any values.

Each render goes through `helm template`, then `helm lint --strict`, then kubeconform, then
`check()`, and stops at the first that fails. Name the Kubernetes task for the same object in
`prereqs`, and give the task `track: helm`. Every rule the README states needs a row in
`tests/test_helm.py` that breaks it and fails, through the real pipeline.

## Dockerfile tasks

A task whose frontmatter says `kind: docker` is a build context with its Dockerfile missing, and
`edits: Dockerfile`. It has a manifest task's brief and README placeholders, and in place of
the chart:

- **`context/`**: the app the Dockerfile builds, shown read-only in tabs. `context/Dockerfile`
  must not exist. Every `COPY` or `ADD` source that is not `--from` a stage must match a file
  here, or the run names the line and lists what the context holds.
- **`Dockerfile`**: the learner's file, empty.
- **`grade.py`**: `brief(r)` as for a manifest, and `check(stages, brief)`. `stages` is the
  Dockerfile parsed into build stages, each `{"base", "name", "line", "globals", "steps"}`;
  a step is `{"cmd", "args", "flags", "exec", "words", "line"}`, `exec` being the JSON array
  of an exec-form instruction and `None` for shell form, and `globals` the `ARG`s above the
  first `FROM`. `stage.all("RUN")` lists a stage's steps of one instruction. Name the line in
  a message when one line is at fault.
- **`solution.Dockerfile`**: the answer key, filled with `str.format`, so a brace Docker needs,
  `${NAME}`, is written `${{NAME}}`. Why and You get cannot hold a brace at all: write
  `$NAME` there.

A submission goes through hadolint, run with drillion's config (errors and warnings fail,
info is advice, `# hadolint ignore=` is ignored), then the context check, then `check()`.
Nothing is built. Give the task `track: docker`. Every rule the README states needs a row in
`tests/test_docker.py` that breaks it and fails, through the real pipeline.

## Workflow tasks

A task whose frontmatter says `kind: workflow` asks for one GitHub Actions workflow, and
`edits` names where it goes, `.github/workflows/<name>.yml`. Give it `track: github-actions`.
It has a manifest task's brief and README placeholders, and:

- **`workflow.yml`**: the learner's file, empty.
- **`repo/`**: optional, the rest of the repository, shown read-only in tabs: a workflow that
  calls the learner's, a reusable workflow theirs calls, or a document such as the
  environments a repository has. `repo/<edits>` must not exist.
- **`solution.yaml`**: the answer key, rendered like a manifest's, each `{placeholder}` a
  whole value. A value that mixes an expression with a brief value
  (`${{ runner.os }}-pip-...`) comes whole from the brief; `${{ }}` elsewhere is written as
  is. In `## You return` and `## Rules` an expression's braces are doubled for `str.format`;
  Why and You get cannot hold a brace at all.
- **`grade.py`**: `brief(r)` as for a manifest, and `check(workflow, brief)`, where `workflow`
  is the learner's file parsed as GitHub reads it: `on`, `yes` and `off` stay strings, and
  only `true` and `false` are booleans. An event with nothing under it, `pull_request:`, is
  there with the value `None`. Match an action by name at any version
  (`uses.startswith("actions/checkout@")`): a major version is not what a task teaches.

A submission is laid out as a repository with `repo/` and the learner's file at `edits`, and
actionlint lints every workflow in it together, so a caller and the reusable workflow it
calls are checked against each other; any finding fails, and names its file and line. Then
`check()`. Nothing runs, and actionlint's shellcheck and pyflakes integrations are off, since
the image has neither. Every rule the README states needs a row in `tests/test_workflow.py`
that breaks it and fails.

## SQL tasks

A task whose frontmatter says `kind: sql` is a database with a question about it, and
`edits: task.sql`. Give it `track: sql`; `ordered: true` when the row order is part of the
answer, and `explain: true` when `check()` reads the plan. It has a manifest task's brief and
README placeholders, and in place of the chart:

- **`db/schema.sql`**: the tables, shown read-only in tabs and run before every pass. It holds
  no rows: those come from `rows()`. `db/task.sql` must not exist.
- **`task.sql`**: the learner's file, empty.
- **`solution.sql`**: the answer key, filled with `str.format`, so a brace SQL needs (a JSONB
  literal) is written `{{` and `}}`. Why and You get cannot hold a brace at all.
- **`grade.py`**: `brief(r)` as for a manifest, and `rows(r, brief)`, which returns
  `{table: [row, ...]}` with each row a dict of column to value; a date is a `date` or ISO
  string, JSON is a dict or list. Optionally `probes(brief)`, `{sentence: sql}`, where the
  sentence is what the learner reads when the probe disagrees, and `check(result, brief)`,
  where `result` has the learner's `fields`, `rows`, `probes` and, with `explain: true`,
  `nodes`, the plan's node types.

A grade runs four passes on one PGlite: the answer key and then the learner's SQL, each on
the data shown and on a hidden second dataset grown from the same seed. There are three
shapes of task, one model:

- **a query**: the last statement's rows are compared with the answer key's, column names
  and order included, values as Postgres prints them, numbers as decimals;
- **a change to the data**: probes read the tables back afterwards;
- **a schema**: probes read `information_schema` and try the writes each rule is about. A
  probe asks about behaviour, never a name the learner was free to choose, such as a
  constraint's; an expected error agrees on its SQLSTATE alone.

`selfcheck` fails a query task whose answer key returns no rows on either dataset, or the
same rows on both, since that task cannot tell a copied answer from a real one. Every rule
the README states needs a row in `tests/test_sql.py` that breaks it and fails.

## Git tasks

A task whose frontmatter says `kind: git` is a repository in a state, opened in a real
terminal instead of an editor. It takes no `tier` and no `edits`, and its folder holds
`history.sh` (the learner's file: their shell history, empty as shipped) beside `grade.py`
and `solution.sh`:

- **`brief(r)`**: as for a manifest, drawing file names, branch names and the like from the
  `random.Random` it is handed.
- **`setup(repo, b)`**: builds the starting repository, using only `b`, the stored brief, and
  never `r`, since a sitting's repository is rebuilt from its brief alone, on a reload, a
  restore or an upgrade, so `setup` has to be a pure function of it. `repo` is a
  `tasks/_git.py` `Repo` open on `<sitting>/repo`. `repo.commit(message, files, author=None)`
  writes `files` and commits them, each commit a fixed minute after the last from a fixed
  epoch, so the same brief always yields the same SHAs; `repo.origin()` adds a bare
  `origin.git` beside the repository and returns it, and `repo.teammate()` clones `origin`
  again so a task can push "someone else's" commits to it without touching the learner's own
  history, and the clone is deleted once `setup()` returns. `repo.git(*args, check=True)` runs
  anything else: a branch, a stash, a merge left half done.
- **`solution.sh`**: the answer key, a bash script run with `bash -e`, rendered with
  `str.format` like `solution.Dockerfile`, so a literal brace bash needs is doubled (`{{`,
  `}}`). An interactive step is scripted, never left for a human to drive:
  `GIT_SEQUENCE_EDITOR="sed -i ..." git rebase -i` for a rebase, `GIT_EDITOR="..."` for a
  commit message, a file written with `printf` rather than opened in an editor.
- **`SKIP`**: a tuple naming which default probes to drop (`operation`, `refs`, `deleted`,
  `head`, `status`, `stash`): a task about the stash may not care what `HEAD` is.
- **`probes(b)`**: optional, `{sentence: argv}`, a git command's argv run in both repositories
  and compared; `sentence` is what the learner reads when they differ ("the files git
  ignores").
- **`check(repo, b)`**: optional, for a rule no comparison can state, or where the learner's
  own wording is the point (a reworded message, a hand-merged paragraph). It reads
  learner-caused state with `repo.git(..., check=False)` or lets `repo.git(...)`'s own
  `check=True` raise, and raises `AssertionError` for what the learner reads; anything else it
  raises is read as a broken task, not a failed one.

The README's `## You return` gives every commit message in a code span and every file the
learner is meant to type given in full, in a fenced block: a **content id** makes a subject
and a tree's bytes exact, so nothing about what to type is left unsaid. `## You get` describes
the repository the way `git log --oneline --all --graph` would show it, in words, with no
placeholders, since it is shown before a sitting opens. Give the task `track: git`, tags from
the fixed set (`staging`, `commits`, `branches`, `merging`, `conflicts`, `rebase`,
`history-rewriting`, `undo`, `stash`, `remotes`, `history-search`, `tagging`), and no `tier`.

A grade compares the learner's repository with the one the answer key builds from the same
`setup()`: every ref's content id, a ref the key deleted, `HEAD`, the staged and unstaged and
untracked content (`git status --porcelain`, plus each changed path's own staged and unstaged
content by blob id, a non-regular file compared by its type and never opened), an operation
left in progress, and the stash, entry for entry rather than only its count, on the local
repository and on `origin.git` alike. `SKIP` drops a row the task's own rules make redundant, and a task
should turn off no more than it must: the comparison is what catches everything an author did
not think to forbid, and `doctor` prints the git version it found. Every rule the README
states needs a row in `tests/test_git_tasks.py` that breaks `solution.sh` and fails, through
the real pipeline.

## When a new task does not show up

A folder the catalogue cannot read is **skipped**, not reported: a half-written task must never
break the menu for the other 297. That makes a mistake look like a task that simply is not there.
Run `uv run drillion doctor` — it reports every rule the folder breaks, not just the first:

- a required key missing, empty, or misspelt (`tags: []` counts as missing);
- frontmatter that is not a closed `---` block, or is not valid YAML;
- `task.py` with no machinery marker line, or with no `solve()` as the last statement of the
  learner's region, or that does not parse;
- a hint count that is not **exactly 3** — `### Hint 1`, `### Hint 2`, `### Hint 3` under
  `## Hints`.

`uv run drillion selfcheck` splices `_reference` into every file and runs the tests; it must be
green on Python 3.14 before a task is trusted. But it only counts tasks the catalogue already
accepted, so if it still says `385/385` after you added one, `doctor` is where to look.

## Retired tags

Six were retired when the vocabulary landed. If an old branch or an old note still uses one:

| retired tag | where it went |
|---|---|
| `exercism` | `source:` — provenance is a field, not a concept you can practise (109 tasks carry one) |
| `core`, `data-structures` | `tier:` — the coarse grouping is its own key now |
| `whole-task` | `difficulty:` — it marked size, and size is not difficulty |
| `rsample` | retired with the track it named |
| `basics` | `functions` — the concept the tasks actually taught |
