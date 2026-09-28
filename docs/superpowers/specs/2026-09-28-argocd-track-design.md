# Argo CD tasks: design

Status: built on `feat/argocd-track`. The research is
[2026-09-28-gha-and-argocd.md](../../research/2026-09-28-gha-and-argocd.md).

## What the learner does

An Argo CD task is a manifest task: the learner writes `task.yaml`, one or more
`---`-separated objects, and it is graded offline. What changes is what they write:
Applications, ApplicationSets, AppProjects, Rollouts and AnalysisTemplates, alongside the
Kubernetes objects those deploy. Where the day job is reading Argo's view of a broken app, a
**diagnosis task** puts that view in the spec, as `argocd app get`, `argocd app diff` and
`kubectl` print it, next to the manifest as it sits in git, and the learner writes the fix.

## What grading can and cannot see

Nothing is synced. There is no cluster, no repo server and no Argo CD. A submission goes
through the same pipeline as every manifest task: shape, the pinned kubeconform against the
packaged schemas, then `check()` or `check_many()`.

- **The schemas** are generated from the CRDs at Argo CD v3.5.3 and Argo Rollouts v1.10.0 with
  kubeconform's `openapi2jsonschema.py` (`DENY_ROOT_ADDITIONAL_PROPERTIES=1`,
  `FILENAME_FORMAT='{kind}-{group}-{version}'`) and packaged beside the Kubernetes ones, so
  the existing lookup finds them and `schema_digest()` covers them. `_schemas/manifest.json`
  records the two tags and the command. A misspelt key anywhere is kubeconform's to refuse.
- **What the schema cannot say is `check()`'s**: an Application's `source` (the schema allows
  `sources` instead), a canary step's weight range, one step type per step, a selector
  against its template. Each of those is a rule in the README and a failing row in
  `tests/test_graders.py`, as for every manifest task.
- **ApplicationSets are not expanded.** `check()` reads the generator and the template, and
  that the template reads each parameter it has to; it never claims to know which
  Applications a controller would make.
- **Waves are stated, not simulated.** A task that teaches waves asks for the annotations,
  and its messages say what order they give, assuming each earlier wave turns healthy.

## How it fits

- No new kind, no new UI. `track: argocd`, logo from devicon v2.16.0 (`argocd-original.svg`).
- Diagnosis evidence is written by hand in the README's `## You get`, in the shape the CLI
  prints, with no braces (doctor's rule for that section). Those tasks have a fixed brief:
  the evidence and the answer name the same objects.
- ApplicationSet templates are Go templates. In `## You return` and `## Rules` their braces are
  doubled for `str.format`; a whole templated value (`'{{.env}}-checkout'`) comes from the
  brief so `solution.yaml` keeps each placeholder a whole value; hints are served raw.

## The tasks (357 to 370)

| # | Task | Drills | Tags |
|---|------|--------|------|
| 357 | first application | an Application: project, source, in-cluster destination, synced by hand | gitops |
| 358 | automated sync | `automated` with `prune` and `selfHeal`, `CreateNamespace`, retry with backoff | sync-policy, drift |
| 359 | a Helm chart as the source | `chart` and a chart version, `releaseName`, `valuesObject`, `ServerSideApply` | values |
| 360 | sync waves | a ConfigMap before the Deployment before the Ingress, waves as strings | sync-waves, multi-document |
| 361 | PreSync migration | a Job hook with a delete policy, on the release's own image | hooks, job |
| 362 | app of apps | a root Application in `argocd` and two children, waves and the finalizer | gitops, sync-waves |
| 363 | a least-privilege project | an AppProject: one repo, a namespace pattern, no cluster resources, quotas kept | security, multi-document |
| 364 | ignore what the HPA owns | `ignoreDifferences` on `/spec/replicas`, `RespectIgnoreDifferences` | drift, sync-policy |
| 365 | ApplicationSet from a list | a list generator, Go templates, `missingkey=error` | generators, templates |
| 366 | ApplicationSet from git directories | directories with an exclude, `.path.basename`, `.path.path` | generators, templates |
| 367 | canary steps | a Rollout: weights and pauses, one indefinite pause to promote by hand | canary, workloads |
| 368 | canary with analysis | an AnalysisTemplate on Prometheus and the Rollout step that runs it | canary, multi-document |
| 369 | diagnose a Degraded app | readiness probe on the wrong path, read from events and logs | troubleshooting, probes |
| 370 | diagnose a failed sync | a PreSync Job at its backoff limit, the wrong database host | troubleshooting, hooks |

## Not now

- A page that shows the apply order, the resource tree or the diff drawn like Argo's UI.
  Each is a UI component to request from the developer, and the text evidence comes first.
- Argo CD's own RBAC (`policy.csv`): only the 250 MB `argocd` binary evaluates it.
- Expanding an ApplicationSet, and a matrix generator, until something offline can check
  what it would produce.
- Running any of it: a sync is a cloud-tier question, as building an image is (ADR 0011).
