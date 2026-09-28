---
title: "release on tag: the tag builds it, the release carries it"
difficulty: medium
minutes: 18
prereqs: [376, 377]
track: github-actions
tags: [releases, artifacts, permissions]
kind: workflow
edits: .github/workflows/release.yml
---
# release on tag: the tag builds it, the release carries it

*Pushing a version tag should be the whole release: the workflow builds what the tag points at, and publishes a GitHub release with those files and notes written from the merged pull requests.*

## Read first
- [Workflow syntax: on.push.tags](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onpushpull_requestpull_request_targetpathspaths-ignore): filter patterns for tags
- [gh release create](https://cli.github.com/manual/gh_release_create): assets and `--generate-notes`

## Why
A release is a tag plus what was built from it. Tying the two in a workflow means nobody builds a release on a laptop, and the files attached to `v2.4.0` are the ones built from `v2.4.0`.

`on.push.tags` filters which tags start the run. `v*.*.*` matches `v2.4.0` and not `v2` or a tag someone pushed by mistake, like `test`.

Build and publish are two jobs, and the build's output reaches the release as an artifact, as in task 376. Only the publishing job needs to write: creating a release needs `contents: write`, so the workflow's token stays at `contents: read` and the `release` job alone raises it.

`gh release create` takes the tag, the files to attach, and `--generate-notes`, which writes the notes from the pull requests merged since the last release. It runs without a checkout, so it is told the repository through `GH_REPO` and the token through `GH_TOKEN`, and the tag reaches the shell through `env` like any other value from a context.

## You get
An empty `.github/workflows/release.yml`. Whatever you type is checked as YAML while you type it, and linted by actionlint when you run it, offline. Nothing is run.

## You return
A workflow named `release`, run when a tag like `v2.4.0` is pushed, with a read-only token, whose job `build` builds the package and uploads `dist/` as `{artifact}`, and whose job `release`, once build is done and with write access to contents, downloads it and creates a GitHub release for the tag with those files and generated notes.

## Rules
- `name: release`, `on` is exactly `push` with `tags: ["v*.*.*"]`, and the workflow's `permissions` is exactly `contents: read`
- two jobs, `build` and `release`, both on `ubuntu-latest`
- `build`'s steps, in order: `actions/checkout` at any version; `run: pip install build`; `run: python -m build`; `actions/upload-artifact` at any version with exactly `name: {artifact}` and `path: dist/`
- `release` has `needs: build` and `permissions` exactly `contents: write`
- `release`'s steps, in order: `actions/download-artifact` at any version with exactly `name: {artifact}` and `path: dist/`; `run: gh release create "$TAG" dist/* --generate-notes`, with exactly three `env` entries, `GH_TOKEN: ${{{{ github.token }}}}`, `GH_REPO: ${{{{ github.repository }}}}` and `TAG: ${{{{ github.ref_name }}}}`

## Hints
### Hint 1
A tag pattern is a glob. Quote it out of habit: a pattern that starts with `*` would otherwise be read as a YAML alias.

```yaml
on:
  push:
    tags: ["v*.*.*"]
permissions:
  contents: read
```

### Hint 2
The job that writes raises its own token, and only its own:

```yaml
  release:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      contents: write
```

### Hint 3
The tag is a context value, so it reaches the shell through `env`:

```yaml
      - run: gh release create "$TAG" dist/* --generate-notes
        env:
          GH_TOKEN: ${{ github.token }}
          GH_REPO: ${{ github.repository }}
          TAG: ${{ github.ref_name }}
```
