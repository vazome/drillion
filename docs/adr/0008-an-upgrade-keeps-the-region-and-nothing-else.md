# An upgrade keeps the region, and drillion takes back only what it shipped

ADR 0003 seeded a writable root from the packaged tasks and left a root that already had
`tasks/` alone. That grew into seeding on every run, so READMEs, `_lib.py` and the test files
follow the installed version — with one carve-out: `task.py` was skipped whole, because the
learner's code is in it.

Skipping it whole was too blunt. `task.py` holds the learner's region *and* the grader below the
marker, so a task anyone had ever opened kept its original machinery for good. A fixed case
generator, a corrected signature, a reworded docstring: none of it reached the people already
practising that task, which is exactly the population it was fixed for.

The prune had the mirror problem. Everything under `tasks/` that the template did not contain was
deleted, deepest first, so a slug drillion had retired left no trace — and so did a task the
learner had written themselves, silently, on the next run.

## Considered options

**Leave `task.py` alone and ship grader fixes as new task numbers.** Rejected: renumbering is the
curriculum order (ADR 0005), and a typo in the machinery is not a new exercise.

**Rewrite `task.py` whole and back the old one up.** Rejected: it makes every upgrade a small data
loss the learner has to notice and undo.

**Splice.** Taken. `backup.restore` already moves a region from one version's machinery into
another's; an upgrade is the same move with the version on disk. `seed()` reads the packaged file,
splices the learner's region into it through the same `region.validate` gate the editor uses, and
writes it atomically. A region that will not fit — an edit outside the region, a signature that
moved — leaves the file untouched and names it in the log.

**Record what was shipped.** Taken, for the prune. `tasks/.shipped` lists the paths the last run
put there. Only a path in that record and no longer in the template is drillion's to take back, so
a task the learner added is never in the record and never touched. A whole task the version has
dropped moves to `tasks/_retired/<slug>/`, which the catalogue skips, instead of being deleted.

## Consequences

- **Grader fixes reach everyone**, including the learner mid-attempt on that task. The region they
  wrote is the only thing carried across.
- **A task file can now be left behind.** A region that no longer fits keeps the old machinery
  rather than losing the work; the log says which task and why, and `drillion doctor` still reports
  a task that cannot be read.
- **A root seeded before `.shipped` existed prunes nothing on its first run** — there is nothing to
  compare against. It gets the record, and the run after that behaves normally.
- **Retired work is on disk, not in a backup.** `backup.bundle()` only carries regions for tasks
  this version ships, so `_retired/` is the only copy. That is a directory the learner can read.
