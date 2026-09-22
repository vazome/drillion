---
title: a cache mount, so pip stops downloading the same wheels
difficulty: medium
minutes: 12
prereqs: [290]
track: docker
tags: [docker, dockerfile, buildkit, cache, pip]
kind: docker
edits: Dockerfile
---
# a cache mount, so pip stops downloading the same wheels

*Change one line of requirements.txt and the layer cache throws the whole install away. A cache mount keeps pip's downloads between builds, outside the image, where they cost nothing.*

## Read first
- [RUN --mount=type=cache](https://docs.docker.com/reference/dockerfile/#run---mounttypecache): a directory that survives from build to build
- [Optimize cache usage: use cache mounts](https://docs.docker.com/build/cache/optimize/#use-cache-mounts): the same idea for pip, npm, apt and go

## Why
In 290 you ordered the layers so that an edit to the app reuses the install. That still leaves the other case: a new dependency in `requirements.txt`. The layer is invalid, so pip starts from nothing and downloads every package again, including the forty that did not change. On a laptop that is a minute; in CI, on every branch, it adds up.

pip already has an answer, its download cache in `~/.cache/pip`. It is not used in an image build because every RUN starts from the layer before it, where that directory is empty, and 290 told pip not to write one anyway, so as not to ship it.

A cache mount is a directory BuildKit keeps between builds, mounted into one RUN while it runs and never part of any layer. Mount it where pip keeps its cache and pip finds last build's wheels there, downloads only what is new, and the image stays exactly as small as before. That also makes `--no-cache-dir` wrong here: the cache it was keeping out of the image is no longer in the image, and the flag would stop pip from using the mount at all.

## You get
A build context with a FastAPI app and its `requirements.txt`, open in the tabs above the editor.

## You return
A Dockerfile that installs the requirements with pip's cache kept in a cache mount, on Python `{python}`, served by uvicorn on port `{port}`.

## Rules
- one stage, `FROM python:{python}-slim`; `requirements.txt` copied on its own, and `app.py` copied after the install, as in 290
- one `RUN pip install -r requirements.txt`, with a cache mount at `/root/.cache/pip`
- no `--no-cache-dir` on that install
- `EXPOSE {port}`, and one `CMD` in exec form: `uvicorn` serving `app:app` on host `0.0.0.0` and port `{port}`

## Hints
### Hint 1
The mount is a flag on the RUN itself, before the command:

```dockerfile
RUN --mount=type=cache,target=/some/dir \
    some-command
```

### Hint 2
pip keeps its cache in `~/.cache/pip`, and the build runs as root, so `~` is `/root`.

### Hint 3
The same line for other tools only changes the target: `/root/.npm` for npm, `/root/.cache/go-build` for Go, `/var/cache/apt` for apt. Each package manager has one directory worth keeping.
