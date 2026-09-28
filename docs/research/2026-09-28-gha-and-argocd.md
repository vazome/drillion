# GitHub Actions and Argo CD: what it takes

Research, 2026-09-28, reviewed the same day (see the end). The Argo CD design is
[2026-09-28-argocd-track-design.md](../superpowers/specs/2026-09-28-argocd-track-design.md).

## Why

A platform role expects Argo CD (Applications, ApplicationSets, sync waves, progressive
delivery) and GitHub Actions (workflows, environment promotion, release automation). The
catalogue has neither. The Kubernetes, Helm and Docker tracks cover the objects underneath,
so both tracks build on what is already there.

## What was verified (prototype, not guessed)

Every tool below was run under `unshare -rn` (no network) with `HOME=/nonexistent`. That
shows offline feasibility, not that the tool passes a grade: the grader's sandbox
(`sandbox.py`) also sets a scratch `HOME`, resource limits and Landlock, and the image adds
the hardened container of ADR 0011. A run through the real grader in the image is an
acceptance check for each track. Helm and kubeconform are Go binaries that already run there,
which is why actionlint, also Go, is expected to.

| Tool | Offline | Size | Verdict |
|---|---|---|---|
| actionlint v1.7.12 | yes | 6 MB | grade workflow tasks with it |
| Argo CRD schemas, generated from Argo CD v3.5.3 and Argo Rollouts v1.10.0 | yes, through kubeconform | 3.4 MB for five | package them, grade Argo tasks on the manifest kind |
| `argocd` CLI v3.5.3 | partly, see below | 250 MB | authoring time only, never in the image |
| `kubectl argo rollouts lint` v1.10.0 | yes | 142 MB | rejected; its semantic rules are written into `check()` instead |
| `act` | no, needs a Docker daemon | | rejected for the reason ADR 0011 gives |

### actionlint

One broken workflow, five findings, all with line and column, JSON through `-format '{{json .}}'`:

- `runs-on: ubuntu-latst`: unknown runner label, with the valid ones listed.
- `python-versoin` on `actions/setup-python@v5`: input not defined, with the valid inputs. The
  metadata of popular actions is bundled, so this needs no network.
- `echo "${{ github.event.pull_request.title }}"`: potentially untrusted, pass it through `env`.
- `needs: [tset]`: job does not exist.
- `${{ matrix.py }}` in a job without a matrix: property not defined.

It runs shellcheck over `run:` steps when shellcheck is on `PATH`. The image has none today
(hadolint bundles its own), so that is a separate decision. It wants a `.github/workflows/`
directory inside a git repository unless it is given the file path directly; pass the path.

