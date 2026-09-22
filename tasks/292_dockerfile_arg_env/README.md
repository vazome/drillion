---
title: "ARG or ENV: build time, run time, or both"
difficulty: medium
minutes: 15
prereqs: [289]
track: docker
tags: [docker, dockerfile, arg, env]
kind: docker
edits: Dockerfile
---
# ARG or ENV: build time, run time, or both

*Some values only matter while the image is built, some only while it runs, and one of them has to cross from one to the other.*

## Read first
- [ARG](https://docs.docker.com/reference/dockerfile/#arg): build arguments, and where each one is visible
- [How ARG and FROM interact](https://docs.docker.com/reference/dockerfile/#understand-how-arg-and-from-interact): the ARG that lives above FROM
- [ENV](https://docs.docker.com/reference/dockerfile/#env): variables the running container sees

## Why
`ARG` is a variable of the build. `docker build --build-arg NAME=value` sets it, it has a default in the Dockerfile, and it is gone when the build ends: the running container never sees it. `ENV` is a variable of the image. Every later instruction sees it, and so does every process in every container started from it.

A CI pipeline stamps the version it is building into the image: it knows the version at build time, so that is an `ARG`. The app wants to report the version while it runs, so the value has to be handed on to an `ENV`. `ENV APP_VERSION=$APP_VERSION` does exactly that. Hardcoding the version in the `ENV` would ignore whatever the pipeline passed.

The one place an `ARG` goes above `FROM` is to choose the base image. Declared there, it is visible to the `FROM` lines and nowhere else; the stage below starts without it. That is how one Dockerfile builds against several Python versions.

Settings like a log level belong only to the running app, and an operator changes them with `docker run -e` or a Kubernetes `env:` without rebuilding. They are plain `ENV`. Never pass a secret either way: both end up readable in the image's history.

## You get
A build context with `app.py`, which reads `APP_VERSION` and `LOG_LEVEL` from its environment when it starts, and fails without them.

## You return
A Dockerfile whose Python version and app version are build arguments, defaulting to `{python}` and `{version}`, and whose log level is `{level}`.

## Rules
- `ARG PYTHON_VERSION={python}` above `FROM`, and `FROM python:${{PYTHON_VERSION}}-slim`
- `ARG APP_VERSION={version}` inside the stage, handed on with `ENV APP_VERSION=${{APP_VERSION}}`
- `ENV LOG_LEVEL={level}`, and no `ARG` for it
- `WORKDIR /app`, `COPY app.py .`, and an exec-form `CMD` running `app.py`

## Hints
### Hint 1
Three kinds of line: an `ARG` above `FROM`, an `ARG` below it, and an `ENV` that reads the second one. `${NAME}` reads a variable in a Dockerfile, as it does in a shell.

### Hint 2
One `ENV` can set several variables. The backslash continues it on the next line:

```dockerfile
ENV APP_VERSION=${APP_VERSION} \
    LOG_LEVEL=...
```

### Hint 3
The same shape with other names:

```dockerfile
ARG NODE_VERSION=22
FROM node:${NODE_VERSION}-slim
ARG BUILD_SHA=dev
ENV BUILD_SHA=${BUILD_SHA} \
    NODE_ENV=production
```

`docker build --build-arg NODE_VERSION=24 --build-arg BUILD_SHA=4f2a9c1 .` builds on Node 24 and stamps the commit; the defaults are what you get without them.
