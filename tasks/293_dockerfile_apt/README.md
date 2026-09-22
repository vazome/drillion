---
title: "apt-get in one RUN: update, install, clean up"
difficulty: easy
minutes: 12
prereqs: [290]
track: docker
tags: [image-size]
kind: docker
edits: Dockerfile
---
# apt-get in one RUN: update, install, clean up

*Three commands that every Debian-based Dockerfile gets wrong at least once, and the one line that gets them right.*

## Read first
- [RUN](https://docs.docker.com/reference/dockerfile/#run): one instruction, one layer
- [apt-get best practices](https://docs.docker.com/build/building/best-practices/#apt-get): the pattern this task drills, and why

## Why
A slim image ships without the package lists `apt-get` installs from, so every install starts with `apt-get update`. Put the update in its own `RUN` and it becomes its own cached layer: weeks later a new line is added to the install, the update is taken from the cache, and apt looks for package versions that have left the mirror. Update and install in the same `RUN`, joined with `&&`, and they are always fresh together.

The lists are about 20 MB nobody needs once the install is done. `rm -rf /var/lib/apt/lists/*` removes them, but only in the same `RUN`: a layer is final once its instruction ends, and deleting the files in a later layer only hides them. The image stays as big.

`--no-install-recommends` stops apt from pulling in every package the ones you asked for recommend. On a server that is usually documentation, fonts and half a desktop.

`apt-get` and never `apt`: `apt` is for people at a terminal, and warns that its output may change under scripts. `-y` answers the question nobody is there to answer.

## You get
A build context with `backup.py`, a nightly job that runs `pg_dump` and uploads the dump over HTTPS. It needs two Debian packages the slim image does not have: `postgresql-client` for `pg_dump`, and `ca-certificates` to trust the upload's TLS certificate.

## You return
A Dockerfile that installs exactly those two packages, on Python `{python}`, and runs `backup.py`.

## Rules
- one stage, `FROM python:{python}-slim`
- one `RUN` does all of the apt work: `apt-get update`, then `apt-get install -y --no-install-recommends` with the two packages and nothing else, then `rm -rf /var/lib/apt/lists/*`, joined with `&&`
- no `apt-get upgrade`: a newer base image is how a base image gets upgraded
- the install comes before `backup.py` is copied
- `WORKDIR /app`, and an exec-form `CMD` running `backup.py` with `python`

## Hints
### Hint 1
A long `RUN` is split across lines with a backslash at the end of each one but the last. Each command after the first starts with `&&`, so the whole `RUN` stops at the first one that fails.

### Hint 2
The shape, with the package names left for you:

```dockerfile
RUN apt-get update \
    && apt-get install -y --no-install-recommends ... ... \
    && rm -rf /var/lib/apt/lists/*
```

### Hint 3
What goes wrong with three separate lines:

```dockerfile
RUN apt-get update
RUN apt-get install -y postgresql-client
RUN rm -rf /var/lib/apt/lists/*
```

The first layer is cached forever, the second installs recommends too, and the third deletes files that the first layer still holds. The image is exactly as big as without it.
