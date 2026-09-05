# Difficulty rubric

How `difficulty:` is decided in a task's frontmatter. All 182 tasks in the catalogue were graded
against this rubric; grade a new one against it too, so the levels keep meaning the same thing.

You are grading how hard a task is to **solve correctly the first time**, for someone learning
Python who has met the concept before but has not automated it.

**Difficulty is not length.** A task that takes 30 minutes of typing but never makes you stop and
think is `easy`. A task you can write in six lines but only after you see the trick is `hard`.
Par time is deliberately not given to you — do not try to infer it.

## easy
One concept, applied the way it is normally applied. The rules hold no surprises: no ties to
break, no empty-input trap, no ordering subtlety, no mutation hazard. If you know the syntax you
are done; if you don't, the hints teach it in one step.

## medium
Either two or more concepts have to work together, **or** one concept meets an edge case that
actually bites — empty input that must not crash, a tie that must break a specific way, an
ordering the naive solution gets wrong, aliasing/mutation of the caller's data, an off-by-one,
a type the grader compares with `is`. The shape of the solution is obvious; getting it right
is not.

## hard
You must make a real decision before you can start writing — pick an algorithm, pick a data
structure, design a small state machine, or work out an invariant. Or several moving parts have
to stay consistent with each other. Or the task hides a requirement that only shows up when you
reason about it (a stop condition, a stable sort, a class the grader identity-checks, a
concurrency or resource constraint).

## Calling it
- Anchor on the `## Rules` section. Rules are where the traps live. A long `## You get` with a
  short, unsurprising `## Rules` is usually `easy`.
- A rule that starts "the moment you meet…", "leave the input alone", "must hand back a real
  `bool`", "which falls out for free if…" is a trap being disclosed — that is at least `medium`.
- Returning a *class* or a *function* rather than a value is at least `medium`.
- Ignore how interesting the story is. Ignore how many words the task uses.
- When genuinely torn between two levels, pick the lower one.
