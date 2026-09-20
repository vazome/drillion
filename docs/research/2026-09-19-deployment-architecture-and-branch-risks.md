# Deployment architecture and config-authoring branch risks

Date: 2026-09-19
Branch inspected: `docs/config-authoring-design` at `a70342b`
Purpose: preserve the branch review and decide whether drillion should replace native
`uv tool install` deployments with one Docker-image-only path.

> **Decision update (2026-09-20):** The maintainer authorized the Docker-image-only transition.
> The original assessment and staged safeguards remain evidence for maintaining that path; the
> implementation in this branch applies the distribution and release-documentation portion while
> keeping `uv` as an internal build and development tool.

## Executive decision

Do **not** make Docker the only deployment path yet.

Make the published image a complete, first-class appliance and consider presenting it first for
people who already use Docker. Keep `uv tool install drillion` as the native path. The application
already has one codebase and one wheel; these are two launch envelopes, not two products. Removing
the native envelope would save some platform-specific tool acquisition and sandbox work, but would
move that complexity onto every learner: Docker Desktop or Engine, a daemon/VM, image pulls,
container replacement, volume handling, and manual browser opening.

This is especially important because `uv tool install` is not ordinary `pip install` into the
user's interpreter. uv gives each tool a persistent isolated environment, puts only its executable
on `PATH`, and can install/select the required Python. Docker adds OS/process isolation; it is not
the first isolation boundary in the current native installation.

There is also no end-user `uv pip` deployment path to remove. The `uv pip install` in the
Dockerfile is an image-build step that installs Drillion's already-built wheel into the image's
locked environment. Replacing that line would not simplify how a learner installs or runs Drillion.

The image is not yet a complete replacement anyway: manifest grading expects a verified
`kubeconform` under the writable data root, but the Dockerfile does not put it there, and current
image smoke coverage counts Python `task.py` files rather than all task kinds. The branch's backup
and erase paths are also still Python-only. Making Docker the only documented route before those
are fixed would concentrate users on the least-complete path.

Putting kubeconform into `/data/tools` during the image build would not solve this: the documented
runtime volume mounted at `/data` hides the image's `/data` contents. A Docker-baked validator must
live in immutable image/package storage, while the mounted root remains learner-owned state.

## Evidence categories

- **Observed code** means the current checkout was read directly on 2026-09-19.
- **Prior discussion** means a local Claude Code JSONL record was read. It is architectural
  history, not proof of the current implementation.
- **External documentation** means current first-party uv or Docker documentation.
- **Recommendation** is the judgment made from those sources.

## Durable branch review

This records the review of `origin/main...a70342b`. It does not claim that every item remains open
after later commits. Re-check each item against the eventual merge head.

### Committed branch issues

