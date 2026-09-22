---
title: run as a numbered user, not root
difficulty: medium
minutes: 15
prereqs: [289]
track: docker
tags: [docker, dockerfile, user, security]
kind: docker
edits: Dockerfile
---
# run as a numbered user, not root

*Root inside a container is root on the files it can reach. A container that never needed it should never have it.*

## Read first
- [USER](https://docs.docker.com/reference/dockerfile/#user): which user the following instructions, and the container, run as
- [COPY --chown](https://docs.docker.com/reference/dockerfile/#copy---chown---chmod): who owns what gets copied
- [runAsNonRoot](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/): how Kubernetes checks the user an image runs as

## Why
An image runs as root unless it says otherwise. Root in a container is not root on the host, most of the time, but it is root over every file the container can write, and it is one kernel bug away from more. Most clusters refuse it outright: a pod with `runAsNonRoot: true` will not start an image that runs as root.

There is a catch in how Kubernetes checks. It reads the image's `USER`, and it can only prove a user is not root when the user is a number. `USER app` could be UID 0 for all it knows, so it refuses to start it. Write the number.

The number still wants a name in `/etc/passwd`, because plenty of tools look the current user up and fail when there is none. `useradd` makes one. With a UID as high as a real one, `useradd` also fills a log file with a record for every UID below it, megabytes of zeroes in the image, unless it is given `-l`.

Order matters twice. Everything that needs root, like creating the user, happens before `USER`; every `RUN` after it runs as the new user. And a file copied in belongs to root unless `COPY --chown` says whose it is.

A user that is not root cannot listen on a port below 1024, which is why apps in containers listen on 8080 and not 80.

## You get
The same `app.py` as the first Dockerfile task: a web server that reads its port from `PORT`.

## You return
The first task's Dockerfile, run as UID `{uid}`, on Python `{python}` and port `{port}`.

## Rules
- one stage, `FROM python:{python}-slim`
- a `RUN useradd` creates the user with UID `{uid}`, with `-l` and no home directory
- every `COPY` hands the files to the user with `--chown={uid}:{uid}`
- `USER {uid}`, as a number, after the user exists and after every `RUN`
- `ENV PORT={port}`, `EXPOSE {port}` and an exec-form `CMD` running `app.py`, as before

## Hints
### Hint 1
One new line near the top, one change to the `COPY`, and one new line near the bottom:

```dockerfile
RUN useradd ...
COPY --chown=... app.py .
USER ...
```

### Hint 2
`useradd --uid 12345 --no-create-home --shell /usr/sbin/nologin -l app` makes user `app` with UID 12345 and no way to log in. `--chown` takes `user:group`, and with no group of its own created, the UID stands in for both.

### Hint 3
A finished example, for a different UID:

```dockerfile
FROM python:3.13-slim
RUN useradd --uid 4242 --no-create-home --shell /usr/sbin/nologin -l svc
WORKDIR /srv
COPY --chown=4242:4242 server.py .
USER 4242
CMD ["python", "server.py"]
```

`USER svc` would work with `docker run`, and be refused by a cluster that checks.
