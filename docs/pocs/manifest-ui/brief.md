# Manifest task UI — proof of concept

You are working in an isolated git worktree on branch `poc/manifest-ui`. Nothing here
ships. The maintainer wants to see what a manifest (Kubernetes YAML) practice task should
feel like, and will keep whatever sticks.

## What already exists

drillion is a local Python practice app. A recent branch taught it a second task **kind**:
`python` (edit a region inside `task.py`) and `manifest` (write a whole `task.yaml`,
graded by kubeconform plus a per-task `check()`).

The client work done so far was deliberately minimal — five edits, enough to stop the
python language server attaching to YAML and to hide the generated-arguments panel:

- `web/src/Editor.tsx` — file name derives from kind (`task.yaml` vs `solve.py`), LSP only
  starts for python
- `web/src/Task.tsx` — hides the python-only panel, fences the reference answer as yaml
- `web/src/Catalogue.tsx`, `web/src/ds/TaskPath.jsx` — a manifest carries a `track`
  (`kubernetes`) where a python task carries a `tier` (`core`/`advanced`/`packages`)
- `web/src/api.ts` — `kind` on the task meta, `tier` now optional

Nobody has designed the manifest experience. That is this POC.

## Run it and look at it

A real, clickable manifest task (the app has no such task in `tasks/` yet — this points it
at a throwaway one and stands in for the kubeconform binary, whose checksums are not
pinned yet):

```bash
cd /tmp/drillion-ui-poc
uv run python /tmp/claude-1000/-home-daniel-github-drillion/2213b00c-88a5-42b7-8ad0-945b70db3a45/scratchpad/preview_manifest.py
# http://127.0.0.1:8770/   — task 271_first_deployment
```

It needs `pnpm --dir web build` first (the server serves `web/dist`, not a vite dev
server). If your sandbox refuses to bind or connect to a local socket, say so in your
report and work from the code and from `curl` against the API shapes below; do not fake
having run it.

The sitting asks for something different every time it opens: "a Deployment named
`checkout` with 2 replicas", then `billing` with 4, and so on. Submitting wrong YAML
currently returns **raw pytest output** — a traceback about a YAML document — which is the
single ugliest thing in the flow.

## Where the opportunities are, roughly ranked

Pick what you think matters. You are not required to do all of it, and you may do
something not on this list if it is better.

1. **Failure output.** A learner who typed `replicas: "2"` gets a pytest traceback. What
   should they get? kubeconform returns structured errors (a path like `/spec/replicas`
   and a message); `check()` failures carry an assertion message (`"name"`, `"replicas"`).
   `web/src/ds/FailedCase.jsx` is how python failures are shown — a manifest is not a
   failed case with arguments, so it likely wants its own shape.
2. **The requirements.** "You return: a Deployment named `checkout` with 2 replicas" is one
   markdown line. It is the whole question, and it is generated per sitting. Should it be
   a checklist the learner can tick against? Should the parts that vary be visually
   distinct from the parts that do not?
3. **Writing YAML from nothing.** The editor opens empty with no language server, no
   completion, no snippet. A blank buffer is a real wall for someone who has never typed a
   Deployment.
4. **The catalogue.** A kubernetes track sitting among 267 python tasks.

## Hard constraints

- **Stack is fixed.** React 19, Vite, CSS Modules, a local design system in
  `web/src/ds/` with tokens in `web/src/ds/tokens/`. **Do not add any dependency** —
  no Tailwind, no shadcn, no component library, no router, no state library. Use the
  existing `ds/` components (`Card`, `Band`, `Collapsible`, `ResultBanner`, `StatusBadge`,
  `Tip`, `TagChip`, …) and the existing tokens. New styling goes in a CSS Module beside
  its component.
- **No "hacker" aesthetic.** No black-and-green terminal palettes.
- **Read before you write.** `web/src/Task.tsx`, `web/src/Editor.tsx`, and two or three
  `ds/*.jsx` + their `.module.css` show the house style. Match it.
- **`pnpm --dir web build` and `pnpm --dir web lint` must pass.** Run both.
- **Never write into `tasks/`.**
- **Python side is off limits** unless a UI change genuinely needs an API field. If it
  does, keep the change small, say so loudly in your report, and remember `api.py` must
  never name a kind — kinds are dispatched through `src/drillion/kinds.py`.
- **Commits:** `git commit --no-gpg-sign`, conventional titles (`feat(web): …`), no
  co-author or "generated with" footers, no em dashes anywhere. Commit as you go.
- Do not push. Do not merge. Do not touch the `docs/config-authoring-design` branch.

## Report

Write `/tmp/drillion-ui-poc/docs/pocs/manifest-ui/report.md`: what you changed and why, what you tried
and rejected, whether you managed to actually run and look at the app, and what you would
do next. Screenshots are welcome if you can take them (`pnpm --dir web screens` runs
Playwright and already has a config).