| Severity | Finding | Evidence and consequence |
|---|---|---|
| Critical | Backup, restore planning and erase are not kind-aware. | `src/drillion/backup.py:18,35-54,81-85,113-136,193-223` fixes the bundle at format 1, calls Python `region.cut`/`region.validate`/`region.stub`, and writes/reads only `regions/<slug>.py`. A manifest can make bundle/erase fail or be absent from a backup. The approved design requires adapter-driven `.py`/`.yaml` artifacts and format 2 (`docs/superpowers/specs/2026-09-16-config-authoring-design.md:394-413`). This is the merge blocker. |
| High | Production content was shipped before the lifecycle/distribution gate it depended on. | The design requires one non-catalogue fixture, then backup format 2, installed-artifact checks, and exactly `271_first_deployment` before any batch (`design:415-443`). The branch instead adds manifest tasks 268-278, including multi-document storage content. This turns unfinished infrastructure into learner data. |
| High | Docker and installed-distribution proof do not cover the new grader. | The runtime image installs the Python environment but not kubeconform (`Dockerfile:28-77`). `tools.installed()` looks only under `<root>/tools` (`src/drillion/tools.py:109-146`). CI downloads the tool in the native OS matrix (`.github/workflows/ci.yml:103-108`), but the image smoke runs `selfcheck` without fetching it and counts only `tasks/*/task.py` (`.github/scripts/image-smoke.sh:21-22,45-58`). The sdist assertion also derives its expected catalogue only from `task.py` (`.github/workflows/ci.yml:155-160`). A green image job therefore does not prove manifest grading works offline. |
| High | The task-authoring contract and task counts are stale. | `CONTRIBUTING.md:80-116` says every task requires `tier` and `task.py`; manifest tasks intentionally use optional/no tier, `task.yaml`, `grade.py`, and `solution.yaml`. `CONTRIBUTING.md:10,21`, `CONTEXT.md:15-18`, and README text still say 267 while `doctor` reported 278 during review. Contributors are being directed to an invalid contract. |
| High | Persisted manifest attempts reject any grader revision change instead of establishing compatibility. | `src/drillion/kinds.py:211-216` compares the stored brief revision for equality. The design requires continuing from the stored brief/spec when the new grader/template is compatible and blocking without destroying work only when it is incompatible (`design:365-372,458-461`). Equality is safe but turns every grader edit into an unnecessary abandoned sitting. |
| Medium | Manifest provenance is collapsed rather than explicit. | The design calls for validator version and binary identity, Kubernetes version, schema digest, grading revision, and a distinct brief-generation revision (`design:267-279`). The branch computes a composite fingerprint and stores a brief revision, but archive/run consumers do not expose all those identities separately. A verdict is harder to reproduce or diagnose. |
| Medium | Multi-document grading exceeds the accepted first slice. | The design requires exactly one non-empty YAML mapping and explicitly rejects multi-document submissions (`design:204-205`); the branch adds `check_many` and multi-resource content. That may be a useful later feature, but it expands parser, grading, solution, backup and UI state before the single-document lifecycle is complete. |
| Medium | Kind behavior is still visible in multiple presentation branches. | `web/src/Task.tsx` contains repeated manifest checks in a screen component. Two kinds do not by themselves justify a new abstraction, but further kinds would scatter lifecycle/presentation policy. Keep the boundary under observation; consolidate only behavior that is genuinely shared by a kind-owned model. |
| Medium | The branch combines several review domains. | The 55-commit delta includes config authoring, ten tasks, UI proof-of-concept documents, release/security changes, schemas, runner/sandbox work, and web changes. This makes rollback and proof attribution harder. It is not a correctness bug, but the releasable vertical slice described by the design would have been easier to validate and revert. |
| Low | The committed diff fails whitespace validation. | `git diff --check origin/main...HEAD` reports trailing whitespace in `UI-POC-REPORT.md` and the config-authoring design, plus blank lines at EOF in the design. |

One earlier review item needs correction rather than preservation as a hard defect: the design and
implementation plan ask the public API to expose a canonical learner filename, while the repository
glossary says the slug is the identifier and explicitly avoids “filename” (`CONTEXT.md:20-22`). The
current catalogue exposes `kind` but not `filename` (`src/drillion/catalogue.py:18-23`). Settle that
contract deliberately. Do not add a public field merely to satisfy an old plan if the client can
derive nothing from it that the server must own.

### Uncommitted working-tree risks

At review time the working tree had 12 modified files. They are not part of `HEAD`, so they must be
reviewed separately from the committed branch:

- `tasks/275_statefulset_headless/task.yaml` contains `asfaf`; manifest learner files are specified
  to ship empty. This would turn a starter into accidental submitted content.
- Ten manifest READMEs add `## Read first` before `## Why`, while the documented contract says the
  four opening sections begin with `## Why`, `## You get`, `## You return`, `## Rules`
  (`CONTRIBUTING.md:88-102`). The prerequisite links themselves may be useful; their placement
  conflicts with the parser/authoring contract.
- `.gitignore` adds `.env`, unrelated to the task content edits. It may be sensible independently,
  but should not be swept into a task-content commit without intent.

### Verification state captured by the review

The earlier review established the following, and this research did not rerun the full suite:

- Passed: Ruff; `drillion doctor` with 278 tasks; web lint; production web build; four focused Node
  suites; working-tree `git diff --check`.
