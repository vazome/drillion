# A Helm task is a chart with one hole in it

Helm is how most teams ship to Kubernetes, and it is a thin layer over the objects the
`kubernetes` track already drills. What Helm adds is one contract: a template reads values, and
a values file supplies them. The question was how much of a chart a learner should write in one
sitting, and how a chart is graded when drillion has no cluster.

The research is [docs/research/2026-09-21-helm-support.md](../research/2026-09-21-helm-support.md),
and the design is
[docs/superpowers/specs/2026-09-22-helm-levels-1-2-design.md](../superpowers/specs/2026-09-22-helm-levels-1-2-design.md).

## Considered options

**The learner writes a whole chart.** Rejected for now. Every place drillion keeps a learner's
work (attempts, the archive, backup, reset, and ADR 0008's upgrade rule) holds one file per
task. A chart is several files, so this would change all of them, and it would also make the
learner type `Chart.yaml`, which `helm create` writes and which has nothing in it to recall.

**The learner writes one file of a chart the task ships.** Taken. `edits` in the frontmatter
names that file, `values.yaml` or one template, and the learner's `task.yaml` is dropped into
the chart at that path when it is rendered. Everything that keeps a learner's work still sees
one file. Writing `values.yaml` for someone else's chart is how most people meet Helm, and
writing one template against a `values.yaml` they can read is how they start writing charts.
Editing both at once is the next level up, and it is what would justify multi-file tasks.

**One validator.** Rejected: each of them catches something the others miss. Tried on the same
mistakes, `helm template` catches Go template, nil-pointer, `required` and `values.schema.json`
errors. kubeconform catches YAML that parses but nests wrong, a number rendered as a string,
and duplicate keys. `helm lint --strict` catches names Kubernetes refuses (RFC 1123) and APIs
removed from the pinned Kubernetes version. So a render goes through all three, in that
order, then `check()`, and stops at the first that fails. Lint runs before kubeconform so a
removed API gets Helm's "use policy/v1" rather than kubeconform's "could not find schema".

**Helm 3.** Rejected. Helm 4 is the current release and what a new learner installs, and the
template language drillion teaches is the same in both. The pin is checksummed the same way as
kubeconform's and moves the same way.

## Consequences

- **A template task renders more than once.** A template with `replicas: 3` passes one render
  whose values say 3. `renders(brief)` in `grade.py` gives a different release and different
  values each time, and `tests/test_helm.py` holds every template task to it.
- **`check()` sees the values Helm used**: the chart's own `values.yaml` with the render's
  merged over it, as `helm template -f` merges them.
- **A Helm verdict is fingerprinted `h1:`**, adding Helm's pin to kubeconform's and the
  schemas', so no existing `m1:` fingerprint moved.
- **The kinds a chart renders must be packaged schemas.** The first ten tasks render only
  Deployments, Services, ConfigMaps, Secrets and PersistentVolumeClaims. A task that renders an
  Ingress or an HPA has to package that schema first.
- **The page shows the chart in tabs**, the learner's file first and the rest read-only, and a
  Run shows what Helm rendered. This is the edit, render, look loop Helm is really used
  with, and it is why the tab strip stops at the files the task ships: no file tree and no
  new files, so a task stays a drill and does not turn into a lab.
