# Config authoring in drillion

Date: 2026-09-16
Status: design approved in chat, awaiting written review

## Why

drillion teaches Python by making people type it out against a grader that changes its data
every sitting. The same pressure applies to configuration languages, and nothing teaches
them: people learn Kubernetes by copying a manifest from a wiki, changing two fields, and
never once writing `readinessProbe` from memory. The skill this design targets is narrow and
physical: recall the shape, recall where it nests, type it correctly, from nothing.

Kubernetes first. Docker second. Helm and the rest come later and are out of scope here.

## What this is not

- Not a cluster. Nothing is deployed, nothing is applied, no daemon runs.
- Not a rewrite. The ladder, cards, attempts, hints, gates, notes, archive, log, focus and
  scheduler are untouched. This adds a second task kind to the catalogue.
- Not Helm, kustomize, Terraform, Compose or CI YAML. Those are later tracks that reuse
  whatever this establishes.
- Not a linting course. `kubeconform` passing is a floor, never the grade.

## The four decisions

1. **Real tools grade it.** `kubeconform` decides whether the manifest is a legal Kubernetes
   object, not a hand-written approximation of the schema.
2. **Both install lines get the same grading.** `drillion doctor` fetches the binaries at a
   pinned version and checksum. The pip and clone paths do not become second class.
3. **The seed generates the brief.** The requirements the learner reads change every sitting,
   so yesterday's manifest cannot be pasted back.
4. **The learner opens an empty file.** No marker, no skeleton, no holes to fill.

## Vocabulary

Added to `CONTEXT.md`:

**Kind**: What language a task is written in: `python` or `manifest`. A task's kind decides
which grader runs, which file the learner edits, and what the editor highlights.
_Avoid_: type, format, language, mode.

`tier` is not extended. It means how far into the Python language a task reaches, and a
Kubernetes task reaches nowhere into it. Config tasks carry `kind: manifest`, a `track`
(`kubernetes`), and ordinary tags (`deployment`, `probes`, `resources`, `configmap`).

**Focus** needs no change at all: it already matches tier, track and tags alike, so
`focus: kubernetes` narrows new picks to this track from the first task.

**Brief** is not a new word. The generated requirements are the task's **spec**, which is
already defined as "the guidance a task shows you: Why / You get / You return / Rules". The
only change is that for `kind: manifest` the spec is rendered per attempt instead of served
verbatim.

## A task on disk

```
tasks/271_first_deployment/
  README.md       frontmatter carries kind: manifest; "You return" holds {placeholders}
  task.yaml       the learner's, entirely. Ships empty.
  grade.py        brief() and check(). Never served to the browser.
  solution.yaml   the gated solution, and selfcheck's input
```

Compared with a Python task, `task.py` splits into three files: the learner's half becomes
`task.yaml`, the grader's half becomes `grade.py`, and the reference answer becomes
`solution.yaml`. The marker line, the cut and the splice all disappear for this kind, because
a YAML file cannot carry Python below a comment.

`grade.py` living outside the learner's file is a small improvement on the Python kind, where
`_reference` sits in the same file and is readable by anyone who scrolls.

## The `grade.py` contract

Two functions, the direct analogues of today's `_gen` and `_reference`:

```python
SERVICES = ["checkout", "billing", "search", "ingest"]

def brief(r):
    """The requirements for one sitting, from the attempt's seeded Random."""
    name = r.choice(SERVICES)
    return {
        "name": name,
        "namespace": r.choice(["payments", "platform", "web"]),
        "replicas": r.randint(2, 5),
        "image": f"ghcr.io/acme/{name}:1.{r.randint(0, 9)}.{r.randint(0, 9)}",
        "port": r.choice([8080, 8443, 9090]),
        "probe_path": r.choice(["/healthz", "/ready", "/live"]),
        "memory": r.choice(["256Mi", "512Mi", "1Gi"]),
    }

def check(doc, b):
    """`doc` is the learner's YAML, parsed. Assert it meets `b`."""
    assert doc["kind"] == "Deployment"
    assert doc["metadata"]["name"] == b["name"]
    assert doc["spec"]["replicas"] == b["replicas"], "replicas"
    container = doc["spec"]["template"]["spec"]["containers"][0]
    assert container["image"] == b["image"]
    probe = container["readinessProbe"]["httpGet"]
    assert probe["path"] == b["probe_path"]
    assert probe["port"] == b["port"]
```

