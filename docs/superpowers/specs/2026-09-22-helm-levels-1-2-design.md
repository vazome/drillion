# Helm in drillion: levels 1 and 2

Date: 2026-09-22
Status: built, with ten tasks (279 to 288); level 3 not started
Research: [2026-09-21-helm-support.md](../../research/2026-09-21-helm-support.md)

## Why

Helm is how most teams ship to Kubernetes, and it is a thin layer over objects the learner
has already typed on the `kubernetes` track. What it adds is one contract: a template reads
values, and the values file supplies them. Level 1 trains the values side of that contract,
level 2 the template side. Level 3 (editing both at once) is out of scope here.

## What this is not

- Not a new learning model. Cards, the ladder, hints, gates, notes, the log and focus work as
  they do for manifest tasks.
- Not multi-file editing. The learner edits exactly one file per task, so attempts, the
  archive, backup, reset, etags and ADR 0008 keep their one-file shape. That is what makes
  levels 1 and 2 cheap and level 3 not.
- Not a lab. No terminal, no cluster, no file tree, no creating or renaming files.
- Not `Chart.yaml` authoring. `helm create` writes it, and there is nothing to recall in it.

## The decisions

1. **Helm 4**, pinned by checksum like kubeconform (v4.3.0 today; linux amd64 and arm64 only,
   since #266).
2. **A Helm task is a chart with one hole in it.** The task ships a chart with one file
   missing. The learner's `task.yaml` fills that hole, and frontmatter names which file it is.
   Every other chart file is shown read-only.
3. **Run shows the render.** A Helm Run returns the YAML Helm produced as well as the verdict.
   Edit, render, look is how Helm is really worked, and the render is Helm's version of the
   pytest panel.
4. **Every Helm task builds on a Kubernetes task.** `prereqs` points at the manifest task for
   the same object, and `tags` carries both (`helm`, `deployment`), so focus and the ladder
   join the two tracks.

## Vocabulary

**Chart**: the files a Helm task ships, under `chart/`. Read-only to the learner, graded
exactly as they are.

**Edits**: the chart path the learner's `task.yaml` stands in for, such as `values.yaml` or
`templates/deployment.yaml`. It is set in frontmatter, fixed per task, and it is the label on
the learner's tab.

**Render**: what `helm template` produced from the chart with the learner's file in place.
It is shown on every Run and Submit, and it is the input to kubeconform and `check()`.

The existing words stay: brief, run, submit, grade, and the learner's file is still their
**region** in the sense that it is all they write.

## A task on disk

```
tasks/279_helm_install_values/
  README.md          kind: helm, edits: values.yaml, track: helm, prereqs: [268, 272]
  task.yaml          the learner's file; ships empty
  chart/
    Chart.yaml
    values.schema.json
    templates/deployment.yaml
    templates/service.yaml
  grade.py           brief(r), check(docs, brief, values), optionally renders(brief)
  solution.yaml      the answer key for the edited file
```

For a level 2 task, `edits` is `templates/deployment.yaml` and `chart/values.yaml` is present
and shown. The rule for `doctor`: `chart/<edits>` must **not** exist (the learner provides
it), and `chart/Chart.yaml` must.

The learner's file is `task.yaml` on disk everywhere drillion stores it (the archive, backup,
reset). Only the render step and the tab label use the `edits` path.

## Level 1: use a chart

The learner writes `values.yaml` for a chart they can read but not change.

- **Brief:** the outcome, never the key names. For example: "run `{replicas}` replicas of
  `{image}`, expose it on port `{port}` as a NodePort." Finding which keys produce that is
  the exercise, and it means reading the templates.
- **Render:** once, release name from the brief.
- **Why a schema ships:** without `values.schema.json`, a misspelt key (`replica: 3`) is
  silently ignored and the chart's default renders. The prototype confirmed it. With the
  schema, Helm says `additional properties 'replica' not allowed`. The first level 1 task ships
  a schema, and a later one can ship without one, where `check()` has to catch the silent
  default. That is the most common real mistake when using a chart.
- **Save:** the file is YAML, but save stays size-only like level 2, so one rule covers the
  kind. A broken values file comes back from Helm on Run with its line (`yaml: line 3:
  mapping values are not allowed`), mapped onto the editor.
- **Answer key:** `solution.yaml` with `{placeholders}`, rendered by the existing
  `render_solution`. It is YAML.

First tasks:

