# Self-contained image design

## Goal

Make every published Drillion image carry the checksum-verified `kubeconform`
binary required by manifest tasks, so it can grade all shipped task kinds after
the image has been pulled without downloading a grader into learner state.

## Scope

This is the Docker appliance slice only. It does not change task content,
backup/restore formats, manifest compatibility policy, or the source/developer
workflow that fetches tools into a local data root.

## Ownership and data flow

`src/drillion/tools.py` remains the sole authority for a tool's release URL,
archive digest, executable name, and executable digest. The Docker build reads
the Linux pin for BuildKit's `TARGETARCH`, downloads the archive in a build
stage, verifies both digests, and copies only the executable into the installed
`drillion/_tools` package directory.

At runtime, `tools.installed(name)` verifies the packaged candidate first. If
it is absent or altered, it verifies the existing `<DRILLION_ROOT>/tools`
candidate. This preserves repository/developer support while ensuring an image
does not rely on its `/data` volume. Neither candidate is trusted merely
because it exists.

The immutable package path is deliberately separate from `/data`: mounting a
learner volume at `/data` cannot mask it, and Docker's non-root runtime never
writes it.

## Image proof

The image smoke script will run `drillion doctor` and `drillion selfcheck`
against a fresh named volume, then query the catalogue/health API rather than
counting `task.py` files. The test fixture for that script will emulate the
additional commands and assert failure propagation. The Python tool tests will
cover preference for a valid packaged binary, rejection of an altered packaged
binary, and fallback to the verified local-root binary.

The Dockerfile uses BuildKit's declared `TARGETARCH` argument in the downloader
stage, consistent with Docker's documented multi-platform build arguments. CI
continues to build the normal Linux image; release builds retain their existing
amd64/arm64 publication and attestations.

## Historical record

`docs/research/2026-09-19-deployment-architecture-and-branch-risks.md` will
retain its review evidence but replace its superseded executive recommendation
with the authorized Docker-only decision and this slice's completion state.

## Error handling and security invariants

- An archive with the wrong digest, a missing executable, or an executable with
  the wrong digest fails the image build.
- Runtime grading accepts only a freshly digest-verified executable.
- The build copies no archive or downloader into the final image.
- `/data` remains the only persistent writable mount and no tool is fetched at
  container start.

## Verification

Run focused Python tests for tool selection and image-smoke contracts; mutation
verify each new/changed test by altering its relevant production branch and
observing the focused test fail, then restore and rerun it. Build the local
image and run its smoke script when Docker is available. Finally run Ruff and
the focused tests, reporting browser verification separately as not requested.