It does not check a composite action's `steps` ("not checked at this point",
[checks.md, v1.7.12](https://github.com/rhysd/actionlint/blob/v1.7.12/docs/checks.md#action-metadata-syntax-validation)),
and it reads an `action.yml` only through a workflow that uses it. A composite-action task is
out until something else can check its body.

### Workflow YAML is not PyYAML's YAML

`yaml.safe_load("on: push\njobs: {}\n")` returns `{True: 'push', 'jobs': {}}`: PyYAML reads
YAML 1.1, where an unquoted `on` is a boolean, and GitHub does not. A workflow kind needs its
own loader that keeps `on`, `off`, `yes` and `no` as strings and `true`/`false` as booleans,
with a test for quoted `on`, unquoted `on` and real booleans. The manifest kind's loader
(`grading.shape`) must not be reused as it is.

### argocd CLI

- `argocd admin settings rbac can <subject> <action> <resource> <object> --policy-file policy.csv`
  answers `Yes` (rc 0) or `No` (rc 1) offline, but only with a KUBECONFIG present. A dummy one
  pointing at `https://127.0.0.1:1` with `user: {token: x}` is enough; with `user: {}` it stops
  and prompts for a username.
- `argocd admin settings rbac validate` checks syntax only: `applicationz` passed as a resource.
- `argocd admin settings resource-overrides health <file> --argocd-cm-path cm.yaml` gives Argo's
  own verdict on a resource with a `status`, offline: `Progressing`, "Waiting for rollout to
  finish: 1 out of 3 new replicas have been updated...".
- `argocd appset generate` needs an Argo CD server ("server address unspecified"). Nothing
  offline expands an ApplicationSet.
- `argocd admin app generate-spec` is offline, but only turns flags into an Application.

### Argo schemas

Generated with kubeconform's `scripts/openapi2jsonschema.py` from the CRDs at the tags,
`DENY_ROOT_ADDITIONAL_PROPERTIES=1` and `FILENAME_FORMAT='{kind}-{group}-{version}'`, so
they land in the packaged set under the names kubeconform's existing
`{{.ResourceKind}}{{.KindSuffix}}.json` template asks for (`application-argoproj-v1alpha1.json`).
No second schema location is needed, and `tools.schema_digest()` covers them because it hashes
the whole folder. Checked with the pinned kubeconform and the grader's own flags:

- a misspelt top-level key (`specc:`) and a misspelt nested one (`selfHeel:`) are refused;
- a file mixing an Application with a ConfigMap validates each against its own schema;
- `setWeight: 150` in a Rollout **passes**: the CRD types it as an integer with no range.
  Argo Rollouts' own validator checks the range, one step type per step, and the selector
  against the template's labels
  ([validation.go, v1.10.0](https://github.com/argoproj/argo-rollouts/blob/v1.10.0/pkg/apis/rollouts/validation/validation.go#L290)).
  A task that teaches steps checks them in `check()`, with a failing row per rule;
- an Application with no `source` passes too (`sources` makes it optional), so `check()` asks.

## Argo CD without its UI

The UI cannot run in drillion: it needs a cluster, the API server, the repo server, the
application controller and Redis.

The job does not hinge on clicking in it. In a GitOps team the UI mirrors git, changes land as
YAML in a pull request, and UI sync is often disabled. What the job needs from the UI is
reading it: sync status (Synced, OutOfSync), health (Healthy, Progressing, Degraded, Missing,
Suspended), the diff, the resource tree and events. drillion drills that reading with
**diagnosis tasks**: the spec shows what `argocd app get` and `argocd app diff` print for a
broken app, and the learner writes the manifest that fixes it. That output is written by hand
as a fixture, in the shape the CLI prints; only a health message produced by
`argocd admin settings resource-overrides health` is the binary's own, and the task says which
is which. No authoring cluster is involved.

**Apply order** (phase, then wave, then kind, then name,
[sync-waves.md, v3.5.3](https://github.com/argoproj/argo-cd/blob/v3.5.3/docs/user-guide/sync-waves.md))
is not a sync plan: Argo also waits for each wave to be healthy and each hook to succeed, a
`Skip` hook is never applied, a selective sync runs no hooks, and pruning runs waves in
reverse. A task that teaches waves states its requirements as waves and says in its messages
what order they give, assuming every earlier wave turns healthy. Nothing on the page claims to
show what a live sync would do.

Clicking through the real UI is an afternoon with `kind` and the Argo CD install manifest,
outside drillion.

## Proposed tracks

**Argo CD, 14 tasks, on the manifest kind** once the Argo schemas are packaged. The list is
in the design.

**GitHub Actions, about 14 tasks, a new kind.** The learner writes one workflow; actionlint,
then `check()` on the workflow parsed with the loader above.

- triggers: `on:`, branch and path filters, `workflow_dispatch` inputs
- `needs:` ordering, `if:` conditions and `failure()`
- matrix with `include` and `exclude`
- caching, artifacts between jobs
- least-privilege `permissions:`, OIDC with `azure/login`
- environments and promotion dev to staging to prod. The task ships a read-only description of
  the environments the repository has and which require a reviewer, and grades the workflow's
  references and job order against it. Required reviewers are a repository setting, not
  workflow YAML
  ([managing environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)),
  so the task says it does not prove an approval is enforced.
- `concurrency:`
- a reusable workflow (`workflow_call`): the caller ships read-only, the learner writes the
  callee, the one-hole shape of ADR 0010
- release on tag, build and push to ACR

## Decided

1. **ApplicationSet expansion.** Nothing offline does it. `check()` grades the generator and
   the template's structure, and that the template reads each parameter it should; no
   expansion is claimed.
2. **Argo RBAC (`policy.csv`).** Only the 250 MB binary evaluates it. Skipped: AppProject roles
   teach the same idea in YAML.
3. **zizmor.** actionlint already flags script injection. Out of the first version.
4. **Composite actions.** Out, as above.

## Also

`tasks/275_statefulset_headless/task.yaml` has held `asfaf` since #252 (cf84a20 added it); it
should be empty like its neighbours. The fix goes in with the first PR of this work.

## Review, resolved

A review on 2026-09-28 raised six findings and two open decisions. All six were accepted:

1. Offline is not the grader: recorded above as feasibility, with a run in the image as the
   acceptance check.
2. Composite actions: out.
3. `on:` under PyYAML: a workflow loader of its own, with its test.
4. Approvals: graded against a shipped description of the environments, and said to be unproven.
5. Rollouts: `setWeight` has no range in the schema; the semantic rules move into `check()`.
6. Apply order is not a sync plan: stated as waves with their assumption, and nothing shows a
   live sync.

The open decisions: diagnosis output is written as fixtures, with any binary-produced message
labelled; the schemas are generated from the tagged CRDs, recorded in `_schemas/manifest.json`
with their sources, and verified through the existing lookup and digest.
