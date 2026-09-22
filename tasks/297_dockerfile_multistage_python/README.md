---
title: "multi-stage Python: build a virtualenv, ship it"
difficulty: hard
minutes: 20
prereqs: [290, 296]
track: docker
tags: [multi-stage, pip, image-size]
kind: docker
edits: Dockerfile
---
# multi-stage Python: build a virtualenv, ship it

*Python has no single binary to copy. A virtualenv is the closest thing: one folder holding everything pip installed.*

## Read first
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/): copying between stages
- [venv](https://docs.python.org/3/library/venv.html#how-venvs-work): what a virtualenv is on disk, and why it cannot move

## Why
Some Python packages compile C extensions when they install, which needs a compiler and headers the runtime has no use for. Others leave pip's build leftovers behind. A multi-stage build does the installing in one stage and hands the result to a clean one, and for Python the result to hand over is a virtualenv.

`python -m venv /opt/venv` makes a folder with its own `bin/python`, its own `pip` and its own `site-packages`. With `/opt/venv/bin` first on `PATH`, `pip install` installs into it and `uvicorn` is found in it. Copy that one folder into the final stage and every package comes along.

Two things decide whether the copied folder still works. The virtualenv's `python` is a link to the interpreter that made it, so both stages must be the same Python image. And its scripts have the folder's absolute path written into their first line, so it has to land at the same path. An `ENV` belongs to its stage, so the final stage sets `PATH` again.

## You get
The same FastAPI app and `requirements.txt` as the layer cache task.

## You return
A two-stage Dockerfile on Python `{python}`: the build stage creates a virtualenv and installs the requirements into it, and the runtime stage copies it and serves the app with uvicorn on port `{port}`.

## Rules
- both stages are `FROM python:{python}-slim`, and the first is named
- the build stage makes the virtualenv with `python -m venv` at an absolute path, puts its `bin` first on `PATH`, and installs `-r requirements.txt` into it with `--no-cache-dir`
- the runtime stage copies the virtualenv `--from` the build stage to the same path, installs nothing itself, and puts its `bin` on `PATH` again
- `app.py` is copied into the runtime stage, `EXPOSE {port}`, and one exec-form `CMD` runs uvicorn serving `app:app` on host `0.0.0.0` and port `{port}`

## Hints
### Hint 1
The layer cache task's Dockerfile, split in two. The install goes in the first stage; the app and the `CMD` go in the second, with one `COPY --from` in between.

### Hint 2
`PATH` has to name the virtualenv's `bin` first, and keep the rest:

```dockerfile
ENV PATH="/opt/venv/bin:$PATH"
```

That line appears in both stages.

### Hint 3
The runtime stage, for a different app:

```dockerfile
FROM python:3.13-slim
COPY --from=build /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /srv
COPY api.py .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7000"]
```

Nothing in it runs pip. If it did, the build stage would have been for nothing.