- Failed: committed-range `git diff --check`, as described above.
- Blocked: full pytest stalled in `tests/test_api.py` under sandbox asyncio and was interrupted.
- Not run: browser/Playwright verification, in accordance with the repository instruction requiring
  explicit agreement.

These are scoped proofs, not a statement that the branch is merge-ready.

## What the current deployment architecture actually is

### Shared application core

Both distributions contain the same wheel-built application, bundled web client, and packaged task
template. An installed run seeds a writable root; a repository run uses its checkout directly
(`src/drillion/settings.py:10-38`, `src/drillion/cli.py:89-120`). The web files remain immutable
package content while tasks and `progress.sqlite3` live under the writable root
(`settings.py:56-68`).

That separation was deliberate. A prior packaging discussion found that tasks could not be read
only from `site-packages`, because learner code lives in the task artifact. It chose a pristine
packaged template plus a writable seeded root for both wheel and image distributions (Claude
conversation `f4f8a743-17d4-4797-acc0-dc624a678494`, message
`f99f3655-ab2d-461b-975f-98724c8b663e`, 2026-08-26T20:57:50Z).

### Native `uv tool` envelope

- README promises Linux, macOS, WSL and native Windows installation, automatic acquisition of
  Python, automatic browser opening, and `uv tool upgrade drillion` (`README.md:76-124`).
- uv documents `uv tool install` as a persistent isolated tool environment whose executable is
  placed on a `PATH` bin directory; packages are not imported into the current Python environment.
  uv also supports managed Python installations and a portable universal lock resolution.
- Drillion chooses OS-appropriate per-user storage (`settings.py:18-38`) and opens the host browser,
  including WSL's `explorer.exe` path (`cli.py:123-128,183-187`).
- The new config-authoring code downloads a checksum-pinned kubeconform build for Linux/macOS
  amd64/arm64 and Windows amd64 into the data root (`tools.py:54-110,140-190`). That preserves the
  native path, but creates five binary pins and platform-specific test obligations.

This is application isolation, not an OS sandbox. The graded subprocess still relies on Drillion's
own Landlock, macOS sandbox, Windows restricted token, or guard/floor tiers (`SECURITY.md:19-115`).

### Docker envelope

- The image fixes the runtime to Linux/Python 3.14, runs as uid 1000, exposes only the app port,
  carries a healthcheck, disables browser opening, and puts the writable root at `/data`
  (`Dockerfile:28-77`).
- The recommended run binds only host loopback and mounts a named volume. Compose adds
  `restart: unless-stopped` (`README.md:126-137`, `compose.yaml:1-14`).
- The release publishes linux/amd64 and linux/arm64, attests the multi-platform index, and publishes
  an SBOM (`.github/workflows/release.yml:54-125`).
- CI builds the image once, smoke-tests it, and scans it (`.github/workflows/ci.yml:207-280`).

The named-volume choice was also deliberate: a bind directory auto-created by Docker is root-owned
while the container runs as uid 1000. Prior discussion selected a named volume for a clone-free
installation and later gave Compose a restart policy so it represented “leave this local service
running,” not merely a longer `docker run` command (Claude conversation
`f4f8a743-17d4-4797-acc0-dc624a678494`, messages
`48ea0b12-daba-4fc1-901b-c65a35a29de4`,
`96ac5ac6-0130-4cfe-a4a3-e34861d02132`, and
`2664f8a4-b310-4f2f-9718-39c3ddb34b00`).

## Would Docker-only be simpler?

### Where it would genuinely simplify Drillion

1. **One runtime OS.** kubeconform, future hadolint, schemas and Python dependencies can be baked
   and tested as one immutable Linux filesystem. Five host-binary pin variants become two image
   architectures. This is the strongest argument for Docker-only now that tasks use non-Python
   tools.
2. **More consistent isolation.** Docker describes a container as an isolated process with its own
   files while sharing the host kernel. On Docker Desktop, Linux containers run inside Docker's
   Linux VM. That gives native Windows/macOS users an additional boundary around the whole app,
   though it does not eliminate Drillion's inner learner-code sandbox.
