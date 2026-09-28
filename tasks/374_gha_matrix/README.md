---
title: "matrix: one job, every Python and every operating system"
difficulty: medium
minutes: 15
prereqs: [371]
track: github-actions
tags: [matrix]
kind: workflow
edits: .github/workflows/ci.yml
---
# matrix: one job, every Python and every operating system

*A library supports several Pythons on several systems. A matrix writes the job once and runs it for every combination, minus the ones you rule out, plus the ones you add.*

## Read first
- [Running variations of jobs in a workflow](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations): `matrix`, `include`, `exclude` and `fail-fast`

## Why
`strategy.matrix` turns one job into many. Each key under it is a list, and GitHub runs the job once for every combination of their values: two operating systems and three Pythons are six jobs. Inside the job, `matrix.os` and `matrix.python` hold the values of the combination being run, so `runs-on` and `python-version` read them.

Not every combination is wanted. `exclude` lists combinations to drop, each written as the keys and values to match. `include` adds combinations the lists do not produce, such as one run on macOS with only the newest Python: an entry that would overwrite a value of every existing combination becomes a combination of its own.

By default the first failing job cancels all the others, which hides whether the failure is one platform or all of them. `fail-fast: false` lets every combination finish.

## You get
An empty `.github/workflows/ci.yml`. Whatever you type is checked as YAML while you type it, and linted by actionlint when you run it, offline. Nothing is run.

## You return
A workflow named `CI`, run on every push, whose one job `test` runs on Ubuntu and Windows with Python 3.12, 3.13 and 3.14, except Windows with {skipped}, plus once on macOS with 3.14, and lets every combination finish.

## Rules
- `name: CI`, and `on: push` with nothing under it
- exactly one job, `test`, with `runs-on: ${{{{ matrix.os }}}}`
- `strategy.fail-fast: false`
- `strategy.matrix.os` is exactly `[ubuntu-latest, windows-latest]`, and `strategy.matrix.python` exactly `["3.12", "3.13", "3.14"]`, as strings
- `strategy.matrix.exclude` is exactly one entry, `os: windows-latest` with `python: "{skipped}"`
- `strategy.matrix.include` is exactly one entry, `os: macos-latest` with `python: "3.14"`
- the steps, in order: `actions/checkout` at any version; `actions/setup-python` at any version with exactly `python-version: ${{{{ matrix.python }}}}`; `run: pytest`

## Hints
### Hint 1
The matrix sits under `strategy`, beside `fail-fast`:

```yaml
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        python: ["3.12", "3.13", "3.14"]
```

### Hint 2
`exclude` and `include` are lists of combinations, each a small map:

```yaml
        exclude:
          - os: windows-latest
            python: "3.12"
        include:
          - os: macos-latest
            python: "3.14"
```

### Hint 3
The job reads its combination through the `matrix` context:

```yaml
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: ${{ matrix.python }}
```
