# Manifest UI proof of concept

Worktree: `/tmp/drillion-ui-poc`
Branch: `poc/manifest-ui`

## What I built

The POC concentrates on the manifest task workspace, especially the transition from an empty file to useful feedback.

- **A manifest brief.** The task's full, server-rendered Markdown stays intact inside a quieter brief panel, with a blue rule, explicit `task.yaml` identity, highlighted inline values, and a short explanation of Run versus Submit. Generated requirements continue to come from the current sitting; nothing is hardcoded to checkout, billing, or a replica count.
- **An optional YAML outline.** A collapsible guide offers an incomplete resource envelope. It opens for an empty draft, explains indentation, and leaves all answer values to the learner. Insert is disabled for a nonempty draft, a conflict, a restore offer, an in-flight run, or a passed task. An untouched inserted outline can be removed. Edited drafts stay intact. This uses the existing draft/save flow.
- **Manifest-specific failure feedback.** Reported JSON-pointer paths appear beside their messages. The quoted-integer example explains how a number differs from a string. The fixture's name, kind, and replicas assertions point back to the sitting's requirements. YAML parsing errors and unfamiliar failures receive separate, cautious explanations. The complete raw report remains under Validator details.
- **A smaller manifest editor viewport.** The editor shares room with its guide and result rather than retaining the height intended for the simpler Python workspace.
- **Editor startup synchronization.** Value and read-only effects also run when the asynchronous editor becomes ready, so an early outline insertion reaches the model and a completed task remains read-only.

New styling lives in `ManifestWorkspace.module.css`. The design reuses Card, Collapsible, Button, SpecText, and the existing result components. It retains IBM Plex Sans, Spline Sans Mono, and the existing white/slate/blue tokens, including their dark-mode equivalents. There are no new dependencies, Python changes, API changes, or changes under the repository's `tasks/` directory.

## Choices, alternatives, and limits

I rejected a client-generated requirement checklist: the API gives the UI authored prose, not structured requirements with individual verdicts. Ticking inferred items could imply checks the grader never performed. I kept the complete specification instead of extracting a sentence with a brittle Markdown regex.

I rejected a prefilled Deployment answer or a full Kubernetes completion system. A generic, explicitly incomplete outline lowers the blank-buffer barrier without revealing this sitting's solution, adding a dependency, or pretending to offer schema-aware completion.

I left the catalogue unchanged. Its existing track support is sufficient for this focused experiment; feedback and the first edit are the higher-value exploration.

The feedback adapter recognises the current API's pytest headline format. It is deliberately small and has a neutral fallback, but is not a structured diagnostic API. Headlines are limited upstream, so the UI does not claim to list every problem or mark unreported fields as correct. The raw report remains available. A future durable implementation should carry diagnostics through the kind dispatch layer rather than expanding frontend traceback parsing.

## Verification

- `pnpm --dir web build`: **passed**, including TypeScript. Vite reported PostCSS, browser externalization, and large-chunk warnings; these did not fail the build.
- `pnpm --dir web lint`: **passed**.
- `node --test web/tests/manifest-feedback.test.mjs web/tests/css-modules.test.mjs`: **passed**, both test files. Coverage includes multiple field messages, requirement assertions, malformed YAML, unknown checker errors, rendered guidance, and preservation of sitting-specific prose.
- `git diff --check`: **passed**.

The worktree initially had no installed dependencies. The default pnpm launch failed against its inaccessible shared SQLite store. I copied the existing installed `node_modules` into this worktree, used the installed Node 22 and pnpm 11.24.0 executables, and set `PNPM_CONFIG_VERIFY_DEPS_BEFORE_RUN=false` for the successful commands. No package manifest or lockfile changed. The temporary dependency symlink was replaced by a local copy before successful builds.

### App and browser status

**I could not use or visually inspect the running app. No screenshots were captured.**

The supplied `uv run` command failed while downloading an unavailable dependency because DNS/network access was restricted. A local copy of the preview launcher, using the existing Python environment and this worktree's source, subsequently printed successful Uvicorn startup on port 8770. However, this sandbox would not allow the client to connect to that local socket: curl failed, and repeated HTTP requests also failed with server and client launched together. The server was stopped afterward.

The browser script therefore never reached the app. Build and static component checks are not evidence of visual, keyboard, or end-to-end correctness. The preview also uses the brief's kubeconform stand-in, not real Kubernetes schema validation.

### Surface review

- Entry points: the shared Task screen serves direct task links and normal task navigation. Run/Submit buttons and their editor shortcuts use the same existing handlers. No Settings or command-palette feature was added.
- Client: web only. New styles use wrapping layouts and existing theme tokens; narrow-screen and dark-mode appearance still need visual review.
- Reverse states: an untouched outline can be removed, help can be collapsed/reopened, and raw diagnostics can be expanded/collapsed. Existing abandon, archive, pass, and draft-conflict flows are retained.
- Connection modes: no transport changes or new endpoints. Existing draft conflict and restore guards also disable outline insertion. Remote, relay, tunnel, and multi-device behavior were not exercised.

## Commits

**No commits could be made.** I attempted:

```sh
git add web/src/Editor.tsx web/src/Task.tsx web/src/ManifestWorkspace.tsx web/src/ManifestWorkspace.module.css web/src/manifestFeedback.ts web/tests/manifest-feedback.test.mjs
git commit --no-gpg-sign -m 'feat(web): guide learners through manifest practice'
```

Both operations failed because Git could not create:

```text
/home/daniel/github/drillion/.git/worktrees/drillion-ui-poc/index.lock
Read-only file system
```

The worktree's Git metadata is outside its writable sandbox. All implementation files and this report remain uncommitted in the requested worktree. Nothing was pushed, merged, or switched to another branch. The supplied brief is preserved.

## What I would do next

1. Run the preview in an environment with reachable local sockets. Review desktop, narrow-screen, dark-mode, keyboard focus, outline insertion/removal, and actual malformed/incorrect/passing submissions.
2. Decide whether the generic outline gives beginners enough help. If not, explore task-authored starter guidance without exposing the reference answer.
3. If the feedback design sticks, introduce structured diagnostics through kind dispatch, preserving unknown-error and raw-report fallbacks.
4. Commit the reviewed POC once the existing worktree's Git metadata is writable.