3. **Reproducible release object.** Base image digest, dependencies, tasks, web assets, tools,
   provenance and SBOM can be one tested object. The existing release pipeline is already close.
4. **Fewer host path differences.** The application sees `/data`, Linux filesystem semantics and a
   fixed interpreter layout everywhere.

### Where it would make the whole product less simple

1. **Installation moves from one executable manager to a platform service.** Native users need
   Docker Engine on Linux or Docker Desktop/another Linux-container runtime on macOS and Windows.
   Docker Desktop itself runs a VM for Linux containers. That is real “semi-virtualization,” but it
   is more machine-level machinery than an isolated uv tool environment.
2. **Browser UX regresses.** A container cannot reliably open the user's host browser. Drillion
   deliberately sets `DRILLION_OPEN_BROWSER=0`; users must open the URL. A host launcher could fix
   that, but it recreates a platform-specific installation layer and defeats the single-path goal.
3. **Data becomes less visible.** A named volume correctly outlives containers, but it is managed by
   Docker rather than appearing as an ordinary per-user directory. Docker's own backup procedure
   mounts the volume into a helper container and archives it. Drillion's in-app portable backup
   must therefore remain correct; Docker cannot replace format-level backup/restore.
4. **Upgrades are not one operation.** The documented flow is pull the image and recreate/start the
   container while retaining the volume (`docs/configuration.md:58-71`). `uv tool upgrade` updates
   the application while the external data root stays in place. Both are manageable; Docker is not
   inherently fewer steps unless Compose and documentation own the replacement workflow clearly.
5. **Cross-platform support becomes indirect.** The current image supports Linux amd64/arm64. macOS
   and Windows work by hosting that Linux image through Docker Desktop/VM integration. Native uv
   currently supports each OS directly and CI exercises all three (`ci.yml:64-108`). Dropping it
   trades app platform code for a large external platform prerequisite.
6. **Release maintenance remains substantial.** Multi-architecture QEMU builds, base-image refresh,
   OS vulnerability scanning, registry availability, attestations, SBOMs and image smoke tests do
   not disappear. The release workflow explicitly budgets 45 minutes for emulated arm64
   (`release.yml:54-61`). Docker consolidates runtime variance; it does not eliminate maintenance.
7. **Container privilege is not VM equivalence on Linux.** Docker containers share the host kernel.
   Namespaces/cgroups isolate processes, but this is not a separate-kernel VM boundary. The current
   non-root user, loopback-only port, no Docker-socket mount, and narrow data mount are good. Avoid
   `--privileged`, host PID/network modes, added capabilities or a Docker socket, all of which would
   materially weaken that boundary.

### Security conclusion

Docker is a worthwhile outer boundary, especially for Windows where Drillion's native restricted
token does not block reads or network (`SECURITY.md:74-97`). It should not be marketed as “safe
virtualization” without qualification:

- On Linux, containers share the host kernel.
- On Docker Desktop, the VM strengthens host separation, but mounted data remains deliberately
  reachable.
- Learner code still executes in the application container. If the inner sandbox falls back to its
  guard tier, Docker limits the blast radius to the container and mounted data, but the named volume
  contains the learner's tasks and progress—the exact data that matters.

Keep both layers: a non-root, least-privilege container and the existing per-submission sandbox.

## Recommended target architecture

Use **one application artifact and two supported envelopes**:

| Concern | Native envelope | Docker appliance |
|---|---|---|
| Best for | Learners wanting the smallest install and automatic browser opening | Existing Docker users, stronger host separation, always-on local service |
| Install | `uv tool install drillion` | `docker compose up -d` or documented `docker run` |
| Runtime | OS-native isolated tool environment | Pinned Linux image, non-root |
| Mutable data | Per-user Drillion root | `/data` named volume |
| Upgrade | `uv tool upgrade drillion` | pull + recreate against same volume |
| Browser | Open automatically | Open `127.0.0.1:8765` manually |
| External graders | Verified per-platform fetch | Baked and verified in image |
| Backup | In-app format plus stopped-root copy | Same in-app format; optionally volume archive |

