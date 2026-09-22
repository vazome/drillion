---
title: "ENTRYPOINT and CMD: the program and its default arguments"
difficulty: medium
minutes: 15
prereqs: [289]
track: docker
tags: [docker, dockerfile, entrypoint, cmd, signals]
kind: docker
edits: Dockerfile
---
# ENTRYPOINT and CMD: the program and its default arguments

*One names what the container is. The other says how it runs when nobody says otherwise.*

## Read first
- [ENTRYPOINT](https://docs.docker.com/reference/dockerfile/#entrypoint): and the table of how it combines with CMD
- [Kubernetes command and args](https://kubernetes.io/docs/tasks/inject-data-application/define-command-argument-container/): which one each field overrides

## Why
`ENTRYPOINT` and `CMD` are joined into one command line when a container starts: the entrypoint first, then the cmd. Anything after the image name in `docker run` replaces the `CMD` and keeps the `ENTRYPOINT`. So the program goes in `ENTRYPOINT`, and its default arguments in `CMD`: `docker run worker --queue other` runs the same program on a different queue, with nobody retyping `python worker.py`. Kubernetes maps them the same way, `command` over `ENTRYPOINT` and `args` over `CMD`.

Both have to be in exec form, the JSON array. A shell-form `ENTRYPOINT` runs under `/bin/sh -c`, and then two things break at once. The shell is PID 1, and `docker stop` sends SIGTERM to PID 1, so the app never hears it and is killed ten seconds later mid-job. A shell-form `ENTRYPOINT` also ignores `CMD` completely, arguments and all.

The worker here drains its current job when SIGTERM arrives. That only works when it is PID 1.

## You get
A build context with `worker.py`, a queue consumer that takes `--queue` and `--concurrency` on its command line and exits cleanly on SIGTERM.

## You return
A Dockerfile, on Python `{python}`, whose container runs `worker.py` on the queue `{queue}` with a concurrency of `{concurrency}` unless told otherwise.

## Rules
- one stage, `FROM python:{python}-slim`, with `WORKDIR /app` and `worker.py` copied in
- one `ENTRYPOINT`, in exec form, running `worker.py` with `python` and nothing else
- one `CMD`, in exec form, holding only the arguments: `--queue {queue} --concurrency {concurrency}`
- every option and every value is its own string in the array

## Hints
### Hint 1
Two arrays. The first is the program: `["python", "worker.py"]`. The second is everything the program is given.

### Hint 2
`--concurrency 4` on a command line is two words, so it is two strings: `"--concurrency", "4"`. The number is a string too: an exec-form array holds nothing but strings.

### Hint 3
The same split for a different tool:

```dockerfile
ENTRYPOINT ["redis-server"]
CMD ["--port", "6380", "--appendonly", "yes"]
```

`docker run redis-image --port 7000` keeps `redis-server` and drops the rest of `CMD`, so appendonly is back to its default. That is the contract: `CMD` is replaced whole.
