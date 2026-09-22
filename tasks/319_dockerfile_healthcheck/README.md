---
title: a HEALTHCHECK with no curl in the image
difficulty: easy
minutes: 12
prereqs: [290]
track: docker
tags: [probes]
kind: docker
edits: Dockerfile
---
# a HEALTHCHECK with no curl in the image

*A running container is not a working one. A HEALTHCHECK tells Docker how to ask, and the image already holds everything it needs to ask with.*

## Read first
- [HEALTHCHECK](https://docs.docker.com/reference/dockerfile/#healthcheck): the options, and what the exit code means
- [urllib.request.urlopen](https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen): fetching a URL with nothing but the standard library

## Why
`docker ps` says `Up 3 hours` for a server that stopped answering two hours ago. The process is alive, so as far as Docker knows, all is well. A HEALTHCHECK is a command Docker runs inside the container on a timer: exit 0 and the container is `healthy`, anything else often enough in a row and it is `unhealthy`. Compose can wait for a healthy database before starting the app, and an orchestrator can replace an unhealthy container.

Almost every example online uses `curl -f`. On a `-slim` Python image, curl is not installed, so the example either fails, or leads to an `apt-get install curl` that adds a download tool and its libraries to every image, for one line. The image already has an HTTP client: Python. `urllib.request.urlopen` raises on a refused connection, a timeout, or any 4xx or 5xx answer, and an uncaught exception exits with 1, which is exactly the signal the check needs.

The timing matters too. `--interval` is how often to ask. `--timeout` is how long one try may take before it counts as failed; the default is 30 seconds, long enough for a hung server to go unnoticed. `--start-period` gives a slow boot some grace before failures count.

## You get
A build context with a FastAPI app that answers `GET /health`, and its `requirements.txt`, open in the tabs above the editor.

## You return
A Dockerfile for the app on Python `{python}`, served by uvicorn on port `{port}`, that checks `/health` every `{interval}` seconds using Python alone.

## Rules
- one stage, `FROM python:{python}-slim`; install `requirements.txt`, then copy `app.py`, as in 290
- no `curl` or `wget` anywhere in the file
- one `HEALTHCHECK`, with `--interval={interval}s` and a `--timeout` in seconds, shorter than the interval
- its probe is in exec form and runs `python`, fetching `http://localhost:{port}/health`
- `EXPOSE {port}`, and one `CMD` in exec form: `uvicorn` serving `app:app` on host `0.0.0.0` and port `{port}`

## Hints
### Hint 1
The options go between `HEALTHCHECK` and `CMD`, and the probe after `CMD`, like any exec-form command:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s CMD ["some", "command"]
```

### Hint 2
`python -c` runs a line of Python. Semicolons separate statements, so a whole probe fits in one string:

```dockerfile
CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)"]
```

Single quotes inside, because the array's own strings use double ones.

### Hint 3
A long line splits with a backslash. The HEALTHCHECK is one instruction, however many lines it takes:

```dockerfile
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s \
    CMD ["python", "-c", "..."]
```
