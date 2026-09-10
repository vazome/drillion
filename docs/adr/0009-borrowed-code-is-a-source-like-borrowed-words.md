# Borrowed code is a source, the same way borrowed words are

89 of the 201 tasks adapt Exercism. Each one carries Exercism's Markdown **verbatim**, a
`source:` field and a closing attribution line, because the problem posed is theirs and the
prose is the copyrightable part of it.

[#226](https://github.com/vazome/drillion/issues/226) proposes three sources that invert
that. `TheAlgorithms/Python` and `fluentpython/example-code-2e` have no problem statements at
all: they are reference implementations, mostly doctested, which is exactly the artefact
`_reference()` needs and the artefact every other source makes an author write. drillion would
take the code and write the words, which is the opposite of what it does today.

The research note behind this is
[docs/research/2026-09-09-task-sources-beyond-exercism.md](../research/2026-09-09-task-sources-beyond-exercism.md),
where every licence was read from the repository's own `LICENSE` rather than a summary.

## Considered options

**Treat borrowed code as a different thing that needs its own rule.** Rejected, and the
reasoning is the whole point of this ADR. Taking an MIT-licensed implementation into
`_reference()` is a *smaller* claim than the one drillion already makes 89 times. MIT grants
reuse outright and asks for the notice to travel with substantial portions. Copying a problem
statement verbatim is the harder case, and it is the case already handled. A source field that
covers the words covers the code.

**Attribute every borrowed line.** Rejected as noise. `103_deporder` hand-rolls a topological
sort; rewriting it as four lines of `graphlib.TopologicalSorter` is not an adaptation of
anyone's implementation, and a `source:` on it would say nothing true.

**One test, on substance rather than on which half was copied.** Taken. If the borrowed
implementation is a substantial portion of `_reference()`, the task carries `source:`, the
closing attribution line and a `NOTICE` entry, whether what was borrowed is the words, the
code, or both. If it is not, it carries none of them. That is the MIT condition restated, and
it happens to be the CC-BY condition too.

## Consequences

- **`source:` means provenance, not prose.** `docs/authoring-tasks.md` says so, and the
  existing field, footer and `NOTICE` machinery is unchanged. Nothing has to be built.
- **0BSD sources are exempt.** Code in the CPython documentation requires no attribution at
  all. The surrounding prose is the PSF licence and is not 0BSD, so the rule for that well is
  the same one either way: adapt the example, write the words fresh.
- **Algorithms are in, judged one at a time.** AGENTS.md already supplies the test, and it is
  not "is this an algorithm": it is whether solving it makes someone better at Python. BFS over
  a dict of lists practises `deque`, set membership and dict iteration, and is Python a person
  would write. A segment tree practises index arithmetic nobody writes in Python. That lands
  `TheAlgorithms/Python` near 25 tasks rather than 60, and it needs no new rule.
- **`advanced` grows, and that is a symptom.** It is 22 of 201 today *because* the object model
  past `@property` is missing. Descriptors, ABCs, `Protocol` and `__slots__` all meet the tier's
  own definition, so the count moves as the gap closes. It is not a target to hit.
- **Numbering is unchanged.** [ADR 0006](0006-the-fundamentals-come-first.md) already ruled that
  a new task appends. A block of this size widens the gap between folder order and curriculum
  order, and that was accepted there. The invariant that matters is machine-checked either way:
  `doctor` reports a prereq that names a later task.
- **Scope is a pilot, not a batch.** The three sources are 75 to 110 tasks. The first
  landing is three, from `fluentpython/example-code-2e`, to find out whether the inverted
  adaptation survives the folder contract before the other seventy are written against it.