Do not create separate application behavior for the two envelopes. `DRILLION_ROOT`, host binding and
browser opening are already the necessary seam. The Docker image may carry a baked tool path, but
the tool verifier should use the same pin/digest authority as native installation.

## Staged next steps

### Stage 0 — make the current branch safe

1. Implement kind-owned backup/restore/erase and format 2 with legacy format-1 reading.
2. Remove production manifest tasks until the one-fixture lifecycle/distribution gate passes, or
   complete those gates before merging any task.
3. Fix the authoring contract, counts, committed whitespace, and accidental working-tree content.
4. Resolve the public `filename` contract from actual client needs rather than copying the old plan.
5. Reconcile with current `origin/main`, then rerun focused and full verification.

### Stage 1 — make Docker genuinely self-contained

1. Bake the correct kubeconform binary for each target architecture into the image at build time;
   verify its digest during the build and at runtime. Do not download it on first learner run.
2. Make the tool lookup support an immutable packaged/image location plus the existing verified
   native data-root location, with one digest authority.
3. Run manifest `doctor` and `selfcheck` in image smoke tests with the network unavailable after
   build. Count catalogue tasks by the catalogue/doctor result, not `task.py` globbing.
4. Build an sdist-derived wheel and the image, then prove Python and manifest tasks, packaged
   schemas, solution rendering, backup/restore and erase offline.
5. Preserve the current hardening: non-root user, loopback port, healthcheck, no socket mount, no
   extra capabilities, `/data` as the only writable persistent mount.

### Stage 2 — make the appliance easy to live with

1. Give one copy-paste Compose flow for install, start, stop, logs, update, version pin, and removal
   without deleting the volume.
2. Put export/import in Settings at the center of backup guidance. Add a tested Docker volume archive
   procedure for disaster recovery, but do not make it the only portable format.
3. State clearly that upgrades require pull/recreate and that removing a container is safe while
   removing the volume is destructive.
4. Test the documented flow on Linux amd64, Linux arm64, Docker Desktop macOS, and Docker Desktop
   Windows/WSL. A multi-arch registry manifest alone is not end-user proof.
5. Measure support burden qualitatively from issues and release failures. Drillion promises no
   telemetry, so do not add telemetry merely to settle this decision.

### Stage 3 — reconsider Docker-only only with an explicit threshold

Reconsider removing native deployment only if all are true:

- Docker is the clear majority user path or native platform/tool failures are a sustained material
  maintenance burden.
- The image is fully offline after pull and every task kind is covered by image smoke tests.
- Backup/export, upgrade/recreate, browser instructions and data removal are as obvious as the
  native flow.
- macOS and Windows Desktop flows are actually tested, not inferred from Linux CI.
- The project accepts that users without Docker—including straightforward native Windows users—are
  no longer supported.

Even then, keep uv internally for dependency locking and image construction. “Docker-only
deployment” does not imply removing uv from development or the Docker build; the current Dockerfile
already uses uv effectively for deterministic wheel and environment construction.

## Prior Claude discussion: decisions worth retaining

The local records show a coherent evolution rather than indecision:

1. The initial production-layout discussion treated Docker as optional and put mutable content
   outside the package (`1375e0f2-863c-4d01-b689-0c8fca7aa586`, message
   `c8c216a8-62d3-40d8-9baf-cd0315fe6525`, 2026-08-25).
2. Packaging work later discovered both wheel and image were incomplete without packaged tasks and
   a writable seeding lifecycle; that shared fix made both distribution lines real
   (`f4f8a743-17d4-4797-acc0-dc624a678494`, message
   `f99f3655-ab2d-461b-975f-98724c8b663e`, 2026-08-26).
3. Installation copy explicitly distinguished native automatic browser opening from Docker's
   self-contained image and persistent volume (`f4f8a743-17d4-4797-acc0-dc624a678494`, message
   `c49ea501-bb9d-4b79-aca1-7608fa447b94`, 2026-08-27).
