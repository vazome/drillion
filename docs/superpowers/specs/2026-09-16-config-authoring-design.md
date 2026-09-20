# Config authoring in drillion

Date: 2026-09-16
Status: merged design; implementation pending

## Why

drillion teaches Python by making people type it out against a grader that changes its data
every sitting. The same pressure applies to configuration languages: copying a manifest and
changing two fields does not train recall of `readinessProbe`. The skill this design targets
is narrow and physical: recall the shape, recall where it nests, type it correctly, from nothing.

Kubernetes first. Docker second. Helm and the rest come later and are out of scope here.

## What this is not

- Not a cluster. Nothing is deployed, nothing is applied, no daemon runs, and no `kubectl` is required.
- Not a rewrite of the learning model. The ladder, cards, hints, gates, notes, log, focus and
  scheduler retain their meaning. Attempts, archives and supporting infrastructure must become
  kind-aware to preserve their existing guarantees.
- Not Helm, kustomize, Terraform, Compose or CI YAML. Those are later tracks.
- Not a linting course. `kubeconform` passing is a floor, never the grade.

Adding a second task kind requires a common learner-artifact boundary across editing,
grading, updates, attempts, recovery and backups.

## The four decisions

1. **Real tools grade it.** `kubeconform` establishes schema validity against drillion's pinned
   Kubernetes OpenAPI version. `check()` adds the exercise requirements. This does not claim
   acceptance by an API server or correct controller/runtime behavior.
2. **Both install lines get the same grading.** `drillion doctor` acquires and verifies pinned
   tools. Pip, clone and Docker use the same validator version and schema content.
3. **The seed generates the brief.** Requirements vary per sitting. Generate them once in a
   sandboxed child and persist them on the attempt; displaying or grading an open attempt must
   never regenerate them. Random generation may repeat a brief; uniqueness is not promised.
4. **The learner opens an empty file.** No marker, no skeleton, no holes to fill. Seed/update
   must preserve an existing learner file, including an intentionally empty one.

## Vocabulary

Added to `CONTEXT.md`:

**Kind**: What language a task is written in: `python` or `manifest`. A task's kind decides
which grader runs, which file the learner edits, and what the editor highlights.
_Avoid_: type, format, language, mode.

`tier` is not extended. It means how far into the Python language a task reaches, and a
Kubernetes task reaches nowhere into it. Config tasks carry `kind: manifest`, a `track`
(`kubernetes`), and ordinary tags (`deployment`, `probes`, `resources`, `configmap`).

Existing tasks without `kind` default to `python`.
Make catalogue requirements and doctor validation conditional on kind: Python retains its
required tier; manifests do not acquire a fabricated Python tier. Expose `kind` and learner
filename in `public()`/API metadata. Update TypeScript metadata so manifest tasks may omit
`tier`; facets, filters and cards must tolerate that absence. Reject unsupported kinds
explicitly.

**Focus** keeps its existing tier/track/tag matching meaning. `focus: kubernetes` selects the
track. Verify missing tiers do not break matching or rendering; no new focus vocabulary is needed.

**Brief** is not a new learner-facing word. Generated requirements are the task's **spec**,
already defined as "the guidance a task shows you: Why / You get / You return / Rules".
For `kind: manifest`, the spec is rendered per attempt. Internally, `brief()` returns the
mapping used to render and grade that spec.

## A task on disk

```text
tasks/271_first_deployment/
  README.md       frontmatter carries kind: manifest; "You return" holds {placeholders}
  task.yaml       the learner's, entirely; ships empty
  grade.py        brief() and check(); never served to the browser
  solution.yaml   the gated solution template and selfcheck's input
```

Compared with a Python task, `task.py` splits into three files: the learner's half becomes
`task.yaml`, the grader's half becomes `grade.py`, and the reference answer becomes
`solution.yaml`. Python marker, cut and splice behavior does not apply to the YAML file.
Keeping `grade.py` out of the browser is an interface boundary, not a claim that locally
installed task source is secret.

The task-kind adapter declares `task.yaml` as
learner-owned. First seed creates the packaged empty file only if absent. Subsequent startup,
seed and upgrades preserve its entire contents. Python updates retain their existing
learner-region preservation behavior. Package-owned graders and templates may update, subject
to the open-attempt compatibility rules below. Add installed-user upgrade coverage, not only
tests run from the repository.

## The `grade.py` contract

