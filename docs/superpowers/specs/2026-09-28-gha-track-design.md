# GitHub Actions tasks: design

Status: built on `feat/gha-track`, stacked on `feat/argocd-track`. The research is
[2026-09-28-gha-and-argocd.md](../../research/2026-09-28-gha-and-argocd.md), and the
decision is [ADR 0014](../../adr/0014-a-workflow-task-is-linted-never-run.md).

## What the learner does

A workflow task is one GitHub Actions workflow with the repository around it. The learner
writes `workflow.yml`, which the grader places at the path `edits` names. A task may ship the
rest of the repository under `repo/`, shown read-only in the tabs a Helm chart uses: the
workflow that calls a reusable one, the reusable one a release calls, the environments a
repository has, a security report.

## What grading can and cannot see

Nothing runs: there is no runner, no Docker daemon and no network. A submission goes through:

1. **actionlint v1.7.12**, pinned by checksum, over every workflow in a repository laid out
   fresh in scratch (`repo/`, the learner's file at `edits`, an empty `.git` as the project
   root), with `-shellcheck= -pyflakes=`. Any finding fails, with its file and line, so the
   editor marks the learner's line and a finding in a shipped caller marks its tab.
2. **`check(workflow, brief)`**, on the learner's file parsed by `WorkflowLoader`: `on` is the
   key `on`, and only `true` and `false` are booleans. `unset` is not applied, since an event
   with nothing under it is null and still on.

Actions are matched by name at any version. The answer keys use the current majors
(`actions/checkout@v7`); for the few actionlint v1.7.12 has no metadata for yet, `check()` is
what reads their inputs.

## How it fits

- A seventh kind, `workflow`, a `_Manifest` subclass beside `_Docker`: `workflow_job`,
  `workflow_fingerprint` (`w1:`), `grade_workflow`, doctor's `_workflow_rules`, and the web's
  maps (`FENCE`, `FILE`, `CHECKS`, `TABS`, `LOOK`, the archive's judge line).
- Track `github-actions`, logo from devicon v2.16.0 (`githubactions-original.svg`).
- The image smoke test counts `workflow.yml` as a learner file; trivy skips `tasks/*/repo`,
  as it skips `tasks/*/chart`.

## The tasks (371 to 385)

| # | Task | Tags |
|---|------|------|
| 371 | first workflow: push and pull request, checkout, setup-python, pytest | triggers |
| 372 | path filters in a monorepo, and `workflow_dispatch` with a choice input | triggers, inputs |
| 373 | `needs` and `if`: lint, test, deploy only on a push to main | needs, expressions |
| 374 | a matrix with `exclude`, `include` and `fail-fast: false` | matrix |
| 375 | `actions/cache` with a key of system, Python and a lockfile hash | caching, matrix |
| 376 | artifacts from a build job to a check job | artifacts, needs |
| 377 | least-privilege `permissions`, and a job block that replaces the workflow's | permissions, security |
| 378 | OIDC to Azure and a deploy to AKS, IDs in `vars`, no secret | permissions, azure, environments |
| 379 | dev, staging, production environments with URLs and concurrency | environments, needs, concurrency |
| 380 | workflow concurrency that cancels pull requests and never main | concurrency, expressions |
| 381 | a reusable workflow with inputs, a secret and an output, its caller shipped | reusable-workflows, inputs |
| 382 | calling a reusable deploy twice, and granting the permissions it needs | reusable-workflows, needs |
| 383 | build and push to ACR with OIDC, Buildx and the `gha` cache | azure, caching, releases |
| 384 | a GitHub release on a version tag, with the built files | releases, artifacts, permissions |
| 385 | fixing a script injection from a shipped security report | security, expressions |

## Not now

- Composite actions: actionlint does not check their `steps`.
- zizmor as a second checker: actionlint already refuses untrusted input in `run`.
- Drawing the job graph GitHub shows, matrix legs expanded: a UI component to request.
- Running any of it: a cloud-tier question.