4. A later native-install incident showed a real lifecycle cost: `uvx` reported the current version
   while serving an older seeded task tree. The wheel was correct; the one-shot seed logic was not.
   That conversation led to syncing packaged machinery on every run while preserving learner files
   (`f94ebc89-734a-438d-9de2-e9e36610d55d`, messages
   `f5dd0602-cf2f-4450-baf8-e4b90dd13256` and
   `67216318-415d-440e-8c6a-ec283d97c3b7`, 2026-09-08). The lesson is that the mutable-root
   lifecycle needs one shared invariant; changing launch envelopes does not remove it.
5. Config-authoring research recognized the real new pressure: kubeconform is a standalone Go
   binary, so native support means securely acquiring platform binaries. The approved direction
   was checksum-pinned acquisition under `<root>/tools`, while already flagging backup extension
   handling as a risk (`2213b00c-88a5-42b7-8ad0-945b70db3a45`, messages
   `5a60dcf2-5ad4-446d-afd1-b264c9ff1023` and
   `782b2723-0728-4bf0-949a-115a3b3d1260`, 2026-09-16).

The new Docker-only idea responds to a real change—the platform now grades with external binaries.
The proportionate response is to finish the appliance first, not to delete the already-working
native route before the replacement is complete.

## Primary external sources

- uv, **Tools**: <https://docs.astral.sh/uv/guides/tools/> — persistent isolated tool
  environments and executables on `PATH`.
- uv, **Python versions**: <https://docs.astral.sh/uv/concepts/python-versions/> — managed versus
  system Python installations and `uv python install`.
- uv, **Resolution**: <https://docs.astral.sh/uv/concepts/resolution/> — universal `uv.lock`
  resolution across operating systems, architectures and Python versions.
- Docker, **What is a container?**:
  <https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/> — containers
  are isolated processes sharing a kernel, unlike full VMs.
- Docker, **Multi-platform builds**:
  <https://docs.docker.com/build/building/multi-platform/> — image architecture/OS compatibility
  and emulation.
- Docker, **Volumes**: <https://docs.docker.com/engine/storage/volumes/> — persistence beyond a
  container lifecycle and the official backup/restore pattern.
- Docker, **Port publishing and mapping**:
  <https://docs.docker.com/engine/network/port-publishing/> — loopback-only publishing.
- Docker Desktop, **Platform FAQ**: <https://docs.docker.com/desktop/troubleshoot-and-support/faqs/general/>
  — Linux containers run inside Docker Desktop's Linux VM and mount/file-sharing boundaries still
  matter.

## Docker-only transition hypotheses and what it unlocks

This section turns the earlier discussion into hypotheses that can be tested. It deliberately
separates three things that are easy to conflate:

- A **release source** is the signed `v<version>` tag and its changelog section.
- A **distribution channel** is a way a learner obtains and launches Drillion: today, a PyPI
  wheel through `uv tool` or an OCI image through GHCR/Docker.
- A **runtime artifact** is the thing actually executed. A multi-platform image tag is one OCI
  image index containing per-platform manifests; it is not one Linux binary that runs unchanged
  everywhere.

The candidate decision is therefore: keep one release source but make GHCR's multi-platform image
the sole supported learner distribution. It does **not** mean removing `uv` from development or
the image build, collapsing amd64 and arm64 into one CPU-specific filesystem, or treating a moving
tag as an immutable release.

### H1: one artifact can make every supported runtime complete and reproducible

**Unlocks, if proved.** The image can hold the application wheel, built client, task template,
external graders, schemas and their verification material in one versioned release object. A
release test can then prove exactly the filesystem that a learner starts, without asking native
machines to download an architecture-specific grader on first use. That is particularly valuable
as Drillion adds non-Python task kinds: the release boundary becomes "the image runs every shipped
task offline after pull," not "the current host can acquire every required tool."

The existing release workflow already publishes an amd64/arm64 index and binds provenance and an
SBOM to its pushed digest. Docker documents that a multi-platform image index selects its matching
platform manifest at pull time. This preserves the two CPU targets behind one public image name,
but it does not remove the need to build and test both targets.

**Does not unlock.** It cannot make mutable learner data part of the immutable artifact. `/data`
must remain a mounted, backed-up state root, and the seeded task/update invariant remains necessary.
Nor can a successful build prove the image contains a newly added tool or task kind: installed-image
tests must exercise that behavior.