Two functions, analogous to today's `_gen` and `_reference`:

```python
SERVICES = ["checkout", "billing", "search", "ingest"]

def brief(r):
    """Requirements for one sitting, from the attempt's seeded Random."""
    name = r.choice(SERVICES)
    return {
        "name": name,
        "namespace": r.choice(["payments", "platform", "web"]),
        "replicas": r.randint(2, 5),
        "image": f"ghcr.io/acme/{name}:1.{r.randint(0, 9)}.{r.randint(0, 9)}",
        "port": r.choice([8080, 8443, 9090]),
        "probe_path": r.choice(["/healthz", "/ready", "/live"]),
        "memory": r.choice(["256Mi", "512Mi", "1Gi"]),
    }

def check(doc, b):
    """Assert that the parsed learner document meets the stored brief."""
    assert doc["kind"] == "Deployment", "kind"
    assert doc["metadata"]["name"] == b["name"], "name"
    assert doc["metadata"]["namespace"] == b["namespace"], "namespace"
    assert doc["spec"]["replicas"] == b["replicas"], "replicas"
    container = doc["spec"]["template"]["spec"]["containers"][0]
    assert container["image"] == b["image"], "image"
    probe = container["readinessProbe"]["httpGet"]
    assert probe["path"] == b["probe_path"], "probe path"
    assert probe["port"] == b["port"], "probe port"
```

This is an illustrative excerpt, not the complete first-task grader. Every requirement shown
in that task's spec needs a corresponding check, including the chosen meaning of `memory`,
container count, ports and selector/label consistency where requested.

`check` uses plain `assert`: grading runs through pytest so the existing `_headline`,
`summarise` and `printed` machinery can report failures. Ensure loaded grader assertions
receive the intended pytest handling; test useful feedback from the imported module.

Neither the server nor catalogue imports
`grade.py`. Both `brief()` and `check()` execute only inside sandboxed children, including
doctor and selfcheck execution. Validate the child's brief result as a bounded JSON
mapping with string keys and supported scalar values; reject non-finite numbers, unsupported
objects and oversized output. Pin limits in the implementation and test rejection.

Load a grader by absolute path with a unique
module name such as `drillion_grade_271`, adding an invocation identity when needed. Do not
depend on `import grade`: the runner adds `tasks/`, not each task directory, to
`PYTHONPATH`, and repeated module names can collide in selfcheck. The canonical manifest
convention is `brief(random.Random(seed))` inside the child. Existing `_lib.rng()` remains
unchanged; it takes no argument and reads `DRILLION_SEED`.

There is no task-authored `render` function. README prose uses `{placeholders}`; trusted
application code substitutes validated stored data without executing the grader.

## The seeded spec

Generate the spec when the attempt opens:

1. Select the attempt seed and identify the task/grader revision.
2. In a sandboxed child, load the grader and call `brief(random.Random(seed))`.
3. Validate the returned mapping and render the README template using that mapping.
4. Atomically persist the attempt seed, brief mapping, rendered spec, and generation revision.
5. Return the persisted spec. Every grading run and gated solution request receives that
   attempt's stored mapping. Retries or concurrent opens must return the committed attempt.

Persist the rendered spec as well as the mapping so a README edit during an upgrade cannot
silently change the learner's displayed requirements.
If generation or formatting fails, do not leave a usable half-initialized attempt.

An unopened manifest task shows its static **Why** and **You get** sections in the catalogue.
Those sections must not depend on brief placeholders. Show generated requirements only after
an attempt opens. Catalogue discovery and rendering use static task metadata only.

Literal braces in README templates must be doubled. `catalogue._read` statically parses the
template and grader AST, checking syntax, required function definitions and allowed simple
placeholder names without importing the task. Where brief keys cannot be determined statically,
doctor/selfcheck validate them against generated mappings. Static inspection does not promise
that every possible brief formats successfully.

On upgrade, never regenerate an existing manifest brief from its seed. Updated graders and
solution templates must continue to accept persisted mappings from earlier versions of that
task; cover that compatibility when changing their inputs. A failure to consume a stored
mapping is an authoring/infrastructure error and must preserve the text and attempt, not mark
the learner's answer wrong or silently reopen the sitting. Record the actual grading fingerprint
on each run. Python attempts migrate without fabricated manifest data. Backups preserve
manifest attempt data.

## Grading

