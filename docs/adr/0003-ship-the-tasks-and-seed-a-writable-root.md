# Ship the tasks inside the package and seed a writable root from them

"Local ready" says a `docker run` or an install gives you a ready environment. Neither did. The
wheel packaged `src/drillion` and nothing else — eleven modules, no tasks, no page — so `uvx
drillion` was a CLI with an empty catalogue. The image baked `web/dist` but not `tasks/` and set
`DRILLION_ROOT=/data`, so `docker run` told you to "run drillion from the repo", which is the
clone-and-build shape a published image exists to remove (#38).

What makes this more than a packaging line: `tasks/` is not read-only content. The learner's code
lives *in* `tasks/<slug>/task.py` — `region.write_region()` rewrites it on every save, and
`runner.selfcheck()` writes and removes `_selfcheck.py` in all 171 folders. Wherever the tasks
live, that place has to be writable.

## Considered options

**Read the tasks straight out of the package.** Rejected: `site-packages` is the wrong place to
write a learner's code to, and is frequently not writable at all. The same objection sinks a
read-only bind mount in the container.

**Keep making people bring their own `tasks/`.** Rejected: that is the clone, and it makes the
published artefacts pointless.

**Ship a pristine template and seed a writable root from it.** Taken. `force-include` puts
`tasks/` into the wheel as `drillion/_tasks` and `web/dist` as `drillion/_web`; `cli.seed()` copies
the template into `settings.root` when that root has no `tasks/`, and does nothing at all when it
has. `settings.root` keeps its meaning and, in a checkout, its value.

## Consequences

- **A checkout is untouched.** The template exists only inside a built wheel, so `seed()` returns
  before it looks at anything. Same root, same `tasks/`, same `progress.json`.
- **An upgrade cannot eat saved code.** A root with `tasks/` is left alone, whole. The cost is
  that tasks added by a later drillion do not reach an already-seeded root; filling in only the
  missing folders is the upgrade path if that starts to matter.
- **Installed, the root is a per-user data directory** (`XDG_DATA_HOME`, `Application Support`,
  `LOCALAPPDATA`) rather than the old fallback, which pointed inside `site-packages`.
- **The build now has an ordering rule.** Hatchling errors on a forced include that is missing, so
  `web/dist` must exist before the wheel is built — hence the committed `web/dist/.gitkeep`, and
  `artifacts` on the sdist target, because a bare `uv build` builds the wheel from the sdist.
