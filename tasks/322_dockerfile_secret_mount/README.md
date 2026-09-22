---
title: a private package index, and a token that never lands in the image
difficulty: hard
minutes: 20
prereqs: [292, 321]
track: docker
tags: [docker, dockerfile, buildkit, secrets, pip]
kind: docker
edits: Dockerfile
---
# a private package index, and a token that never lands in the image

*The install needs a token for the company's package index. Pass it as a build argument and anyone who pulls the image can read it back out.*

## Read first
- [Build secrets](https://docs.docker.com/build/building/secrets/): `--secret` on the command line, a secret mount in the Dockerfile
- [RUN --mount=type=secret](https://docs.docker.com/reference/dockerfile/#run---mounttypesecret): the `id`, `target` and `env` options
- [pip configuration: environment variables](https://pip.pypa.io/en/stable/topics/configuration/#environment-variables): every option can be set as `PIP_<NAME>`

## Why
Most companies keep their own Python packages on a private index: Artifactory, Nexus, GitLab or CodeArtifact. pip reaches it through an index URL with a token in it, `https://user:token@pypi.acme.internal/simple`, and the install inside the Dockerfile needs that URL.

Every obvious way to get it there leaks it. An `ARG` or `ENV` is written into the image's history, and `docker history` prints it. A `.netrc` or `pip.conf` copied in and deleted by a later RUN is still in the layer that copied it, and any layer can be unpacked. A token on the `pip install` line is in the history too. Images get pushed to registries, pulled onto laptops, and scanned by tools that print what they find.

A secret mount is BuildKit's answer. The value is handed to the build from outside, `docker build --secret id=pip_index_url,env=PIP_INDEX_URL .`, and exists only while the one RUN that mounts it is running. With `env=`, the mount sets an environment variable for that RUN alone, and pip reads `PIP_INDEX_URL` as if it were `--index-url`. Nothing about it reaches a layer, the history, or the image's config.

## You get
A build context with a FastAPI app and its `requirements.txt`, open in the tabs above the editor. In real life some of those requirements would come from the private index.

## You return
A Dockerfile that installs the requirements through the private index, with its URL passed as the build secret `pip_index_url`, on Python `{python}`, served by uvicorn on port `{port}`.

## Rules
- one stage, `FROM python:{python}-slim`; `requirements.txt` copied on its own before the install
- one `RUN pip install --no-cache-dir -r requirements.txt`, with a secret mount whose `id` is `pip_index_url` and whose `env` is `PIP_INDEX_URL`
- no `ARG`, `ENV` or `LABEL` that names the index URL, a token or a password, and no `COPY` of a credentials file
- nothing about the index or its token on the install line itself
- `EXPOSE {port}`, and one `CMD` in exec form: `uvicorn` serving `app:app` on host `0.0.0.0` and port `{port}`

## Hints
### Hint 1
A secret mount is a flag on the RUN, like the cache mount in 321, with its own options:

```dockerfile
RUN --mount=type=secret,id=some_id,env=SOME_VARIABLE \
    some-command
```

### Hint 2
pip reads any of its options from an environment variable named `PIP_` and the option in capitals, with dashes as underscores. `--index-url` is `PIP_INDEX_URL`, so the install line itself needs no change at all.

### Hint 3
Without `env=`, the secret is a file at `/run/secrets/<id>`, and the command has to read it: `PIP_INDEX_URL=$(cat /run/secrets/pip_index_url) pip install ...`. The `env=` form says the same thing in the mount, and keeps the install line plain.
