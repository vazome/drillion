---
title: "multi-stage: build with Go, ship only the binary"
difficulty: medium
minutes: 18
prereqs: [291]
track: docker
tags: [multi-stage, image-size]
kind: docker
edits: Dockerfile
---
# multi-stage: build with Go, ship only the binary

*The compiler is 800 MB. The program it makes is 7. Only one of them needs to reach production.*

## Read first
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/): several FROMs, and copying between them
- [distroless](https://github.com/GoogleContainerTools/distroless#why-should-i-use-distroless-images): images with the app and its runtime, and nothing else

## Why
Building needs a toolchain: the Go compiler, its module cache, git, a shell. Running needs none of it. A Dockerfile with one `FROM golang` ships all of it, and every CVE scanner in the company will list what it finds in there.

A multi-stage build has several `FROM` lines. Each starts a new stage from scratch, and only the last one becomes the image. `COPY --from=build` reaches back into an earlier stage and takes just what it names, so the build stage does the compiling and the final stage receives the binary and nothing else.

A Go binary built with `CGO_ENABLED=0` is static: it carries everything it needs and runs on an empty filesystem. That makes the runtime stage almost nothing. `scratch` is literally empty. `gcr.io/distroless/static` adds only CA certificates, timezone data and a non-root user, 65532, which its `:nonroot` tag switches to for you. Neither has a shell, so nothing in the final stage can `RUN`, and neither can an attacker who gets in.

## You get
A build context with `go.mod` and `main.go`, an HTTP service with no dependencies outside the standard library, listening on 8080.

## You return
A two-stage Dockerfile that builds the service with Go `{go}` into a binary called `{name}`, and ships only that binary.

## Rules
- the first stage is `FROM golang:{go} AS build`, and builds with one `RUN` of `go build` with `CGO_ENABLED=0`, writing the binary with `-o` to a path ending in `/{name}`
- the second stage is `gcr.io/distroless/static-debian12:nonroot`, or `scratch` with a numeric `USER`
- the second stage copies the binary alone `--from` the build stage, and has no `RUN`
- `ENTRYPOINT` runs the binary by its path, in exec form

## Hints
### Hint 1
Two blocks, each starting with a `FROM`. The first has `WORKDIR`, the copies and the build; the second has one `COPY --from`, and the `ENTRYPOINT`.

### Hint 2
`CGO_ENABLED=0 go build -o /out/name .` builds the package in the current directory into `/out/name`. The variable written before the command applies to that command only. Adding `-trimpath -ldflags="-s -w"` makes the binary smaller and free of your build machine's paths.

### Hint 3
The same pattern for a different binary:

```dockerfile
FROM golang:1.25 AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /out/tool ./cmd/tool

FROM scratch
COPY --from=build /out/tool /tool
USER 65532
ENTRYPOINT ["/tool"]
```

The runtime stage has no shell, so the entrypoint must be the exec form: there is no `/bin/sh` to run a string.