`runner.run_tests` dispatches through the kind implementation. For manifests it snapshots the
learner's file and stored attempt brief into scratch and creates a fixed pytest harness.
The harness loads the task's grader by absolute path under a unique module name inside the
sandbox. It never regenerates the brief.

Runner harness pseudocode:

```python
def test_manifest():
    # Resolved pinned paths and the attempt mapping are supplied by trusted setup.
    out = subprocess.run(
        [KUBECONFORM, "-strict", "-kubernetes-version", KUBERNETES_VERSION,
         "-schema-location", LOCAL_SCHEMA_TEMPLATE,
         "-output", "json", "task.yaml"],
        capture_output=True, text=True, timeout=VALIDATOR_TIMEOUT,
    )
    assert out.returncode == 0, readable_validator_output(out)
    doc = load_exactly_one_mapping(Path("task.yaml").read_text())
    grade = load_grader_by_path(GRADER_PATH, UNIQUE_MODULE_NAME)
    grade.check(doc, STORED_BRIEF)
```

Require exactly one nonempty YAML document whose root is a mapping. Reject multi-document
input, scalar/list roots and empty submissions before semantic checks. Strict validation must
see the original text, so duplicate keys cannot disappear through an earlier permissive parse.
Use safe YAML loading and make missing-field/type failures readable to the learner.

Retain the existing sandbox, overall 60s timeout and case-capture path. Bound the validator
subprocess within that overall budget. Verify compatibility on each supported sandbox; reuse
of `_run_pytest` alone does not prove every tier needs no changes.

Schema errors and missed exercise requirements use the existing output panel. Reduce validator
JSON to useful messages and paths, with bounded stderr fallback for invalid/missing JSON.
Missing/corrupt tools or packaged schemas are grader-availability errors, not red answers.