**Acceptance evidence.** For each published platform, run `doctor`, `selfcheck`, a representative
submission, restart/upgrade against existing data, and backup/restore with outbound network disabled
after the pull. Verify the image index with `docker buildx imagetools inspect`, then record its
digest in release metadata.

### H2: Docker-only reduces host-support complexity enough to justify a Docker prerequisite

**Unlocks, if accepted as product scope.** The runtime OS contract becomes Linux and the supported
CPU contract becomes the image's listed platforms. Drillion can concentrate external-tool
installation, paths, permissions and process behavior in the image. That reduces the application's
native Windows/macOS/Linux acquisition matrix and makes a production failure more reproducible from
one image digest.

**Cost and boundary.** This moves, rather than erases, complexity. Linux users need a container
engine; macOS and Windows users need Docker Desktop or an equivalent Linux-container runtime. Those
users execute Linux containers through a VM/integration layer, need enough disk and memory for
images, and still have host-specific volume/file-sharing behavior. The browser remains a host
concern. Supporting Docker Desktop on Windows and macOS is still cross-platform support and needs
real end-to-end tests.

**Decision test.** Do not use a vague claim that Docker is "simpler." Define the supported hosts
and their setup path, run the complete documented flow on each, and compare the resulting support
burden with native distribution over at least two releases. With Drillion's no-telemetry policy,
use issue/release evidence rather than new collection.

### H3: one image produces a better trust and rollback story

**Unlocks.** A version tag provides a human-friendly release name; the image digest identifies the
exact multi-platform index. GitHub documents attesting an OCI image by its fully-qualified subject
name and pushed digest, and verification through `gh attestation verify oci://...`. Combined with
the existing provenance and SBOM attestations, this gives a single consumer verification path and
makes a known-good rollback an explicit `image@sha256:...` choice.

**Required policy.** Keep immutable semantic-version tags and make `latest` convenience only.
Docker documents that tags can be retargeted while digests are immutable. Release notes must record
the index digest, supported platforms, the upgrade/rollback command, and the provenance verification
command. A user who values repeatability should pin a digest; a user who wants current releases may
use the documented version or `latest` tag.

**Does not unlock.** Attestation proves a statement about what built a digest; it does not make a
bad application safe, make arbitrary Docker invocations safe, or recover a deleted volume. Keep the
non-root image, loopback-only publishing, no Docker-socket mount, minimal writable mount and the
inner learner-code sandbox.

### H4: one distribution channel can simplify release operations

**Unlocks.** The release workflow can stop building/uploading wheel and sdist artifacts, PyPI trusted
publishing, release-asset attestations, and their consumer documentation. Its irreversible release
critical path becomes: tag/main gate, multi-platform image build/push, image attestation/SBOM, image
smoke/scan, and a changelog-backed GitHub Release containing the exact image reference. This reduces
the number of artifact stores whose version, provenance and availability must agree.

**Important limitation.** It does not reduce the release to one job or one platform. Image scanning,
QEMU/native builders, registry permissions/availability, both manifests, the state migration path
and release metadata remain. A GitHub Release should remain as the human changelog and discovery
surface unless a separate decision replaces it; it just no longer carries installable Python assets.

### H5: the appliance can make ongoing use more obvious than native tools

**Unlocks, if the Compose contract is complete.** One named service and named volume can give a
consistent vocabulary for start, stop, logs, update, version pin, rollback, backup and destruction.
The image can also run after the user closes the terminal via the existing restart policy. This is
especially attractive for people who already operate local Docker services.

**Does not unlock.** `docker run` alone is not lifecycle UX. It is easy to lose a container's
unmounted state, accidentally remove a volume, or update an image without recreating the service.
The browser still will not open reliably from the container. The documented Compose flow must make
the state boundary and destructive commands unmistakable, and Settings export/import remains the
portable recovery path.

## Recommended decision and future execution plan

The evidence supports **image-first readiness, not immediate Docker-only removal**. Finish the
image as the complete appliance first, measure the actual support trade-off, then make the
hard-to-reverse product decision. This order creates useful work even if native `uv tool` remains
supported indefinitely.

