# The fundamentals come first, and this is the last renumbering

[ADR-0005](0005-task-numbers-are-the-curriculum-order.md) made a task's number its curriculum
position, derived from the concepts each task's page shows the learner. It was right about the
edges it could see and wrong about the ones it could not. The detector only linked a concept to a
task that already taught it, so nothing tied "task 008 iterates a dict" to "task 106 is the dicts
task", and the sort had no reason to move either one.

The result was a ladder whose rungs were in the wrong order. Measured on the code tasks actually
show, and on their reference solutions:

- `list.append` appeared in 23 reference solutions from task `003` on. The lists task was `097`.
- `while` appeared in 13 reference solutions from `043` on. No task taught it at all until `172`.
- `dict.items` from `008`; the dicts task was `106`. `range()` from `006`; loops was `101`.
- Task `002`'s own reference was `[f"{k}={v}" for k, v in pairs]` — a comprehension from task `005`
  and an f-string from task `017`, inside the answer to the second task in the catalogue.

The cause was structural. The 84 Exercism tasks are a designed beginner syllabus and they all sat
at `088`–`171`, behind 86 tasks of closures, decorators, `asyncio` and `functools`, because
minimal-churn only moves a task when an edge forces it and there were no edges to force it.

## Considered options

**Re-derive the whole order from the concept graph.** The graph is 2485 edges over 182 tasks once
the basics are in the concept map, and every ordering that minimises violated edges puts something
absurd at the front: `008_typehints` first, or `asyncio` at position 29. Optimising an edge count
is not the same as teaching, and a curriculum whose first task is chosen by a heuristic is worse
than one whose first task is chosen. Rejected, after building it and looking at the output.

**Move the Exercism block in front of the pyops block, both untouched.** Explainable in one
sentence, and it halves the violated edges. But it drags the tasks that teach f-strings, slicing
and `sorted` behind the beginner tasks that use them, and made four concepts worse than they were.
Rejected.

**Keep both designed sequences, and interleave only what has to move.** Taken. Exercism's basics
syllabus (`088`–`122`) goes to the front in its own order, because it was authored as a first
course and reads like one. Six tasks from the pyops set are folded into it at the point of first
use: `slicing`, `f-strings`, `sorted`, `enumerate`/`zip`, `unpacking` next to the Exercism
unpacking pair, and `comprehension` immediately after the loops pair rather than before it — a
comprehension is a loop written short, and the graph's preference for putting it earlier is the
one place the graph was overruled on purpose. `172_batchbudget`, the new `while` task, sits with
the loops it belongs to. Everything else keeps its relative order.

Violated edges fall from 884 to 336 of 2485. Concepts taught more than ten places after their first
use fall from 16 to 5, and the worst gap from 159 places to 28.

## Consequences

- **Progress orphans a second time.** Slugs are the progress key, so every card is lost again. This
  is the second time and it is the last: the same trade ADR-0005 made, taken again only because it
  was still nearly free and the alternative was shipping a first task that assumes two later ones.
  From here a new task appends, and a concept that belongs earlier is a reason to write a new task,
  not to move the ones that exist.
- **`doctor` now enforces what the number means.** A prereq that names a later task is a reported
  problem, alongside dangling references and cycles. The invariant that made this ADR necessary is
  no longer a convention nobody checks.
- **Nine prereqs were dropped rather than satisfied.** Each was a derived edge from ADR-0005's pass
  that pointed the wrong way once the beginner tasks came first: the Exercism sets task gated on the
  pyops sets task, blackjack's comparisons gated on classes, the lasagna timer gated on
  `try`/`except`. They encoded "this page shows one" rather than "you cannot start without it".
- **Numbers are contiguous again, `001`–`182`.** ADR-0005 retired `087` and left a gap; the
  renumbering closes it, so the id is once more exactly the position.
- **The order is defensible, not optimal.** Five concepts are still taught after something uses
  them, the largest being `unpacking` at 29 against a tuple assignment in task 1. Closing those
  means writing tasks, not moving them, which is the work #181 tracks.
