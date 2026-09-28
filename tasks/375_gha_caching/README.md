---
title: "caching: a key that changes exactly when the dependencies do"
difficulty: medium
minutes: 15
prereqs: [374]
track: github-actions
tags: [caching, matrix]
kind: workflow
edits: .github/workflows/ci.yml
---
# caching: a key that changes exactly when the dependencies do

*Every job starts on a clean machine and downloads every dependency again. A cache keeps the download between runs, and its key decides when it is stale.*

## Read first
- [Dependency caching reference](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching): `key`, `restore-keys`, and what a hit means
- [Expressions: hashFiles](https://docs.github.com/en/actions/reference/workflows-and-actions/expressions#hashfiles): a hash of the files that decide the dependencies

## Why
`actions/cache` saves a folder at the end of a job under a **key**, and restores it at the start of the next job that asks for the same key. The whole design is the key: it has to change exactly when the cached content would.

pip's downloads depend on three things, so the key is built from three things. The operating system, `runner.os`, since a wheel built for Linux is no use on Windows. The Python version, `matrix.python`, since wheels differ per version. And the lockfile, through `hashFiles`, which hashes its content: change one pinned version and the hash changes, so the key misses and the cache is rebuilt.

A missed key does not have to start from nothing. `restore-keys` lists prefixes to try when the exact key misses, and the most recent cache that matches one is restored: yesterday's cache for the same system and Python, with one package out of date, beats downloading all of them.

## You get
An empty `.github/workflows/ci.yml`. Whatever you type is checked as YAML while you type it, and linted by actionlint when you run it, offline. Nothing is run.

## You return
A workflow named `CI`, run on every push, whose job `test` runs for Python 3.13 and 3.14 on `ubuntu-latest` and caches pip's downloads under a key of the system, the Python version and a hash of `{lock}`, falling back to the newest cache for the same system and version.

## Rules
- `name: CI`, `on: push` with nothing under it, and exactly one job, `test`, on `ubuntu-latest`
- `strategy.matrix` is exactly `python: ["3.13", "3.14"]`
- the steps, in order: `actions/checkout` at any version; `actions/setup-python` at any version with exactly `python-version: ${{{{ matrix.python }}}}`; `actions/cache` at any version; `run: pip install -r {lock}`; `run: pytest`
- the cache step's inputs are exactly `path: ~/.cache/pip`, `key: {key}` and `restore-keys: {restore}`

## Hints
### Hint 1
`hashFiles` takes a path pattern and returns a hash of the matching files' content:

```yaml
          key: ${{ runner.os }}-pip-${{ matrix.python }}-${{ hashFiles('requirements.txt') }}
```

### Hint 2
A restore key is a prefix: the key up to, and including, the last dash before the hash.

```yaml
          restore-keys: ${{ runner.os }}-pip-${{ matrix.python }}-
```

### Hint 3
The cache step goes after Python is set up and before anything installs, so the install finds what it restored:

```yaml
      - uses: actions/cache@v6
        with:
          path: ~/.cache/pip
          key: ...
          restore-keys: ...
      - run: pip install -r requirements.txt
```
