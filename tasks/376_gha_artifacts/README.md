---
title: "artifacts: build once, hand the result to the next job"
difficulty: medium
minutes: 15
prereqs: [373]
track: github-actions
tags: [artifacts, needs]
kind: workflow
edits: .github/workflows/package.yml
---
# artifacts: build once, hand the result to the next job

*Jobs share nothing: each starts on its own clean machine. An artifact is how one job's output reaches another, and it means the thing you check is the thing you built.*

## Read first
- [Store and share data with workflow artifacts](https://docs.github.com/en/actions/tutorials/store-and-share-data): uploading, downloading, and retention

## Why
A job that builds a package and a job that checks or publishes it run on two different machines, so nothing the first wrote to disk exists for the second. Building again in the second job is worse than slow: it publishes something nobody tested.

`actions/upload-artifact` stores files from a job under a `name`. `actions/download-artifact` in a later job fetches them by that name into a `path`. The later job has to `needs` the first, or it may start before there is anything to download.

Artifacts cost storage, and a build's output is only interesting for a few days. `retention-days` deletes it after that many days, instead of the repository's default of up to ninety.

## You get
An empty `.github/workflows/package.yml`. Whatever you type is checked as YAML while you type it, and linted by actionlint when you run it, offline. Nothing is run.

## You return
A workflow named `package`, run on every push, whose job `build` builds the package and uploads `dist/` as `{artifact}` for {days} days, and whose job `check` downloads that same artifact once build is done and checks it with twine.

## Rules
- `name: package`, `on: push` with nothing under it, and exactly two jobs, `build` and `check`, both on `ubuntu-latest`
- `build`'s steps, in order: `actions/checkout` at any version; `run: pip install build`; `run: python -m build`; `actions/upload-artifact` at any version with exactly `name: {artifact}`, `path: dist/` and `retention-days: {days}`
- `check` has `needs: build`, and its steps, in order: `actions/download-artifact` at any version with exactly `name: {artifact}` and `path: dist/`; `run: pipx run twine check dist/*`
- `check` does not check the code out or build anything itself

## Hints
### Hint 1
The upload names what it stores, and says how long to keep it:

```yaml
      - uses: actions/upload-artifact@v7
        with:
          name: wheel
          path: dist/
          retention-days: 5
```

### Hint 2
The download asks for the same name, and puts the files where the next step expects them:

```yaml
  check:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v8
        with:
          name: wheel
          path: dist/
```

### Hint 3
A glob in `run` is the shell's, so `dist/*` reaches twine as every file in the folder.
