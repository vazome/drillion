# Helm support: what it takes

Research, 2026-09-21. Nothing here is built yet. The concept for levels 1 and 2 is
[2026-09-22-helm-levels-1-2-design.md](../superpowers/specs/2026-09-22-helm-levels-1-2-design.md).

## Where we start

Helm was deferred by name in the config-authoring spec
(`docs/superpowers/specs/2026-09-16-config-authoring-design.md`), and the phase-1 plan set the
bar for adding it: a third kind is "a new class in `kinds.py` plus a task-folder convention,
never a seventh pass through the same six modules."

The manifest kind already gives Helm most of what it needs:

- a sandboxed grading child (`manifest.GRADE_SOURCE`) that runs a pinned binary, reads its
  report, then runs the task's `check()`;
- pinned, checksum-verified tools (`tools.py`), fetched by `doctor --fetch` in CI and the
  Docker image;
- packaged Kubernetes 1.34.11 schemas and kubeconform to judge whatever Helm renders;
- briefs generated per sitting and stored on it, specs with `{placeholders}`.

## What was verified (prototype, not guessed)

Run in the scratchpad against Helm v4.3.0 (latest, 2026-09-09):

- **Offline works.** `helm template` on a local chart under `unshare -rn` (no network) with a
  read-only `HOME` and `XDG_*` rendered fine. No cache or config dir needed for `template`.
