# A fixed 5-box Leitner ladder, not FSRS

`AGENTS.md` says the UX must reflect spaced repetition "(FSRS)", and FSRS is the obvious choice —
it is what Anki ships. We tried it and rejected it: drillion schedules a **skill practised on
freshly generated data**, not a memory of a fixed item, so FSRS's central quantity — the
probability of recalling *this* card — is not a thing drillion can measure. Passing a task returns
it in 2 → 4 → 8 → 16 → 28 days, and that list is the whole scheduler.

## Considered options

**FSRS.** Rejected on four counts, in order of weight:

1. **The recall model does not apply.** Every task regenerates its data each sitting, so the exact
   answer you gave last time never existed. FSRS estimates retrievability of a specific memory
   trace; there is no trace here to decay.
2. **It needs self-reported grades.** FSRS is driven by Again/Hard/Good/Easy. drillion computes
   the **grade** from runs, active seconds and whether the solution was taken — deliberately, and
   for a reason recorded in `README.md`: self-rating is how people finish a curriculum and still
   cannot code.
3. **It cannot be fitted here.** FSRS's parameters want a corpus of review history. One user, 171
   cards, a season of practice — the weights would stay at their defaults forever.
4. **Those defaults are wrong for this.** With stock settings a task passed three times returns in
   46 days, then 90. FSRS is tuned for vocabulary over years, where a lapse costs one word. Over a
   season, Cepeda 2008 puts the optimal gap at 10–20% of the retention interval, which is a number
   you can write down instead of fit.

**A fixed ladder.** Taken. Five integers, no dependency, and the cost of mistuning it is bounded:
too-short intervals over-review a little, where a mistuned FSRS silently drops material for a
quarter.

## Consequences

The ladder is deliberately cruder than FSRS. Two of the differences below are real gaps; the third
is a decision. All three are recorded so they are decided rather than discovered:

- **A struggle never demotes.** `struggled` is worth `+0`, so a card that fights you every time
  holds its box and its interval. Classic Leitner sends a failed card back to box 1; this ladder
  has no negative step at all.
- **Nothing ever graduates.** Box 4 returns every 28 days forever. Review load therefore only ever
  grows, toward all 171 cards on a monthly cycle, and a task you have mastered is never retired.
- **`difficulty` deliberately does not reach the scheduler.** Every task declares
  `easy`/`medium`/`hard`, graded against `docs/difficulty-rubric.md`, and the ladder treats all
  three identically. This is the one place drillion declines FSRS's shape on purpose rather than
  for lack of data: difficulty is signposting for the person choosing a task, so they know what it
  will cost them before they open it. What matters is that they practise, not which label the task
  carried.

The first two are gaps and each is a small change to `scheduler.py`; the third is settled. Reopen
this decision if those fixes stop being small, not because FSRS is fashionable again.
