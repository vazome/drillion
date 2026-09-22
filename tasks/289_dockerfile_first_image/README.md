---
title: your first Dockerfile
difficulty: easy
minutes: 10
track: docker
tags: [cmd]
kind: docker
edits: Dockerfile
---
# your first Dockerfile

*An image is a filesystem and a command. A Dockerfile is the recipe for both, one instruction at a time.*

## Read first
- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/): every instruction, and what it adds to the image
- [Shell and exec form](https://docs.docker.com/reference/dockerfile/#shell-and-exec-form): why `CMD` takes a JSON array

## Why
Every image starts `FROM` another one. For a Python app that is an official `python` image, and the tag says which Python and how much else comes with it: the `-slim` variants leave out compilers and manuals nobody needs at runtime, and are a fraction of the size.

After `FROM`, each instruction adds a layer. `WORKDIR` makes a directory and moves into it, so everything after it has a place to land. `COPY` brings files in from the build context, the folder the build was started in. `ENV` sets a variable every process in the container sees. `EXPOSE` records which port the app listens on; it opens nothing, but it tells the next reader which port matters, and it is the port `docker run -P` publishes. `CMD` is what runs when the container starts.

`CMD` has two spellings. The JSON array, called exec form, runs the program directly. The plain string, shell form, runs it inside `/bin/sh -c`, and the shell becomes the process that receives `docker stop`. Use the array.

drillion does not build your image: there is no Docker engine inside it. It lints your Dockerfile with hadolint, checks every file you copy is in the build context, and then checks the requirements below.

## You get
A build context holding `app.py`, open in the tabs above the editor, and an empty `Dockerfile`. The app is a small web server that reads the port to listen on from the `PORT` variable.

## You return
A Dockerfile for the app on Python `{python}`, listening on port `{port}`.

## Rules
- one stage, `FROM python:{python}-slim`
- `WORKDIR /app`, before anything is copied
- copy `app.py` alone, not the whole context
- `PORT` is set to `{port}` with `ENV`, and the same port is the one `EXPOSE` names
- one `CMD`, in exec form, running `app.py` with `python`

## Hints
### Hint 1
Five instructions do all of it, in this order: `FROM`, `WORKDIR`, `COPY`, `ENV` and `EXPOSE`, then `CMD` last. Each one goes on its own line, the instruction in capitals.

### Hint 2
With `WORKDIR /app` set, a relative destination lands inside it, so `COPY app.py .` puts the file at `/app/app.py`. `ENV` takes `NAME=value`, with no spaces around the `=`.

### Hint 3
The same shape for a different app:

```dockerfile
FROM node:22-slim
WORKDIR /srv
COPY server.js .
ENV LISTEN=3000
EXPOSE 3000
CMD ["node", "server.js"]
```

Every word of the array is its own quoted string. `CMD ["python app.py"]` is one word: a program called `python app.py`, which does not exist.
