# Configuration and where your data lives

## Environment

| variable | default | meaning |
|---|---|---|
| `DRILLION_ROOT` | cwd if it has `tasks/`, else the checkout, else a per-user data directory | where `tasks/` and `progress.json` live |
| `DRILLION_HOST` | `127.0.0.1` | bind address (`0.0.0.0` inside Docker) |
| `DRILLION_PORT` | `8765` | port |
| `DRILLION_OPEN_BROWSER` | `1` | open the browser on start (`0` in Docker) |
| `DRILLION_SEED` | — | pin the data seed when running a task by hand |

## The root

Everything drillion owns — `tasks/` and `progress.json` — lives under one root, and nothing it
owns lives anywhere else.

Run it from a clone and the checkout is the root: the tasks you practise are the ones in
`tasks/`, edited in place, and nothing is copied anywhere. Run an installed drillion with no
`tasks/` in sight and the first command copies the tasks that ship inside the wheel into a
per-user data directory (`XDG_DATA_HOME`, `~/Library/Application Support`, `LOCALAPPDATA`),
once. A root that already has `tasks/` is never written over, so an upgrade cannot touch code
you saved. [ADR 0003](adr/0003-ship-the-tasks-and-seed-a-writable-root.md) has the reasoning.

`progress.json` holds your cards, open attempts, log, archived solutions and notes. It is
untracked and git-ignored, so a fresh clone starts with an empty ladder rather than the
maintainer's. It is the only copy of your practice history and nothing rebuilds it — if a pull
ever offers you a modify/delete conflict on it, keep your file.

## Docker

The container sets `DRILLION_ROOT=/data`, so mount something there:

```bash
docker run -d --name drillion -p 127.0.0.1:8765:8765 -v drillion:/data \
  ghcr.io/vazome/drillion:latest
```

The named volume outlives the container: upgrading is `docker pull` and start again, and your
progress is still there. `latest` follows the newest release; name a version —
`ghcr.io/vazome/drillion:0.1.0` — to stay put. [compose.yaml](../compose.yaml) is that same run
spelled out, plus `restart: unless-stopped` so it survives a reboot: save the one file anywhere
and `docker compose up -d`.

To keep those files in a directory you can open, bind-mount one and hand the container your own
uid — it runs as uid 1000 and cannot write a directory Docker made for root:

```bash
mkdir -p drillion-data
docker run -d --name drillion -p 127.0.0.1:8765:8765 \
  --user "$(id -u):$(id -g)" -v "$PWD/drillion-data:/data" \
  ghcr.io/vazome/drillion:latest
```

Mount a directory, never a single file: saving renames a `.tmp` over `progress.json`, and a
single-file bind mount refuses that rename.

## Security posture

The server binds to loopback, accepts only `127.0.0.1`/`localhost` host headers, rejects bodies
that declare more than 256 KB, and runs task code only inside a pytest subprocess with a timeout. It is a laptop
tool; do not put it on a public address.

## Verifying a release

Releases go out through PyPI's trusted publishing, so drillion stores no upload token anywhere,
and every artifact is attested where it lands. Which command you want depends on where you got
the file from.

**From the GitHub release** — the wheel, the sdist and their provenance are all on the release
page, so this needs nothing but the download:

```bash
gh attestation verify drillion-<version>-py3-none-any.whl --repo vazome/drillion
```

The `drillion-<version>.intoto.jsonl` beside them is the same provenance in a file, for a checker
that cannot reach GitHub's API.

**From PyPI** — PyPI keeps its own [PEP 740](https://peps.python.org/pep-0740/) attestation:

```bash
pypi-attestations verify pypi --repository https://github.com/vazome/drillion \
  pypi:drillion-<version>-py3-none-any.whl
```

**From ghcr** — the image carries build provenance and an SPDX SBOM. Verify the tag rather than a
platform digest; the tag resolves to the multi-arch index, which is what was signed:

```bash
gh attestation verify oci://ghcr.io/vazome/drillion:<version> --repo vazome/drillion
```

All three name the same thing: the `release.yml` run at the tag that built it.
