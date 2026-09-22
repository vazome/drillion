---
title: the layer cache, and why requirements.txt goes first
difficulty: easy
minutes: 12
prereqs: [289]
track: docker
tags: [layer-cache, pip]
kind: docker
edits: Dockerfile
---
# the layer cache, and why requirements.txt goes first

*A one-character change to your code should not cost a two-minute reinstall of everything it depends on.*

## Read first
- [Build cache](https://docs.docker.com/build/cache/): how a layer is reused, and what invalidates it
- [Optimize cache usage](https://docs.docker.com/build/cache/optimize/#order-your-layers): ordering layers so the cache survives an edit

## Why
Every instruction is a layer, and the builder caches each one. On the next build it reuses a layer until it meets the first instruction whose inputs changed; from there on everything is rebuilt. For `COPY` the input is the files copied, so the layer is invalid the moment any of them changes.

That makes the order the whole game. Copy the app and then install the dependencies, and every edit to the app throws away the install. Copy only `requirements.txt`, install, and only then copy the app, and an edit to the app rebuilds one small layer while the install comes from the cache. Dependencies change weekly; code changes every few minutes.

`pip` keeps a cache of every wheel it downloads, which is dead weight inside an image: `--no-cache-dir` leaves it out. hadolint insists, and so does every reviewer who has pulled a 900 MB image.

uvicorn listens on `127.0.0.1:8000` unless told otherwise. Inside a container that address is the container itself, unreachable from outside it, so a server in a container binds `0.0.0.0`. (FastAPI's own `fastapi run` binds `0.0.0.0` for you; here you start uvicorn yourself and say it.)

## You get
A build context with a FastAPI app and its `requirements.txt`, open in the tabs above the editor.

## You return
A Dockerfile that installs the requirements, then copies the app, on Python `{python}`, served by uvicorn on port `{port}`.

## Rules
- one stage, `FROM python:{python}-slim`, with `WORKDIR /app`
- `requirements.txt` is copied on its own, then installed with `pip install --no-cache-dir -r requirements.txt`
- `app.py` is copied after the install, never before it
- `EXPOSE {port}`
- one `CMD` in exec form: `uvicorn` serving `app:app`, on host `0.0.0.0` and port `{port}`

## Hints
### Hint 1
Two `COPY` lines instead of one, with the `RUN` between them. The first copies only the file that decides what gets installed.

### Hint 2
The install line is `RUN pip install --no-cache-dir -r requirements.txt`. `-r` reads the list from the file, so the pinned versions in it are the ones you get.

### Hint 3
uvicorn takes the app first, then its options, and every option and value is its own string in the array:

```dockerfile
CMD ["uvicorn", "shop:api", "--host", "0.0.0.0", "--port", "7000"]
```

`shop:api` is "the object `api` in the module `shop`". Here the module is `app` and so is the object.