`check` uses plain `assert` on purpose: the run goes through pytest, so the existing
`_headline`, `summarise` and `printed` machinery renders a failed assertion for a manifest
exactly as it renders one for Python, with no new panel and no new formatting code.

There is no `render` function. The README keeps its ordinary `## You return` section with
`{placeholders}`, and the API fills it with `str.format(**brief)` when it serves the spec. The
brief stays where every other task's spec already lives, and an author writes prose rather
than string-building code.

## The seeded spec

Today `api._payload` serves `meta["spec_md"]` verbatim. For `kind: manifest` it serves
`meta["spec_md"].format(**brief(rng(seed)))`, with the seed taken from the open attempt, the
same seed `runner.run_tests` already receives. An unopened task has no attempt and therefore
no seed, so the catalogue preview renders one throwaway brief purely so the card is readable
from the browser; it is replaced the moment the attempt opens.

A literal brace in a manifest task's README has to be doubled. That is a real authoring
footgun, and `catalogue._read` rejects a `kind: manifest` README whose `format` call raises,
so the task never reaches the menu with a broken spec.

## Grading

`runner.run_tests` gains a manifest branch. It writes into the scratch directory that already
exists, then calls the same `_run_pytest` that Python tasks use:

1. Copy the learner's `task.yaml` into the scratch directory.
2. Write a generated `_check.py` there, holding the seed and importing the task's `grade`.
3. `_run_pytest` runs it under the existing sandbox, timeout and case capture.

The generated test is small and fixed:

```python
def test_manifest():
    out = subprocess.run([KUBECONFORM, "-strict", "-schema-location", SCHEMAS,
                          "-output", "json", "task.yaml"],
                         capture_output=True, text=True)
    assert out.returncode == 0, _readable(out.stdout)
    doc = yaml.safe_load(Path("task.yaml").read_text())
    grade.check(doc, grade.brief(rng(SEED)))
```

Consequences worth stating plainly, because they are the reason for this shape:

- `summarise`, `_headline`, `printed`, the 60s timeout, the case capture and every sandbox
  tier work with no change.
- A schema error and a missed requirement arrive in the learner's output panel through the
  same path, so the browser needs no new failure rendering.
- `kubeconform -output json` is parsed down to the message and the path before it becomes an
  assertion message, because its raw JSON is not something to read in a panel.

`-strict` is not optional: without it a manifest with a misspelled field is valid, and
misspelled fields are most of what a learner gets wrong.

## The region

`region.py` currently assumes Python everywhere: `bounds` finds the marker, `cut` splits at
it, `_solve` finds the function, `stub` rebuilds the signature, `validate` parses an AST.
None of that applies.

For `kind: manifest` the rules are:

- `validate`: the text is not empty and `yaml.safe_load` parses it. Nothing else. A learner is
  free to lay the document out however they like.
- `stub`: the empty file. Passing a task resets `task.yaml` to empty, the same way passing a
  Python task resets it to the signature.
- `etag` and `revision`: hash the whole file. There is no machinery half to hash separately,
  so `revision` hashes `grade.py` instead, which keeps the recorded "which grader did this
  pass meet" promise intact.

Roughly thirty lines beside the Python ones, dispatched on kind. The Python functions do not
move and do not change.

## Acquiring the tools

`drillion doctor` gains a tools section. For each tool it needs, it reports one of: present
and verified, missing, or checksum mismatch.

- Pinned by version and SHA256 per platform, in a table in `settings.py`.
- Downloaded into `<root>/tools/<name>`, never into the repo and never onto `PATH`.
- Verified on every run, not only at download, because a silently swapped grader is worse
  than a missing one.
- The Kubernetes JSON schemas ship as package data rather than being downloaded, so the only
  network call ever made is for the binary itself.

When a tool is missing, a `kind: manifest` task does not fail red. The task page says the
grader is not installed and names the command to fix it. A learner must never be shown a
failing test that is not about their answer.

`docker run` users have the tools baked into the image, so the fetch never happens there.

## Sandbox