| # | Chart renders | Brief asks for | Prereqs |
|---|---|---|---|
| 279 | Deployment + ClusterIP Service | replicas, the image split into repository and tag, service port | 268, 272 |
| 280 | the same chart, NodePort optional | `service.type: NodePort` and a fixed `nodePort` | 273, 279 |
| 281 | Deployment with `resources` passed through `toYaml` | requests and limits as nested values | 279 |
| 282 | a worker chart with no schema and a default on every value | replicas, tag and `env` as strings; a typo renders the default | 270, 279 |
| 283 | Deployment, and a PVC behind `persistence.enabled` | the switch as a real boolean, size and storage class | 277, 279 |

## Level 2: turn a manifest into a template

The learner writes one template against a `values.yaml` they can read. The README shows the
hardcoded manifest being replaced, in the shape the `kubernetes` track taught.

- **Brief:** what the chart must do for any values, such as "the replica count, image and
  name follow the values and the release."
- **Render: at least twice.** A template with `replicas: 3` hardcoded passes a single render
  with `replicas=3`. `renders(brief)` returns each render's release name and values, and they
  differ in every field the task asks the learner to template. `check()` runs on each render.
- **Save:** size only. A template is not YAML (`image: {{ .Values.image }}` fails
  `yaml.safe_load`), so save must not parse it.
- **Answer key:** `solution.yaml` is the template, literal. There are no brief placeholders,
  because the whole point is that it works for any values, and it is never YAML-parsed.

First tasks:

| # | Learner templates | Drills | Prereqs |
|---|---|---|---|
| 284 | `templates/deployment.yaml` | `.Values`, `.Release.Name`, labels that agree | 268, 279 |
| 285 | `templates/configmap.yaml` | `range` over a map, `quote` on every value | 270, 284 |
| 286 | `templates/deployment.yaml` | `toYaml .Values.resources \| nindent 12`, `with` | 281, 284 |
| 287 | `templates/service.yaml` | `if .Values.service.enabled`, `default` | 272, 284 |
| 288 | `templates/secret.yaml` | pipelines: `b64enc` then `quote` | 271, 284 |

286 exists because `indent` against `nindent` is the mistake the validation table showed only
kubeconform catches. 287 is the one where an empty render is correct for one of its renders.

## The `grade.py` contract

The manifest contract, with the render made explicit:

```python
def brief(r):                 # as for manifests: a flat mapping of scalars
    ...

def renders(b):               # optional; level 2 always defines it
    return [
        {"release": b["name"], "values": {"replicas": b["replicas"], "image": b["image"]}},
        {"release": "other", "values": {"replicas": b["replicas"] + 1, "image": "httpd:2.4"}},
    ]

def check(docs, b, render):   # once per render, after Helm, lint and kubeconform accepted it
    # render = {"release": ..., "values": ...}: the values Helm used, the chart's own
    # values.yaml with the render's merged over it
    ...
```

- With `renders` absent (level 1), there is one render: release `brief["release"]`, and
  its values are the learner's file as parsed.
- `docs` is every rendered document, in Helm's order. An empty render reaches `check()` as
  `[]`. The pipeline does not refuse it, because 284 expects one. The authoring guide says
  to assert on the document count first, in the learner's words.
- As for manifests: each assert message is what the learner reads, anything but an
  `AssertionError` is a grader fault that costs no attempt, and a stored brief keeps grading
  after `grade.py` is upgraded.

## Grading

One sandboxed child, as for manifests (`manifest.GRADE_SOURCE` gains a Helm branch, not a
second grader). The chart is copied into scratch, `task.yaml` is written to `chart/<edits>`,
and `HELM_CACHE_HOME`, `HELM_CONFIG_HOME` and `HELM_DATA_HOME` point into scratch. Then, per
render, it stops at the first step that fails:

1. `helm template <release> chart --kube-version 1.34.11 -f <values>`: Go template errors, nil
   pointers, `required`, `values.schema.json`, and values YAML. For level 1 the learner's file
   is itself the values and no `-f` is passed.
2. `helm lint chart --strict --kube-version 1.34.11 -f <values>`: RFC 1123 names, removed
   APIs, Chart metadata. `[ERROR]` and `[WARNING]` lines become diagnostics; `[INFO]` and the
   slog lines are dropped. It runs before kubeconform so a removed API gets Helm's "use
   policy/v1".
3. kubeconform `-strict` on the render: structure, types, duplicate keys.
4. `check(docs, brief, values)`.

A diagnostic that names the edited file gets its line. Helm prefixes paths with the chart
name (`web/templates/z.yaml:1`), so the child strips `<chart name>/` before comparing against
`edits`. A diagnostic in a read-only file has no line and names the file instead: the
learner's values reached a template they cannot change, and the message has to say which.

