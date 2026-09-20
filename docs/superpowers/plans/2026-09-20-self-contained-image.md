# Self-contained image Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a checksum-verified `kubeconform` executable inside each Docker image and prove manifest tasks work from a fresh `/data` volume without a runtime download.

**Architecture:** `src/drillion/tools.py` continues to own the pin data. The Docker downloader stage imports that module using only the standard library, selects its Linux `TARGETARCH` pin, and rejects wrong archives or executable bytes before copying the executable to `drillion/_tools` in the final venv. Runtime tool discovery verifies that immutable candidate before its existing mutable-root fallback.

**Tech Stack:** Python 3.14, pytest, Docker BuildKit multi-platform arguments, Bash, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-20-self-contained-image-design.md`

## Global Constraints

- Do not edit `tasks/`.
- Do not add dependencies or a configurable tool path.
- `PINS` remains the sole release URL and checksum authority.
- `/data` remains the only persistent mutable container path; the baked executable must be outside it.
- Preserve source/developer `doctor --fetch` behavior as a verified local-root fallback.
- Every changed or new test needs deliberate mutation verification: demonstrate its relevant production change fails the focused test, restore it, then demonstrate the focused test passes.
- Do not commit this work.

---

### Task 1: Verified immutable tool discovery

**Files:**
- Modify: `src/drillion/tools.py:19,109-146`
- Modify: `tests/test_tools.py:10-38`

**Interfaces:**
- Produces: `PACKAGED_TOOLS: Path`, the immutable package directory.
- Produces: `installed(name: str) -> Path | None`, returning the first digest-verified candidate in `[PACKAGED_TOOLS / pin.member, tools_dir() / pin.member]`.
- Consumes: the existing `PINS`, `pin_for`, and `digest` interfaces.

- [ ] **Step 1: Write the failing tests**

Add three literal-payload tests. Each monkeypatches `tools.PACKAGED_TOOLS` and `settings.root`, replaces the current host pin's `binary_sha256` with `sha256(b"packaged")`, and asserts these outcomes:

```python
def test_a_matching_packaged_binary_is_preferred(tmp_path, monkeypatch):
    packaged = tmp_path / "package-tools"
    binary = packaged / "kubeconform"
    packaged.mkdir()
    binary.write_bytes(b"packaged")
    monkeypatch.setattr(tools, "PACKAGED_TOOLS", packaged)
    monkeypatch.setattr(settings, "root", tmp_path / "data")
    _pin_binary_digest(monkeypatch, b"packaged")
    assert tools.installed(tools.KUBECONFORM) == binary
```

Add a test that writes `b"altered"` to the packaged candidate and `b"local"` to `<root>/tools/kubeconform`, pins `b"local"`, and asserts the local path is returned. Add a third test with only an altered packaged candidate and assert `None`.

The production mutations these tests must catch are: removing `PACKAGED_TOOLS` from the candidate order; accepting a packaged path without its digest check; and returning `None` before evaluating the local fallback.

- [ ] **Step 2: Verify RED**

Run: `UV_CACHE_DIR=/tmp/drillion-uv-cache uv run --no-sync pytest tests/test_tools.py -q`

Expected: the new tests fail because `PACKAGED_TOOLS` does not exist and `installed()` only checks `<root>/tools`.

- [ ] **Step 3: Implement the minimal candidate verifier**

Move `import requests` into `_download()` so the module can be imported by the Docker downloader without installed application dependencies. Add:

```python
PACKAGED_TOOLS = PKG / "_tools"

def installed(name):
    pin = pin_for(name)
    for path in (PACKAGED_TOOLS / pin.member, tools_dir() / pin.member):
        if path.is_file() and digest(path) == pin.binary_sha256:
            return path
    return None
