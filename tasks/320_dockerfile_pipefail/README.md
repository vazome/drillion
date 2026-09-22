---
title: "SHELL with pipefail: a failed download fails the build"
difficulty: medium
minutes: 15
prereqs: [293]
track: docker
tags: [shell]
kind: docker
edits: Dockerfile
---
# SHELL with pipefail: a failed download fails the build

*`curl URL | something` is in half the Dockerfiles you will ever read. Without one setting, the shell judges that line by the last command alone, and forgets the download.*

## Read first
- [SHELL](https://docs.docker.com/reference/dockerfile/#shell): the shell every later RUN is handed to
- [hadolint DL4006](https://github.com/hadolint/hadolint/wiki/DL4006): set pipefail before a RUN with a pipe
- [Installing Helm from a binary release](https://helm.sh/docs/intro/install/#from-the-binary-releases): the tarball and what is inside it

## Why
A pipeline's exit status is the status of its last command. In `curl URL | tar -xz`, that is tar's, and curl's failure counts for nothing. Here tar happens to fail too when it is fed nothing, so the build stops, with an error about gzip that sends you looking at the wrong command. Pipe into something content with empty input, like `sh`, `tee` or `gpg --dearmor`, and there is no error at all: the step succeeds, the layer is cached, and the image ships without what it was supposed to download.

`set -o pipefail` changes the rule for every pipe: the pipeline fails if any command in it fails. In a Dockerfile the setting goes on the shell itself, with the `SHELL` instruction, and applies to every RUN after it. `/bin/sh` in many base images does not accept `-o pipefail`, so the shell named is bash, which every Debian image has.

Half of the fix is curl's. Without `-f`, curl treats a 404 as a successful download of an error page, exits 0, and pipes the HTML on. With `-f` it exits non-zero on any HTTP error, and pipefail passes that on.

## You get
A build context with `deploy.sh`, the script this image runs, open in the tab above the editor.

## You return
A Dockerfile for a deploy image: Debian with Helm `{helm}` downloaded from its release tarball, running `deploy.sh`.

## Rules
- one stage, `FROM debian:bookworm-slim`
- `SHELL ["/bin/bash", "-o", "pipefail", "-c"]`, before any RUN that pipes
- curl installed with `apt-get`, in a RUN of its own before the download
- one RUN that downloads `https://get.helm.sh/helm-v{helm}-linux-amd64.tar.gz` with `curl -f` and pipes it into `tar`, extracting only `linux-amd64/helm` into `/usr/local/bin`
- `COPY deploy.sh /usr/local/bin/deploy.sh`, and `ENTRYPOINT ["deploy.sh"]`

## Hints
### Hint 1
`SHELL` takes the shell and its options as an exec-form array, and the last one is `-c`, which is how the RUN's text is handed over:

```dockerfile
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
```

### Hint 2
The tarball holds a folder, `linux-amd64/`, with `helm` inside. `--strip-components=1` drops that folder from the path as it extracts, and naming the one member extracts nothing else:

```dockerfile
RUN curl -fsSL https://example.com/tool.tar.gz \
    | tar -xz -C /usr/local/bin --strip-components=1 linux-amd64/tool
```

### Hint 3
The apt install is the one from 293, with `curl` and `ca-certificates` in it. Without the certificates curl cannot check the HTTPS server it downloads from.
