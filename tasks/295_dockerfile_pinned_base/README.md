---
title: pin the base image by digest, and label where it came from
difficulty: easy
minutes: 12
prereqs: [292]
track: docker
tags: [security, labels]
kind: docker
edits: Dockerfile
---
# pin the base image by digest, and label where it came from

*A tag is a name that can be pointed somewhere new tomorrow. A digest is the content itself.*

## Read first
- [Pin base image versions](https://docs.docker.com/build/building/best-practices/#pin-base-image-versions): tags move, digests do not
- [OCI annotations](https://github.com/opencontainers/image-spec/blob/main/annotations.md#pre-defined-annotation-keys): the label keys every registry understands

## Why
`python:3.13-slim` is rebuilt every time Debian ships a security fix, and the tag moves to the new image. That is convenient, and it means two builds of the same commit a week apart are built on different bases. When one of them breaks, nothing in the Dockerfile says what changed.

A digest pins the content. `python:3.13-slim@sha256:` followed by 64 hex digits names one exact image, and the builder refuses anything that does not hash to it. The tag stays in front for the humans reading it, and so that tools like Renovate or Dependabot know what to bump the digest to. The trade is that security fixes now arrive when the digest is bumped, not by themselves: pinning without a bot to bump it is how images go stale.

Labels go the other direction: they tell whoever finds the image where it came from. `org.opencontainers.image.source` is the repository, and GitHub, GitLab and most registries link a package to its code by that key. `org.opencontainers.image.revision` is the commit, which only the pipeline running the build knows, so it arrives as a build argument.

## You get
The same `app.py` as the first Dockerfile task. There is no registry to pull from here, so the digest to pin is given to you.

## You return
A Dockerfile built on `python:{python}-slim` pinned to the digest `{digest}`, labelled with its source repository `{repo}` and the commit it was built from.

## Rules
- one stage, built `FROM python:{python}-slim@sha256:{digest}`
- `LABEL org.opencontainers.image.source="{repo}"`
- `ARG REVISION`, with no default, and `LABEL org.opencontainers.image.revision` set from it
- `WORKDIR /app`, `COPY app.py .`, and an exec-form `CMD` running `app.py`

## Hints
### Hint 1
The digest goes after the tag, joined with an `@` and prefixed with the algorithm: `image:tag@sha256:<digest>`.

### Hint 2
`LABEL` takes `key="value"` pairs, several on one instruction with a backslash between lines. A build argument is read as `${NAME}` in a label, as anywhere else, once an `ARG` has declared it in the stage.

### Hint 3
A finished example for a different image:

```dockerfile
FROM node:22-slim@sha256:9d7b9f3c0f3e1c5a2b8e4d6f7a1c3e5b7d9f1a3c5e7b9d1f3a5c7e9b1d3f5a7c
ARG REVISION
LABEL org.opencontainers.image.source="https://github.com/example/web" \
      org.opencontainers.image.revision="${REVISION}"
```

The pipeline builds it with `docker build --build-arg REVISION=$(git rev-parse HEAD) .`