The result carries `rendered`, the text of the first render, on failure as well as success,
whenever step 1 got far enough to produce it.

**Fingerprint and provenance** add Helm's pin to what judged a pass, next to kubeconform and
the schema digest, under a new prefix (`h1:`), so existing `m1:` fingerprints do not move.

## Editor and page

What the learner sees on a Helm task, top to bottom where it differs from a manifest task:

- **A tab strip over the editor**: `FileTabs` in `web/src/ds/`, drawn in Claude Design from
  [helm-chart-tabs.md](../../design/helm-chart-tabs.md). The learner's file comes first,
  marked "yours"; the others sit under one "Read-only" label. It goes between the Run/Submit
  row and the editor, flush with it (the editor's top corners go square). It stays out of the
  toolbar row because that row wraps and would push the editor down. A note line under the
  strip says what the active file is ("part of the chart, read-only, you write values.yaml"),
  and for a marked file, that the fix goes in the learner's file. Every variant of that line
  shares one grid cell, so switching tabs never moves the editor. The editor wrapper carries
  `role="tabpanel"` and is read-only on every tab but the learner's.
- **Monaco mode** is YAML for every tab. Go template syntax has no standalone Monaco mode
  and gets YAML highlighting. That is acceptable for 2 levels, and worth revisiting only if
  learners trip on it.
- **Result panel:** diagnostics as for manifests, then a collapsible "Rendered" block holding
  `rendered`, open by default on Run and closed on Submit.
- **The track rail** gets a `helm` track. Its logo is already in `web/public/tracks/helm.svg`,
  from devicon v2.16.0 like the others.

Payload: `_payload` adds `chart: [{"path": ..., "text": ...}]` for Helm tasks, in tab order,
and `meta.edits`. `grade.py` and `solution.yaml` are never in it.

## Surface

- `catalogue.py`: `HELM = "helm"`; `REQUIRED_BY_KIND[HELM] = ("edits",)`; `_check_helm`;
  `FILENAMES[HELM] = "task.yaml"`.
- `kinds.py`: `_Helm(_Manifest)`, overriding `validate` (size only), `reference` (placeholder
  render for `values.yaml`, literal otherwise), `revision`, `provenance`, `grade`, `selfcheck`
  (the answer key goes into the hole and must pass every render).
- `manifest.py`: the Helm branch of the child, `job()` carrying the chart, `edits`, renders
  and the Helm binary; `fingerprint` for `h1:`. The existing manifest path is unchanged.
- `tools.py`: `HELM` pins for linux amd64 and arm64. Install by the member's basename, since
  Helm's is `linux-amd64/helm`.
- `api.py`: `chart` and `edits` in the payload; `rendered` through to the Run and Submit
  response.
- `doctor.py`: `KIND_RULES[HELM]`: `edits` names a file that is absent from `chart/`,
  `Chart.yaml` present, level 2 defines `renders`, and the rules for manifest READMEs apply.
- `web/`: `api.ts` kind union and new fields; every `kind === "manifest"` in `Editor.tsx`
  and `Task.tsx` becomes `kind !== "python"`; the Rendered block; the tabs once provided.
- `Dockerfile`: nothing new; `doctor --fetch` picks the pin up.
- Docs: `CONTEXT.md` (the three words above, task counts), `authoring-tasks.md` "Helm tasks",
  an ADR for Helm 4, the pipeline and "one hole per chart".
- Tests: `tests/test_graders.py` rows per README rule, as for manifests; a hardcoded template
  failing the second render is the row every level 2 task needs.

**Schemas:** the ten tasks above render only Deployments, Services, ConfigMaps, Secrets and
PersistentVolumeClaims, which are already packaged, so growing the schema set is not a blocker for these levels. It becomes one for
Ingress, HPA and friends.

**Sandbox:** Landlock already lets the child execute from `tools_dir()` and write to scratch.
The image runs read-only with a `/tmp` tmpfs, and Helm needs neither, as the prototype
showed with a read-only `HOME`. It still needs one run inside the image before merge,
per AGENTS.md.

## Built

The Helm pin, the `_Helm` kind and its grading, `FileTabs` over the editor with the Rendered
block, and all ten tasks, each with a row per rule in `tests/test_helm.py`. The decisions are
recorded in [ADR 0010](../../adr/0010-a-helm-task-is-a-chart-with-one-hole.md).

## Open questions

1. Is `edits` the right frontmatter word? Alternatives: `fills`, `learner_file`.
2. Should level 1 show the rendered output of the chart's *defaults* before the learner types
   anything? It is a free render with no learner input, and it shows what the chart does.
