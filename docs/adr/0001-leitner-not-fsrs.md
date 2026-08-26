# A fixed Leitner ladder, not FSRS

`AGENTS.md` says the UX must reflect spaced repetition "(FSRS)", and FSRS is the obvious choice —
it is what Anki ships. We tried it and rejected it: drillion schedules a **skill practised on
freshly generated data**, not a memory of a fixed item, so FSRS's central quantity — the
probability of recalling *this* card — is not a thing drillion can measure. Passing a task returns
it in 2 → 4 → 8 → 16 → 28 → 60 → 120 days, and that list is the whole scheduler.

## Considered options

**FSRS.** Rejected on four counts, in order of weight:

1. **The recall model does not apply.** Every task regenerates its data each sitting, so the exact
   answer you gave last time never existed. FSRS estimates retrievability of a specific memory
   trace; there is no trace here to decay.
2. **It needs self-reported grades.** FSRS is driven by Again/Hard/Good/Easy. drillion computes
   the **grade** from runs, active seconds and whether the solution was taken — deliberately, and
   for a reason recorded in `docs/how-it-works.md`: self-rating is how people finish a
   curriculum and still cannot code.
3. **It cannot be fitted here.** FSRS's parameters want a corpus of review history. One user, 171
   cards, a season of practice — the weights would stay at their defaults forever.
4. **Those defaults are wrong for this.** With stock settings a task passed three times returns in
   46 days, then 90. FSRS is tuned for vocabulary over years, where a lapse costs one word. Over a
   season, Cepeda 2008 puts the optimal gap at 10–20% of the retention interval, which is a number
   you can write down instead of fit.

**A fixed ladder.** Taken. Seven integers, no dependency, and the cost of mistuning it is bounded:
too-short intervals over-review a little, where a mistuned FSRS silently drops material for a
quarter.

## Consequences

The ladder is deliberately cruder than FSRS. Two of the differences below were real gaps, both
now closed; the third is a decision. All three are recorded so they are decided rather than
discovered:

- ~~**A struggle never demotes.**~~ Closed (#1): `struggled` is worth `-1`, so a card that
  fights you walks back down a box a sitting, with box 0 as the floor. Not classic Leitner's
  back-to-box-1, because `struggled` is drillion's grade for anything slow, anything over two
  runs and anything peeked — common enough that one bad sitting must not cost a month of
  laddering. Each struggle is also counted on the card (#9), and reaching `LAPSE_LIMIT` flags
  the task rather than punishing the schedule further.
- ~~**Nothing ever graduates.**~~ Closed (#2) by the tail: while 28 was the ceiling, every card
  you had mastered came back monthly, so review load only ever grew, toward all 171 cards on a
  monthly cycle. `LADDER` now runs on to 60 and 120, which sheds that load without inventing a
  status for "retired" — a done card you keep getting right simply comes back rarely.
  `REVIEWS_PER_DAY` (#7) bounds what any one day can cost you on top of that.
- **`difficulty` deliberately does not reach the scheduler.** Every task declares
  `easy`/`medium`/`hard`, graded against `docs/difficulty-rubric.md`, and the ladder treats all
  three identically. This is the one place drillion declines FSRS's shape on purpose rather than
  for lack of data: difficulty is signposting for the person choosing a task, so they know what it
  will cost them before they open it. What matters is that they practise, not which label the task
  carried.

The first was a gap and is now closed; the second is still a gap, and no longer a change to
`scheduler.py` alone; the third is settled. Reopen this decision if the remaining fix stops being
small, not because FSRS is fashionable again.
