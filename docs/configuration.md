# Configuration and where your data lives

## Environment

| variable | default | meaning |
|---|---|---|
| `DRILLION_ROOT` | cwd if it has `tasks/`, else the checkout, else a per-user data directory | where `tasks/` and `progress.sqlite3` live |
| `DRILLION_HOST` | `127.0.0.1` | bind address (`0.0.0.0` inside Docker) |
| `DRILLION_PORT` | `8765` | port |
| `DRILLION_OPEN_BROWSER` | `1` | open the browser on start (`0` in Docker) |
| `DRILLION_SEED` | — | pin the data seed when running a task by hand |

## The root

Everything drillion owns, `tasks/` and `progress.sqlite3`, lives under one root, and nothing it
owns lives anywhere else.

The Docker image carries a pristine task template. On its first start, Drillion copies that template
into the mounted `/data` root. Every later start brings Drillion-owned task machinery in line with
the image version while preserving the code you wrote. A task Drillion no longer ships moves to
`tasks/_retired/<slug>/` rather than being deleted, and a task you added yourself is never touched
— `tasks/.shipped` records what Drillion put there, and that is all it takes back.
[ADR 0003](adr/0003-ship-the-tasks-and-seed-a-writable-root.md) has the reasoning, and
[ADR 0008](adr/0008-an-upgrade-keeps-the-region-and-nothing-else.md) how upgrades behave.

`progress.sqlite3` holds your cards, open attempts, log, archived solutions and notes. It and
its SQLite journal files are git-ignored, so a fresh clone starts with an empty ladder. SQLite
transactions serialize updates from processes sharing this root; the database belongs on a
local filesystem, including a local Docker volume, not a network share or cloud-sync folder.

An existing `progress.json` is imported on first access in a single transaction. Its original
bytes are preserved, and a completed import is never repeated. Invalid JSON is refused with an
error instead of starting over; repair the JSON or restore a backup and retry. A newer database
format is also refused without rewriting it. Stop old drillion servers before upgrading: an
old release still writes JSON and cannot see new SQLite progress. Downgrading to such a release
would show only the pre-import snapshot, not the progress made since upgrading.

Passing or abandoning commits the archive before resetting the task file. A pending reset is
stored in the same transaction and retried on the next access after an interruption. Recovery
preserves externally edited code rather than overwriting it.

### Backup and restore

Stop every drillion process using the root, then copy the **whole root** to another location.
This keeps saved task code and progress together. Restore with all servers stopped too, keeping
the damaged root aside until the restored copy has been checked. Never delete a SQLite journal
to clear an error: it may be needed for crash recovery. For a live database-only backup, use
SQLite's backup API or the SQLite CLI's `.backup` command, not a raw copy of an active database.

The retained JSON is a pre-migration snapshot, not an ongoing backup. SQLite protects committed
transactions against interrupted writes; it cannot protect against disk loss or accidental
deletion, and it does not make task slugs stable across renames.

## Docker

The container sets `DRILLION_ROOT=/data`, so mount a named volume there:

```bash
docker run -d --name drillion -p 127.0.0.1:8765:8765 -v drillion:/data \
  ghcr.io/vazome/drillion:latest
```

The named volume outlives the container. To update or roll back, pull the desired image, stop the
old container, remove it, then run it again with the same volume; removing the container does not
remove the volume:

```bash
IMAGE=ghcr.io/vazome/drillion:latest
docker pull "$IMAGE"
docker stop drillion
docker rm drillion
docker run -d --name drillion -p 127.0.0.1:8765:8765 -v drillion:/data "$IMAGE"
```

`latest` follows the newest stable release. Use a version such as
`ghcr.io/vazome/drillion:0.8.2` to stay on a named release or the digest recorded in its GitHub
Release to reproduce an exact image. [compose.yaml](../compose.yaml) is the same run spelled out,
plus `restart: unless-stopped` so it survives a reboot: save the one file anywhere and
`docker compose up -d`.

To keep those files in a directory you can open, bind-mount one and hand the container your own
uid, since it runs as uid 1000 and cannot write a directory Docker made for root:

```bash
mkdir -p drillion-data
docker run -d --name drillion -p 127.0.0.1:8765:8765 \
  --user "$(id -u):$(id -g)" -v "$PWD/drillion-data:/data" \
  ghcr.io/vazome/drillion:latest
```

Mount a directory, never a single file: SQLite needs to create journal files beside the
database, and task saves rename temporary files in their task directories.

## Security posture

The server binds to loopback, accepts only `127.0.0.1`/`localhost` host headers, rejects bodies
that declare more than 256 KB, and runs task code only inside a pytest subprocess with a timeout. It is a laptop
tool; do not put it on a public address.

## Verifying a release

Each release is a multi-platform GHCR image with build provenance on its image index and an SPDX
SBOM for each platform image. Verify the version tag, which resolves to the signed
multi-architecture index:

```bash
gh attestation verify oci://ghcr.io/vazome/drillion:<version> --repo vazome/drillion
```

The GitHub Release records the exact immutable image digest created by the same `release.yml` run.