```

Keep `tools_dir()` and `acquire()` unchanged: acquisition always writes only the mutable developer/data-root location.

- [ ] **Step 4: Verify GREEN and mutate**

Run the focused test command. Then temporarily delete `PACKAGED_TOOLS / pin.member` from the candidate tuple and rerun only `test_a_matching_packaged_binary_is_preferred`; it must fail. Restore the tuple and rerun all of `tests/test_tools.py`; it must pass.

### Task 2: Architecture-specific, pin-driven Docker build

**Files:**
- Modify: `Dockerfile:18-75`
- Test: `tests/test_tools.py` (Task 1's runtime contract)

**Interfaces:**
- Consumes: `tools.PINS[tools.KUBECONFORM][("linux", TARGETARCH)]` and its archive/executable digest fields.
- Produces: executable `/app/.venv/lib/python3.14/site-packages/drillion/_tools/kubeconform` in the final image.

- [ ] **Step 1: Confirm the runtime test protects the consumer contract**

Run: `UV_CACHE_DIR=/tmp/drillion-uv-cache uv run --no-sync pytest tests/test_tools.py -q`

Expected: PASS before Dockerfile work. The consumer-visible runtime selection already has a red-green proof from Task 1; the Docker image build is the integration proof for this task.

- [ ] **Step 2: Add a downloader stage before `runtime`**

Use the project-pinned Python base image, copy `src/drillion/` so `tools.PINS` and the packaged schema manifest can be imported, and declare `ARG TARGETARCH`. In a Python heredoc, select:

```python
pin = PINS[KUBECONFORM][("linux", os.environ["TARGETARCH"])]
```

Download `pin.url` with `urllib.request.urlopen`, write it beneath `/tmp`, compare its SHA-256 with `pin.archive_sha256`, use `tools._extract()` to write `/out/kubeconform`, and compare its SHA-256 with `pin.binary_sha256`. Raise `SystemExit` on either mismatch. Do not hard-code a URL or checksum in the Dockerfile.

After the wheel is installed in `runtime`, create its `drillion/_tools` directory and copy only `/out/kubeconform` there. Preserve root ownership/readability and the existing non-root `drillion` user. Do not copy the archive, the source tree, or download utilities into `runtime`.

- [ ] **Step 3: Build the local image**

Run: `docker build --load --tag drillion:ci .`

Expected: successful build with an executable in the immutable package directory. If Docker is unavailable, record its exact error as a blocked integration proof; do not weaken the build checks.

- [ ] **Step 4: Integration mutation verification**

Temporarily change the downloader's expected executable digest comparison to `"0" * 64` and rerun the Docker build. Expected: build fails in the downloader stage. Restore the real comparison, rebuild, and confirm it passes.

### Task 3: Catalogue-aware image smoke coverage

**Files:**
- Modify: `.github/scripts/image-smoke.sh:45-58`
- Modify: `tests/test_ci.py:105-142`

**Interfaces:**
- Consumes: `drillion doctor`, `drillion selfcheck`, and `/api/health` from the built `drillion:ci` image.
- Produces: a zero exit only when the seeded-volume image reports a verified grader, selfchecks every catalogue task kind, and its health task count equals the catalogue's doctor count.

- [ ] **Step 1: Write the failing smoke-contract test**

Extend the fake Docker executable in `test_smoke_reaches_volume_check_and_propagates_failures` so it records every argument and returns a literal successful doctor line, `kubeconform: v0.8.0, verified`, and selfcheck success. Assert the successful script invokes `docker exec seeded drillion doctor` and `docker exec seeded drillion selfcheck`. Add `doctor` to the parametrized failing commands and assert exit status 7 for it.

The production mutations these tests must catch are removing the seeded-volume doctor invocation and removing the seeded-volume selfcheck invocation. The fake remains only at the Docker process boundary; the Bash script, its exit propagation, and its `curl` result are real.

- [ ] **Step 2: Verify RED**

Run: `UV_CACHE_DIR=/tmp/drillion-uv-cache uv run --no-sync pytest tests/test_ci.py -q`

Expected: the new assertions fail because the script only selfchecks the first container and compares health to a `task.py` glob.

- [ ] **Step 3: Make the smoke script prove the image contract**

After `seeded` becomes healthy, run `docker exec seeded drillion doctor` and require its grader line to end in `verified`; run `docker exec seeded drillion selfcheck`. Capture the final `N tasks, no problems` doctor line and compare its literal count with `curl -fsS .../api/health | jq -r .tasks`. Remove the checkout `ls tasks/*/task.py` count entirely.

Keep the existing LSP check, HTTP root check, and task-open check. The original first-container selfcheck can remain as the live mounted-root smoke, but the fresh named-volume checks are the image's offline task-kind proof.

- [ ] **Step 4: Verify GREEN and mutate**

Run the focused CI test command. Temporarily remove `docker exec seeded drillion selfcheck`, rerun only the new smoke-contract test, and confirm it fails. Restore it and rerun all `tests/test_ci.py`; it must pass.

### Task 4: Correct the research record and final verification

**Files:**
- Modify: `docs/research/2026-09-19-deployment-architecture-and-branch-risks.md:1-45`

**Interfaces:**
- Produces: a durable review record whose current decision is Docker-only and whose retained historical risks are explicitly time-scoped.

- [ ] **Step 1: Update the superseded decision**

Remove the duplicate decision-update block. Replace the `## Executive decision` conclusion with a dated statement that Docker-only distribution is authorized, `uv` remains a build/development tool, and this change closes the image-contained-validator prerequisite. Retain the original findings as historical review evidence; do not rewrite them as new observations.

- [ ] **Step 2: Run focused proof**

Run:

```bash
UV_CACHE_DIR=/tmp/drillion-uv-cache uv run --no-sync pytest tests/test_tools.py tests/test_ci.py -q
UV_CACHE_DIR=/tmp/drillion-uv-cache uv run --no-sync ruff check src/drillion/tools.py tests/test_tools.py tests/test_ci.py
UV_CACHE_DIR=/tmp/drillion-uv-cache uv run --no-sync ruff format --check src/drillion/tools.py tests/test_tools.py tests/test_ci.py
git diff --check
```

Expected: all commands pass.

- [ ] **Step 3: Run the image integration proof**

Run: `bash .github/scripts/image-smoke.sh`

Expected: the locally built `drillion:ci` image becomes healthy, verifies `kubeconform`, selfchecks all catalogue tasks from a named volume, and exits 0. Report browser/Playwright verification as not run because it was not requested.