Pass `-strict`, an explicit concrete Kubernetes version and only the bundled local schema
location. Do not enable missing-schema skipping or remote fallback. Kubeconform documents
strict-mode rejection of additional properties and duplicate keys, an unpinned default version
of `master`, and local schema locations. Its scope is OpenAPI validation, not all server-side
checks. [Kubeconform documentation](https://github.com/yannh/kubeconform#usage)

## The region

`region.py` remains the Python implementation: `bounds`, `cut`, `_solve`, `stub`, AST
validation and splice semantics keep their existing meaning.

Use a small task-kind adapter for the **learner artifact**. Python's artifact is a region in `task.py`;
manifest's artifact is all of `task.yaml`.

The adapter owns or delegates:

| Operation | Python | Manifest |
|---|---|---|
| Filename and editor language | `task.py`, Python | `task.yaml`, YAML |
| Read/body and replacement | Existing region extraction/splice | Whole file |
| Validation | Existing Python rules | YAML syntax and one-mapping submission contract |
| Empty/reset | Existing signature stub | Zero-byte file |
| Etag | Existing learner-region policy | Hash exact learner-file bytes |
| Revision | Existing Python grader policy | Composite grading fingerprint below |
| Gated solution | Existing reference path | Safely render `solution.yaml` with stored brief |
| Archive/backup suffix | `.py` | `.yaml` |

An empty manifest is a valid initial/reset lifecycle state but not a valid submission. Preserve
existing editing/save semantics; do not prevent storing an unfinished draft simply because it
cannot yet pass grading.

Route API read/save, `has_given`/bounds-dependent behavior, attempt opening, etags, abandonment,
solution retrieval, pass/archive/reset, seed/update, backup/restore/erase and recovery through
this boundary. Avoid scattered direct calls to Python region operations on manifests.

### Pending reset and recovery

Make `state._task_path()`, `reset_after_commit()` and recovery resolve the learner artifact
through the adapter before any manifest can pass.

Migrate `DB_SCHEMA` so pending-reset records identify the kind and canonical root-relative
learner path rather than deriving `task.py` from the slug. Existing records migrate as Python
records. Resolve paths under the task root, reject traversal or mismatched task identity, and
dispatch the reset through the adapter. Preserve the transaction ordering between pass/archive
commit and deferred filesystem reset. Recovery must be idempotent, retain existing protection
against overwriting newer edits, and leave no duplicate pass after retry.

Exercise interruption after commit, before reset and during reset for both kinds. YAML recovery
must produce an empty learner file; Python recovery must preserve its grader machinery.

### Grading fingerprint

The manifest etag identifies learner bytes. The revision identifies the grading environment;
these are different promises. Hashing only `grade.py` is insufficient.

Use a versioned, canonical fingerprint covering at least grader bytes, pinned kubeconform
version and verified binary identity, concrete Kubernetes version and schema-content digest.
Record validator version, Kubernetes version and schema digest explicitly in attempt/run/archive
metadata; the existing `python` field alone does not describe a manifest verdict. Record the
brief-generation revision separately from the actual grading revision. Platform binary hashes
may differ; retain that provenance while testing equivalent behavior across supported platforms.
If shared task grading helpers are introduced later, include their content in the fingerprint
at that point.

## Acquiring the tools

`drillion doctor` gains a tools section reporting present and verified, missing, checksum
mismatch, unsupported platform, or invalid/missing schema data. Missing infrastructure produces
an actionable grader-unavailable state instead of an answer failure.

- Maintain pinned version/platform/architecture entries in `settings.py`, including release
  archive URL, archive SHA256, expected executable member and executable SHA256.
- Define supported OS/architecture aliases explicitly. Unsupported combinations fail clearly.
- Download to a temporary location with connection/read limits and bounded size. Verify the
  archive before extraction; do not treat it as a naked executable. Upstream's tagged v0.8.0
  release configuration specifies `.tar.gz`, a Windows `.zip` override and a separate
  `CHECKSUMS` file. This establishes the acquisition design; it does not select drillion's pin.
- Extract exactly the expected regular executable member; reject traversal, absolute paths,
  links and ambiguous members. Set executable permissions where required.
- Verify the extracted binary, then atomically install into `<root>/tools/<name>` on the same
  filesystem. Keep the prior verified install usable if acquisition fails; clean interrupted
  temporary downloads/extractions. Never put the tool on `PATH` or in the source repository.
- Verify the selected executable before grading, not only at download. Treat checksum changes
  as explicit pin updates, not something a runtime download can silently authorize.

Pin a concrete `X.Y.Z` Kubernetes version beside the validator release and package its matching
`standalone-strict` schema set. Actual versions/checksums remain implementation selections;
unresolved placeholders are not acceptable at the first-task release gate.

Include schemas and their version/digest manifest alongside `tasks` and `web/dist` in wheel
and sdist data. Resolve them
from the installed package, not the working directory. Verify local references are complete.
Build/install a real wheel in a clean environment and grade offline. Build from sdist and
verify the resulting package too. Docker must contain the same schema digest and validator
release; test its installed contents rather than assuming the image copies them.

During grading, schemas are never downloaded. Doctor tool acquisition is the config grader's
network step; this is not a claim about all drillion features. Docker images bake in verified
tools so acquisition is unnecessary there. Release asset selection must be checked against the
chosen release's [upstream assets](https://github.com/yannh/kubeconform/releases).
Archive layout is defined in the
[tagged v0.8.0 release configuration](https://github.com/yannh/kubeconform/blob/v0.8.0/.goreleaser.yml).

## Sandbox

Subprocess execution is already an intentional sandbox capability. Keep task-authored Python
inside the sandbox when adding both brief generation and external validation.

Required implementation work:

- Landlock: permit the verified tool location to execute, and allow read access to packaged
  schemas and required grader inputs. Retain network denial.
- macOS: add tool/schema paths to the required SBPL rules and verify actual execution as well
  as readability under the generated profile.
- Windows: verify tools and schema reads under the existing restricted token; add permission
  changes only if required by those platform checks.
- Guard: retain existing policy; confirm brief generation and grading work within it.

Apply the same bounded child-execution discipline to briefs, doctor and selfcheck.
Validate with networking unavailable on every supported platform; do not rely only on Linux's
network restriction to establish offline behavior.

## Editor

Import the YAML registration from the existing standalone-languages dependency and include it
in the production build. Consume public `kind`/filename metadata, use `.yaml` URIs and YAML
language IDs for manifest editor and diff models, and retain `.py` for Python. Dispose/recreate
models and language-client bindings correctly when switching task kinds. Never attach the
Python LSP to a manifest model.

The first release provides highlighting and bracket handling, without YAML completion or a
YAML language server. Verify edit and diff views in the built application, including switching
from Python to YAML and back. Dockerfile registration belongs to the later Docker phase.

Hide the generated-arguments case panel for manifest runs: they have no Python-style generated
call arguments. Keep the persisted spec visible as the requirements, and use the existing
output panel for schema diagnostics and assertion failures. Return an absent case value for
manifest runs rather than a misleading empty Python case. Preserve Python case capture.

## selfcheck

Dispatch `runner.selfcheck()` by kind. Retain Python's region/reference path and add manifest
solution grading. CI runs the whole catalogue on every supported OS, so manifest support must
land **before the first manifest enters the production catalogue**.

For a deterministic seed corpus, selfcheck generates a sandboxed brief, renders the solution,
parses the rendered YAML and runs the same strict schema and semantic grading path used for
learner submissions. It also renders the README and verifies its placeholders. Use a documented
stable corpus that covers branch choices and numeric boundaries; exhaust meaningful branches
where the discrete generator is small. Sampled success is evidence for those cases, not proof
that the entire generated domain is satisfiable.

`solution.yaml` earns its place twice: it is selfcheck input and the existing gated **solution**
served through `/api/task/{slug}/solution`. For an open attempt it uses that attempt's stored
brief and compatible template, never a newly generated one.

The solution gate is intentionally different between kinds in the browser. A Python learner
can inspect `_reference` below the marker in `task.py`, so its solution endpoint is advisory.
For manifests, serve `solution.yaml` only through the gated endpoint: the general asset route
must remain confined to the task's `assets/` directory using resolved-path containment. Do not
make the solution template or grader available through an ungated file route to make the kinds
look alike. This gate controls browser delivery; a user with local filesystem access can still
read installed files.

Raw `str.format(**brief)` can change YAML types or
break quoting. Keep the template file, but render scalar placeholders with a trusted helper
that serializes strings as quoted YAML-compatible scalars and numbers/booleans with their
intended types. Define placeholders as entire scalar values; reject unsupported interpolation
positions, attribute/index lookups and format conversions. Values such as image strings are
assembled in `brief()`, not by splicing unquoted fragments in YAML. Parse every rendered
solution before grading, and cover quotes, colons, braces and YAML-like string values. README
substitution remains a separate plain-text operation.

Missing tools fail doctor/CI prerequisites as infrastructure problems. They must not silently
skip manifest selfcheck and report an all-green catalogue. Use test-only fixture tasks to land
these capabilities while the production catalogue still contains only Python tasks.

## Backup

Route bundle, restore planning and erase through the same learner-artifact adapter,
storing Python regions as `<slug>.py` and whole manifests as
`<slug>.yaml`.

Set **FORMAT = 2** before writing manifest entries.
Version 0.8.2 accepts format 1 and can silently ignore YAML entries in it; new data must not
masquerade as format 1. The existing format-equality check in 0.8.2 rejects format 2.
The new reader continues to accept valid legacy format-1 Python bundles.

Format 2 identifies artifact kind and canonical filename and includes persisted brief/spec,
seed and revision metadata needed to resume an open manifest attempt. Retain existing archive
and state guarantees. Validate the full restore plan before mutation; reject incompatible or
unknown formats/kinds and unsafe paths without silent drops. Preserve the user's existing
restore conflict policy. Erase/reset uses the adapter's empty representation.

Verify mixed-kind round trips, legacy import, unfinished manifest attempt
restoration and erase behavior. A restored attempt must display the same requirements and
grade against the same mapping, or report incompatible infrastructure without destroying data.

## Phases

Each phase ends with something that runs. The first milestone is a working Deployment fixture,
kept outside the production catalogue. Release it as `271_first_deployment` only after all
lifecycle and distribution requirements are complete.

1. **One fixture, end to end.** In an isolated test root, a learner can open an empty YAML
   editor, receive a sandbox-generated persisted spec, type a Deployment and receive strict
   schema and semantic feedback. Build the kind-aware metadata and artifact adapter, unique
   grader loading, canonical RNG, brief persistence, pinned tool acquisition, local schemas,
   sandbox permissions and grading fingerprint needed for that path. Include YAML model/diff
   handling and the manifest case-panel behavior. Seed/update preservation and kind-aware
   pending-reset recovery must exist before exercising a successful pass. Include a safe
   reference-solution renderer and a deterministic fixture check using the normal runner.
   Exit: the fixture opens, grades, passes, archives and resets through the application; Python
   behavior remains green. This is the same vertical slice that will become the first task,
   not a throwaway alternative grader. It is not yet shipped in the production catalogue.
2. **Release readiness and the first catalogue task.** Complete whole-catalogue selfcheck on
   every supported OS, branch/boundary seed coverage, solution gating, backup format 2,
   legacy import, restore and erase. Complete wheel/sdist/Docker schema packaging and offline
   installed-artifact checks. Exercise interrupted resets, repeated seed, upgrades, persisted
   requirements, mixed-kind backup round trips and language switches in the built UI.
   Verify actual pins, matching schema digests and infrastructure-error handling. Only when
   these gates pass, promote the fixture to exactly `271_first_deployment` and rerun catalogue
   CI. No Kubernetes batch is authored before this single task is releasable.
3. **The Kubernetes batch.** Pod, Deployment, Service, ConfigMap, Secret, Ingress, PVC, Job,
   CronJob, HPA, probes, resources, labels and selectors. Each task stays within the initial
   single-document/single-file scope and adds complete assertions plus selfcheck coverage.
   Extend packaged schema coverage explicitly when needed.
4. **Docker.** Reuse the established lifecycle. Pin `hadolint` for daemonless linting, but first
   select an actual Dockerfile parser/API for assertions on instructions. Define parsing and
   lint policies, fingerprint both dependencies, register the editor language and add fixture
   selfcheck before the first Docker task. Do not imply hadolint JSON is an AST. Hadolint
   documents an internal AST and CLI diagnostic output formats; these are different interfaces.
   [Hadolint documentation](https://github.com/hadolint/hadolint)

## Risks

- **A generated brief that no manifest satisfies.** Early selfcheck tests a deterministic
  corpus and covers meaningful branches; it does not prove arbitrary generators satisfiable.
- **Authoring cost exceeds the Python kind.** Four files, varying requirements and safe scalar
  templates require care. Shared helpers under `tasks/_lib` may reduce repetition; changes to
  grading helpers must be reflected in fingerprints.
- **Upgrades alter a sitting.** Persisted briefs/specs and compatibility coverage prevent silent
  requirement changes. Incompatible graders/templates must block clearly while preserving work.
- **Seed/reset/restore destroys learner work.** Ownership-aware updates, migrated pending resets,
  adapter-based backups and crash/upgrade tests are prerequisites to production content.
- **A stale or incomplete pin.** Treat validator, Kubernetes version and schema content as an
  explicit compatibility set; doctor reports their identities. Dependency bumps rerun offline
  installed-package and reference-solution checks.
- **Brace escaping and YAML scalar errors.** Static README syntax checks catch malformed
  templates; executable selfcheck catches generated-key mismatches. Scalar-aware rendering and
  parsed solution checks cover the distinct YAML risks.
- **Packaging differs from a checkout.** Wheel, sdist-derived wheel and Docker validation must
  establish that tools/schemas can actually be found without source-tree paths or network access.

## Deferred, deliberately

- Helm, kustomize, Compose, Terraform, CI YAML.
- Multi-document manifests and tasks spanning more than one file.
- Any language server or schema completion for YAML.
- `docker build` actually building, which requires additional runtime infrastructure.
- Grading by policy, for example conftest and Rego. Revisit if `check()` proves insufficient;
  the first implementation does not require authors to learn a second policy language.

Lifecycle safety, persisted briefs, backup compatibility, selfcheck, language handling,
fingerprinting and packaging are not deferred. They are prerequisites to the first production task.

## Appendix: implementation audit and revision history

This design incorporates the original implementation review against `vazome/drillion` main
at version 0.8.2 and the subsequent editorial review. Repository observations are inherited
from those reviews; this document merge is not a new independent repository audit. The table
retains all 19 findings and their original severities. Its remediations reflect the final design.

The follow-up removes generated catalogue previews and a separate brief-contract version,
limits the initial fingerprint to actual grading inputs, and removes a redundant old-reader
verification requirement. It also makes the fixture the first runnable milestone, clarifies
the browser solution gate, and hides the manifest generated-arguments panel.

| ID | Severity | Hole identified in the review | Concrete remediation and acceptance evidence | Phase |
|---|---|---|---|---|
| A01 | P0 | Calling `brief()` in the API or catalogue breaks the task-code execution boundary. | Generate in a sandboxed child; validate and persist JSON; catalogue uses static AST/template checks. Verify API/discovery never imports the grader; catalogue cards show static Why/You get only. | 1 |
| A02 | P0 | `cli.seed()` preserves only existing `task.py`; a packaged empty `task.yaml` overwrites learner work. | Declare learner ownership in the adapter; preserve entire manifests on seed/update. Verify repeated seed and installed-wheel upgrade with edited and empty files. | 1–2 |
| A03 | P0 | `_task_path()`, `reset_after_commit()` and recovery assume `task.py` and Python regions. | Migrate pending resets to kind and relative learner path; adapter-driven idempotent recovery. Verify legacy migration and interrupted pass/reset for both kinds. | 1–2 |
| A04 | P0 | The “~30 lines beside Python” estimate misses API/attempt calls to cut, stub, splice, has_given, bounds, revision, solution, abandon, reset and etags. | Introduce one learner-artifact adapter and route all lifecycle consumers through it; retain Python internals and regression coverage. | 1–2 |
| A05 | P0 | Deferring manifest selfcheck breaks multi-OS CI as soon as task 271 enters the catalogue. | Land kind-aware solution/selfcheck with fixture tasks before production task authoring; require green checks on every supported OS. | 1–2 |
| A06 | P0 | Backup bundle/restore/erase use Python region operations; format 1 lets old readers silently ignore YAML. | Adapter-driven backup operations, format 2 and legacy format-1 reading; the existing old-reader equality check rejects format 2. Verify mixed round trips and preserved attempt data. | 2 |
| A07 | P0 | Monaco registers only Python, uses `.py` editor/diff URIs and always attaches the Python client. | Register YAML, expose kind/filename, select correct model/diff language and omit Python LSP for manifests. Verify the production build and kind switches. | 1–2 |
| A08 | P0 | Catalogue/doctor/TypeScript require `tier`, contradicting the proposed manifest metadata; public metadata lacks kind. | Conditional requirements, Python default kind, optional manifest tier, kind/filename in public metadata and tolerant facets. | 1 |
| A09 | P0 | Scratch `import grade` cannot find the per-task module and repeated names collide in selfcheck. | Load absolute paths under unique module names in the child. Verify multiple graders cannot reuse each other's module state. | 1 |
| A10 | P1 | The proposed `rng(SEED)` API does not exist; `_lib.rng()` is zero-argument. | Canonical manifest convention: `random.Random(seed)` inside the child; preserve existing helper compatibility. Verify deterministic generation. | 1 |
| A11 | P1 | Hashing only `grade.py` omits validator and schema changes that affect verdicts. | Fingerprint grader bytes, validator identity, Kubernetes version and schema digest; add shared task helper content only when such helpers exist. Verify each grading input change changes the recorded identity. | 1 |
| A12 | P1 | No concrete Kubernetes schema target is pinned; kubeconform defaults to `master`. | Pin a concrete version, pass it explicitly and ship matching strict schemas. Verify offline resolution with no fallback. | 1 |
| A13 | P1 | “Legal Kubernetes object” overstates OpenAPI validation. | Define the guarantee as schema validity against the pinned version plus exercise assertions; exclude API-server/controller guarantees from wording. | Design / 1 |
| A14 | P1 | Tool acquisition omits release archive extraction and installation details. | Archive SHA check, one safe expected member, executable verification/permissions, OS/arch mapping, timeouts, atomic replacement and interruption cleanup. Test failure preservation. | 1 |
| A15 | P1 | Existing packaging includes tasks/web assets but not schemas. | Include schema data in wheel/sdist and Docker; verify real installed artifacts contain the same version/digest and work offline. | 2 |
| A16 | P1 | Recomputing a brief from the seed after an upgrade can change an open attempt's question. | Persist the exact brief and spec with generation revision; grade/render against stored data, retain input compatibility and preserve attempts on incompatibility; no separate contract version. Verify restart/upgrade/restore behavior. | 1–2 |
| A17 | P1 | `str.format()` on YAML has quoting/type hazards beyond README brace escaping. | Scalar-aware solution renderer with defined placeholder positions; parse and grade output. Cover difficult scalar values in selfcheck. | 1–2 |
| A18 | P1 | “Several seeds” samples satisfiability rather than proving it. | Document deterministic corpus and branch/boundary coverage; exhaust small meaningful domains where practical and state the limit of sampled evidence. | 1–2 |
| A19 | P2 / Docker | Hadolint CLI diagnostics do not supply the instruction AST required by semantic assertions. | Choose and validate a separate parser/API before Docker tasks; define its instruction model, pin/fingerprint it and test semantic checks independently of lint diagnostics. | 4 |