Less work than feared. `sandbox.py:252` already makes `/usr/bin` and `/bin` executable on
purpose, because task 033 grades `subprocess.run` on `echo`, and `guard.py` states that
subprocess stays open at every tier. Executing a foreign binary is an existing, deliberate
capability rather than a new hole.

What changes:

- Landlock: `_roots` gains `<root>/tools` with `_EXEC` rights.
- macOS: the same path joins the SBPL profile's readable set in `_sbpl`.
- Windows: the restricted token confines writes and not reads or exec, so nothing changes.
- guard: nothing changes.

Landlock denies TCP outright, and that stays denied. `kubeconform` validates against the
local schema directory and needs no network, which is the whole reason the schemas ship as
package data.

## Editor

Monaco already carries YAML and Dockerfile grammars through
`@codingame/monaco-vscode-standalone-languages`, which is already a dependency. The editor
picks its language from the task's file extension. No new dependency, no new build step.

The Python language server is not wired to YAML. A learner gets highlighting and bracket
handling, not completion. That is acceptable for a first release and is the honest position
anyway: completion would do the recalling that this feature exists to train.

## selfcheck

`runner.selfcheck()` solves every task with its own `_reference` and is the reason a
270-task catalogue can be trusted. A manifest task has no reference function to auto-solve
with, so without `solution.yaml` every config task silently leaves the safety net.

With it, selfcheck for a manifest task is: for several seeds, render the brief, grade
`solution.yaml` against it, and expect green. This catches the failure mode that actually
matters, which is a `brief` that can generate requirements its own `solution.yaml` cannot
satisfy.

`solution.yaml` therefore earns its place twice, because it is also the gated **solution**
the glossary already defines, served by the existing `/api/task/{slug}/solution`.

A solution written for one brief cannot literally satisfy another, so `solution.yaml` holds
the same `{placeholders}` as the README and is formatted with the same brief.

## Backup

`backup.py` writes regions as `<slug>.py` and reads them back by that suffix. A manifest task
restored through that path would be dropped without a word, which is data loss in the one
feature whose entire job is not losing data. The stored name takes the task's real extension,
and the reader accepts both. Old backups contain only `.py` entries and keep working.

## Phases

Each phase ends with something that runs.

1. **One task, end to end.** `kind` in the frontmatter, the catalogue branch, the region
   rules, the doctor fetch, the sandbox path, the seeded spec, the runner branch, the editor
   language, and exactly one task: `271_first_deployment`. Nothing is authored in volume
   until a learner can open that one task, type a Deployment, and be told precisely which
   requirement they missed.
2. **selfcheck, solution and backup.** The safety net and the reverse states, before there is
   enough content for their absence to hurt.
3. **The Kubernetes batch.** Pod, Deployment, Service, ConfigMap, Secret, Ingress, PVC, Job,
   CronJob, HPA, probes, resources, labels and selectors. Authoring, not engineering.
4. **Docker.** A second tool in the same machinery: `hadolint` for sanity, asserts on the
   parsed instructions for the brief. `hadolint` runs with no Docker daemon and no Docker at
   all, which is why it is chosen over `docker build --check`, which needs buildx and would
   re-break the install path phase 1 protects.

## Risks

- **A generated brief that no manifest satisfies.** The one genuinely new failure mode.
  Phase 2 is what catches it, which is why it comes before volume.
- **Authoring cost per task is higher than a Python task.** Four files instead of two, and a
  brief that has to vary without becoming nonsense. If this proves too heavy in phase 3, the
  answer is a shared `brief` helper library under `tasks/_lib`, not abandoning the seeding.
- **A stale pin.** A pinned binary eventually stops matching a schema release. `doctor` says
  which version it has, and the pin is a normal dependency bump.
- **Brace escaping in READMEs.** Mitigated by rejecting an unformattable spec at scan time.

## Deferred, deliberately

- Helm, kustomize, Compose, Terraform, CI YAML.
- Multi-document manifests, and tasks spanning more than one file.
- Any language server or schema completion for YAML.
- `docker build` actually building, which needs a daemon.
- Grading by policy, for example conftest and Rego. It would express requirements more
  precisely than `check()` and costs the author a second language to learn. Revisit only if
  `check()` proves genuinely insufficient.
