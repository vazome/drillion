# Untrack progress.json, so a clone ships no practice history

`AGENTS.md` makes two claims about the same file that cannot both hold. "Always open source" says
anybody can freely clone and use drillion. "Local ready" says upgrades must not cost a learner
their progress. `progress.json` was tracked, and the committed copy was the maintainer's real
practice — cards, log entries, archived solutions. Every clone inherited someone else's ladder, and
the maintainer's own `git pull` collided with the maintainer's own file (#4).

## Considered options

**Keep it committed.** Rejected on two counts:

1. **It is right for one person, wrong for a project meant to be cloned by strangers.** "It is
   your work" was never the maintainer's work to ship to everyone who runs `git clone`.
2. **It cannot scale past one contributor.** Two people running drillion from the same clone would
   fight over the same tracked file every session either of them had.

**Untrack it, ship nothing, no migration.** Taken. `state.load()` already returns a full default
dict — empty cards, open attempts, log and archive — when the file is absent, so a fresh clone
needs no seeding code. An existing install's file does not change shape, so it reads back exactly
as it did before. `.gitignore` already excluded the `.bak` file next to it; `progress.json` joins
it.

## Consequences

- **A fresh clone starts with an empty ladder.** No cards, no log, no archived solutions — the
  learner's own practice, not the maintainer's, from the first session.
- **An existing install keeps its file, untouched, with no migration step.** Nothing about the
  file's format changed and `state.load()` never required it to be tracked, so upgrading is a
  no-op for anyone who already has a `progress.json` on disk.
- **The conflict on upgrade is the mechanism, not a wart.** Git deletes an untracked-upstream file
  on its own only when the local copy is unmodified — that is, only when there was no real
  practice to lose. Anyone with actual history gets a modify/delete conflict on `progress.json`
  instead, and the correct resolution is to keep the local file: it is the only copy of that
  person's work, and nothing in drillion can rebuild it.

Closes #4.
