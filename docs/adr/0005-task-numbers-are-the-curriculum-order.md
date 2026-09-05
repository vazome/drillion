# Task numbers are the curriculum order, at the cost of existing progress

Task `001` taught f-strings. Its own "You get" example unpacked a tuple, and its hints reached for
`str.join`. Both concepts lived further up the ladder, at `005` and `026`. The scheduler was not at
fault: it gates on `prereqs`, and the pyops block declared almost none, so serving `001` first was
a legal move over the graph it was given. The number in the folder name looked like an order and
was not one.

"Categorical pragmatism" says drillion's job is to get people better at Python, and value #4 says
the design must reflect spaced repetition, where topics span tasks and build on each other. A first
task that assumes two later ones is the failure mode both of those exist to prevent, and no amount
of scheduler tuning fixes it while the graph itself is empty.

## Considered options

**Author the missing prereqs by hand and leave the numbers alone.** Cheapest to ship and it
preserves every slug. Rejected because it leaves two orders in the repo, the real one in `prereqs`
and a decorative one in the folder names, and the decorative one is the one a person reads when
they browse `tasks/`. The next task written by hand would drift again the same way.

**Derive the graph, then renumber to match it.** Taken. The dependency edges come from the code
each task actually shows the learner (fenced python blocks, inline spans, the stub), unioned with
the authored prereqs, then a minimal-churn topological sort assigns numbers. 40 of 171 folders
move. Every prereq now points strictly backwards, verified, zero forward edges, so a task's number
is its curriculum position and `drillion doctor` can keep it that way.

**Renumber, and ship a slug migration.** Rejected. Slugs are the progress key in `state.py`, so
renumbering orphans existing cards, and a migration would be a permanent table mapping old slugs to
new ones, carried forever to serve installs that exist today in alpha. That is machinery bought for
one event.

## Consequences

- **Existing cards orphan.** This crosses "Local ready", which says learning progress must be kept
  regardless of distribution line, and it is the one value this decision knowingly spends. It was
  taken on maintainer sign-off, on the grounds that the project is pre-1.0 and the practice history
  at risk is small, and it should not be taken a second time. Once someone other than the
  maintainer has a `progress.json` worth keeping, renumbering is off the table and the answer
  becomes a stable task id decoupled from the folder name.
- **The number is now load-bearing.** Inserting a task between two others means renumbering
  everything after it, which is the cost of the number meaning something. In practice a new task
  goes at the end of the run of its topic and declares its prereqs, and only a genuinely earlier
  concept forces a shift.
- **The derived graph only sees concepts some task already teaches.** The detector links a concept
  to the task that teaches it, so a concept taught by no task (`while`, `lambda`, `map`/`filter`,
  `match`, the walrus, `bytes`) produces no edge and no gap report. The order is now correct over
  the tasks that exist; whether the tasks that exist cover Python is a separate audit, opened as #181.
