# A workflow task is linted, never run

Continuous integration is where most teams meet their platform every day: the workflow that
tests a pull request, builds an image, and deploys it through environments. The question was
how to grade a GitHub Actions workflow inside a read-only container with every capability
dropped, under Landlock, with no network and no Docker daemon.

The research is [docs/research/2026-09-28-gha-and-argocd.md](../research/2026-09-28-gha-and-argocd.md),
and the design is
[docs/superpowers/specs/2026-09-28-gha-track-design.md](../superpowers/specs/2026-09-28-gha-track-design.md).

## Considered options

**Run it with `act`.** Rejected, for the reason ADR 0011 gives for building images: `act`
runs each job in a Docker container, which needs a daemon and the network, and a verdict would
take minutes. Seeing a workflow run belongs in a cloud tier.

**The manifest kind with a workflow JSON schema.** Rejected. A schema says a key is allowed,
not that `needs: [tset]` names a job that exists, that `python-versoin` is not an input of
`actions/setup-python`, or that an issue title in `run` is a script injection. And the
manifest kind parses with PyYAML, which reads an unquoted `on:` as the key True.

**actionlint, then `check()`.** Taken. actionlint is one static Go binary of 6 MB with
published checksums, pinned the same way as hadolint. It checks the syntax, every expression
against the contexts it can reach, runner labels, the inputs of popular actions from metadata
it bundles, and untrusted input in scripts, all offline. Given a repository root, it reads a
caller and the reusable workflow it calls together, and refuses an input, secret or output
that does not line up. Then the task's own `check(workflow, brief)` reads the workflow parsed
as GitHub parses it.

## Consequences

- **A seventh kind, `workflow`**, on the manifest kind's brief and answer key. The learner's
  file is `workflow.yml`, placed at `edits`, `.github/workflows/<name>.yml`, and a task may
  ship the rest of the repository under `repo/`, shown in the chart's tabs.
- **Its own YAML loader.** `grading.WorkflowLoader` keeps `on`, `off`, `yes` and `no` as
  strings and only `true` and `false` as booleans. A task's `check()` never sees PyYAML's
  YAML 1.1.
- **A grade lays the repository out fresh** in the sandbox's scratch directory, with an empty
  `.git` as actionlint's project root, so `./.github/workflows/` paths resolve.
- **shellcheck and pyflakes are off** (`-shellcheck= -pyflakes=`): actionlint runs them only
  when they are on `PATH`, the image has neither, and a verdict must not depend on the host.
- **A passing workflow has never run.** Whether an environment really requires a reviewer is
  a repository setting no file can show; a task that teaches environments says so, and grades
  the names and the order.
- **A composite action is not a task yet**: actionlint does not check a composite action's
  `steps`.
- **The verdict is fingerprinted `w1:`**: the grader's files, the actionlint pin, and the
  flags it runs with.