- **DNS is off by default.** `getHostByName` rendered `""`; it needs `--enable-dns` to resolve.
- **`--kube-version 1.34.11`** is accepted, so `.Capabilities` matches our packaged schemas.
- **Rendered output pipes straight into kubeconform** with the existing schema location.
- **Template errors name the learner's line:** `parse error at (web/templates/bad.yaml:2):
  missing value for if`. That maps onto the editor the way pytest's `task.py:12` does now.
- **Size.** `helm-v4.3.0-linux-amd64.tar.gz` is 20 MB (under `MAX_ARCHIVE`, 64 MB); the binary
  is 66 MB unpacked. That lands in every Docker image and every CI `doctor --fetch`.
- **Checksums.** `get.helm.sh` publishes `<archive>.sha256sum` per platform, as `.tar.gz` for
  linux amd64 and arm64 (the only platforms drillion runs on since #266). Same shape as
  kubeconform. The binary's
  own sha256 is ours to compute, as today.

## Validation: who catches what

Each case below was written as a template and put through all three validators with Helm
4.3.0, kubeconform `v0.8.0-drillion.3` and the packaged 1.34.11 schemas.

| Mistake | `helm template` | kubeconform `-strict` | `helm lint --strict` |
|---|---|---|---|
| Template syntax (`{{ if }}`) | error, file:line | n/a | error |
| Nil pointer (`.Values.nope.deeper`) | error, file:line:col | n/a | error |
| `required "..."` / `fail` | error with the author's message | n/a | **warning only**, then a follow-on name warning |
| Value fails `values.schema.json` (type, `additionalProperties`, pattern; draft 2020-12 works) | error: `at '/replicas': got string, want integer` | n/a | error |
| `toYaml \| indent 2` where `nindent 4` belongs (valid YAML, wrong nesting) | passes | **catches**: `at '/metadata': additional properties 'a' not allowed` | passes |
| `replicas: {{ .Values.replicas \| quote }}` | passes | **catches**: `got string, want null or integer` | passes |
| Duplicate key | passes | **catches**: `key "name" already set` (PyYAML silently keeps the last one) | passes |
| Removed API (`policy/v1beta1` PDB on 1.34) | passes | "could not find schema", which our message blames on spelling or a packaging gap | **catches**: `deprecated in v1.21+, unavailable in v1.25+; use policy/v1` |
| `metadata.name: Bad_Name` (RFC 1123) | passes | **passes** (the schema has no rule for it) | **catches** |
| Chart.yaml `version: one` | error | n/a | error, clearer |
| Everything wrapped in `{{ if false }}` (renders nothing) | passes, empty output | passes: "0 resources found" | passes |

What this means:

- **No single validator is enough.** `template` catches Go and values errors, kubeconform
  catches structure and types, and `lint` catches naming and removed APIs. Each has cases only it
  catches.
- **Order matters for the message.** Run `lint` before kubeconform, so a removed API gets
  Helm's "use policy/v1" instead of our "check the spelling" text.
- **An empty render must be our own check.** Every tool passes it. `shape()` already refuses an
  empty file; for Helm it should say "the template rendered nothing with these values."
- **The RFC 1123 gap affects the existing manifest tasks too.** kubeconform accepts
  `Bad_Name`, and a real cluster refuses it. Today a manifest task only catches it if its
  `check()` asks for an exact name. This is worth a separate issue.
- **`lint` output is text only**: no JSON flag in v4.3.0. The lines have the form
  `[ERROR|WARNING|INFO] <file>: <message>`, and Helm 4 also writes slog lines
  (`level=WARN msg=...`) to stderr. Keep ERROR and WARNING, drop INFO (`icon is recommended`
  fires on every chart).
- **`lint` renders with the chart's own `values.yaml` unless given `-f`/`--set`.** Lint each
  value set the grade renders, or the brief's values are never linted.
- **Out of scope, on purpose:** `--dry-run=server` and `--disable-openapi-validation` need a
  cluster. The client dry-run that `template` uses validates nothing against OpenAPI offline.

### The schema set has to grow

`helm create`'s own scaffold renders a ServiceAccount, Service, Deployment, HPA, Ingress, a test
Pod and an HTTPRoute. kubeconform fails it straight away on `could not find schema for
ServiceAccount`. We package 10 kinds today. Helm tasks will realistically need at least
ServiceAccount, HorizontalPodAutoscaler, Ingress, Role/RoleBinding, NetworkPolicy and
PodDisruptionBudget. HTTPRoute is a Gateway API CRD, missing from the core schema repo
entirely. Either leave it out of tasks or package its CRD schema on purpose. This change goes
through `_schemas/manifest.json` and the schema digest, so it also changes the manifest
fingerprint (`m1:`) for existing tasks. It needs its own small PR first.

### Other validators, considered and not recommended

These are from general knowledge; I did not run them against Helm 4 here.

- **kubeval**: superseded by kubeconform, which we already pin.
- **chart-testing (`ct lint`)**: wraps `helm lint` plus yamllint and a Chart.yaml schema.
  It assumes a git repo of charts. Heavy for grading one template.
- **kube-linter / kube-score / Polaris**: best-practice policy (resource limits,
  `runAsNonRoot`, probes). Useful teaching content, but they are opinions, not validity. A
  task that wants "must set limits" writes that as a `check()` assert, which is the spec's
  existing line on policy grading (conftest/Rego deferred for the same reason).
- **helm-unittest plugin**: YAML-written template tests. It does the same job as `check()`
  in Python, and it would add Helm 4's plugin install path to the sandbox.

### A task shape the validators make possible

`values.schema.json` is enforced by `template` and `lint` alike, with messages worth reading.
"Write the schema that rejects these values and accepts those" is a single-file JSON task
graded by Helm itself. It is a good fit for a later task after the template tasks.

## What breaks if we just reuse `manifest`

1. **A template is not YAML.** `image: {{ .Values.image }}` fails `yaml.safe_load` (flow
   mapping). `_Manifest.validate` would refuse to *save* the learner's draft.
2. **The answer key collides.** `render_solution` fills `{name}` placeholders and then
   YAML-parses the result. A Helm solution is a template, so the parse fails.
3. **Archive member is in a subdirectory.** Helm's is `linux-amd64/helm`
   `acquire` writes to `scratch / pin.member` and installs at
   `tools_dir() / pin.member`, so both paths gain a directory that does not exist. Install by
   the member's basename instead.
4. **Fingerprint and provenance** name kubeconform only. A Helm verdict is also Helm's.

## How a learner works with Helm

Helm wraps Kubernetes objects the learner already knows, so every Helm task builds on a
Kubernetes task through `prereqs`. "Template a Deployment" requires 268 (first Deployment).
Tags carry both (`helm`, `deployment`), so a focus on `deployment` offers both kinds of task,
and the ladder reviews the object's shape through either one.

The real Helm loop is edit, render, look, lint. It maps onto drillion's own:

- **Run** (free) renders with the task's values and shows the output YAML plus any errors.
  That render is the Helm version of the pytest output panel.
- **Submit** runs the full pipeline below and grades.

Decided: **Helm 4** (v4.3.0 at time of writing). Image size is not a concern: the Helm binary
is baked in by `doctor --fetch` like kubeconform.

## What the learner works on, by difficulty

| Level | Learner edits | Shown read-only | Drills |
|---|---|---|---|
| 1. Use a chart (easy) | `values.yaml` | the template | reading a template, the values contract |
| 2. Turn a manifest into a template (medium) | one template | `values.yaml` | `.Values`, `.Release`, `toYaml \| nindent`, `if`, `required` |
| 3. Change both sides (hard) | template + `values.yaml` (maybe `values.schema.json`) | nothing else | keeping the two in agreement, e.g. an optional Ingress |
| 4. Named templates (later) | adds `_helpers.tpl` | | `define`, `include` |

The learner never writes `Chart.yaml`: `helm create` generates it, and there is nothing to
recall in it. A `values.schema.json` task ("reject these values, accept those") also fits
level 3 and is graded by Helm itself.

**Levels 2 and up need more than one render.** A template that hardcodes `replicas: 3` passes a
single render with `replicas=3`. `grade.py` defines `values(brief) -> [dict, ...]`, and
`check(doc, brief, values)` runs on each render.

### Tabs, not a file tree

Harder tasks show a tab strip, one tab per file (the UI component is requested from the
developer, per AGENTS.md). What keeps this a drill and not a KodeKloud lab:

- the task fixes the files, 2 or 3 at most; the learner never creates, renames or deletes one;
- read-only files are visibly locked;
- no terminal, no cluster, no VM: grading takes seconds, is exact and runs offline;
- the task comes back on the ladder.

Tabs yes, a file tree no. A task that wants the learner to explore a directory has become a lab.

## Phases

1. **Schemas.** Package the kinds Helm tasks will render (ServiceAccount, HPA, Ingress,
   Role/RoleBinding, NetworkPolicy, PDB). This PR stands alone because it moves the manifest
   fingerprint.
2. **Levels 1 and 2.** The Helm kind with one editable file, read-only tabs for the rest, and
   the rendered output on Run. Attempts, the archive, backup, reset and etags keep their
   one-file shape.
3. **Level 3**, once levels 1 and 2 have been used. This makes a task's learner artifact a small
   map of fixed filenames to text, which touches the archive, backup, etag, reset and ADR 0008
   ("an upgrade keeps the region"). That is the real cost here, not the tab strip.

## Surface for phase 2

- `catalogue.py`: `HELM` kind, required keys, folder check (`README.md`, `grade.py`, the
  solution, `chart/Chart.yaml`, `chart/values.yaml`, the learner file), filename.
- `kinds.py`: `_Helm`, most of it inherited from `_Manifest`; overrides `validate` (no YAML
  parse on a template), `reference` (the solution is literal, no placeholder fill),
  `provenance`/`revision`.
- `manifest.py`: one grading child with render and lint steps before `shape()`: copy the chart
  into scratch, drop the learner file in place, run the pipeline below with `HELM_*_HOME`
  pointed at scratch. Map `(<file>:<line>[:<col>])` to a diagnostic with a line. The
  fingerprint adds the Helm pin.
- `runner.py` / `api.py`: Run returns the rendered YAML for the Helm kind.
- `tools.py`: `HELM` pins for linux amd64 and arm64, install by basename. `report()` already loops pins.
- `sandbox.py`: `tools_dir()` is already exec and scratch is already writable under Landlock.
  Needs one run inside the read-only image.
- `doctor.py`: `KIND_RULES[HELM]`.
- Web: `api.ts` kind union; `Editor.tsx` ext and file name; `Task.tsx` reference fence, editor
  height and "Validator details" label (all currently `=== "manifest"`, so they become "not
  python"); the rendered-output panel; the read-only tabs. The track rail on this branch
  picks up a `helm` track from task frontmatter.
- Docs: `CONTEXT.md` task counts and kind wording, `authoring-tasks.md` Helm section, an ADR
  recording Helm 4, the validator pipeline and "tabs, not a file tree".
- Tests: `tests/test_graders.py` rows per README rule, as for manifests.

## Grading pipeline

Per value set that `grade.py` asks for:

1. `helm template <release> <chart> --kube-version 1.34.11 -f <values>`: Go template, nil and
   `required` errors, `values.schema.json`.
2. Refuse an empty render in our own words.
3. `helm lint --strict --kube-version 1.34.11 -f <values>`: RFC 1123 names, removed APIs,
   Chart metadata. ERROR and WARNING lines become diagnostics; INFO is dropped. It runs before
   kubeconform so a removed API gets Helm's message and not ours.
4. kubeconform `-strict` on the render: structure, types, duplicate keys.
5. `check(doc, brief, values)` on the parsed documents: the task's requirements. This is the
   grade; steps 1 to 4 are the floor.

On save, only the size is checked: a template is not YAML, and step 1 is where its errors are
worth reading.

## Separate issue

kubeconform accepts `metadata.name: Bad_Name` and a real cluster refuses it. The existing
manifest tasks have this gap today, independent of Helm.