### Phase A — establish the image contract

1. Write the supported image contract: public GHCR name, semantic-version and `latest` tag policy,
   supported platforms, `/data` ownership, networking, update/rollback semantics and verification
   command. Decide whether GitHub Releases remain changelog-only; do not change consumer docs yet.
2. List every runtime dependency by task kind, including its source, version, checksum, target
   platforms and immutable image location. The same authoritative pin data must drive native fetches
   and image installation while both envelopes exist.
3. Define the release invariant: a digest-pinned image works without a network after pull, for every
   shipped task kind, while preserving an existing `/data` volume across upgrade and rollback.

Exit criterion: the contract is reviewed and each statement has an owner test or a documented
operational procedure.

### Phase B — make the image the full runtime artifact

1. Install external graders into an immutable image path during each platform build, verify the
   selected binary against the authoritative checksum, and make runtime lookup prefer that verified
   immutable path when present. Do not place it under `/data`, because the learner volume masks image
   contents there.
2. Extend image smoke tests to use an actual built image and run catalogue discovery, every kind's
   reference/selfcheck path, and one user submission. Derive expected task coverage from the
   catalogue rather than a `task.py` filename convention.
3. Add offline checks after pull/build. Prove package assets, schemas and external graders are found
   without a runtime download, then prove backup, restore, reset and update behavior with a retained
   named volume.
4. Retain both platform builds and add platform-specific proof where emulation cannot establish
   behavior. Inspect the pushed image index and verify its attestation against its index digest.

Exit criterion: each supported platform has a digest-pinned image test record and all task kinds
work offline from that image.

### Phase C — prove the learner operations

1. Make `compose.yaml` the one canonical learner workflow. Document exact commands for first start,
   normal stop/start, logs, updating to a version, rolling back by digest/version, backup/export and
   removal that preserves data; put destructive volume removal in a separately labelled step.
2. Exercise the documentation on Linux amd64, Linux arm64, Docker Desktop macOS and Docker Desktop
   Windows/WSL. Confirm port binding remains loopback-only, the service starts after reboot, and
   browser instructions are clear.
3. Publish at least two image releases with this complete flow while retaining the native route.
   Record setup/update failures and documentation gaps from normal maintainer support, without adding
   telemetry.

Exit criterion: the image path is independently usable on every proposed supported host and no
release-only regressions remain unresolved.

### Phase D — make the product-scope decision

Proceed to Docker-only only if Phase B/C evidence shows a net reduction in support and the project
explicitly accepts excluding users without a Linux-container runtime. If accepted:

1. Announce a deprecation window in release notes and README; state the final native-supported
   version and keep its provenance/verification instructions reachable.
2. Remove PyPI publishing, wheel/sdist release assets, native-install badges/instructions and
   native-only release verification only after that window. Keep source builds/developer tooling and
   `uv` where they remain necessary to build/test the image.
3. Simplify `release.yml` only after an image-only dry run proves tag/version gate, multi-platform
   push, SBOM/provenance, scan, smoke and changelog release creation. Preserve the same signed-tag
   and main-ancestry rules.
4. At removal, update README, configuration, CONTRIBUTING, release verification and CI together;
   search for every PyPI/wheel/native-install claim so no stale contract remains.

Exit criterion: users have one documented Docker path, release artifacts and verification describe
only that path, and upgrade/rollback/data-retention behavior is proven for the final supported
platforms.

## Sources added for this transition analysis

- Docker, **Multi-platform images and manifest lists**:
  <https://docs.docker.com/build/building/multi-platform/> — one image index can select an
  architecture-specific manifest at pull time.
- Docker, **Image digests**:
  <https://docs.docker.com/dhi/explore/security-concepts/digests/> — digests are immutable; tags
  are mutable.
- GitHub, **Publishing Docker images**:
  <https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images> — GHCR
  publication with `GITHUB_TOKEN` and the permissions required for image attestations.
- GitHub, **Artifact attestations**:
  <https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations>
  — OCI subject name/digest, registry publication and `gh attestation verify`.
