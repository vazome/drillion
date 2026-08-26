# How a sitting works, and why it works that way

## The loop

1. **Today** shows due reviews first (most overdue first), then up to 2 new tasks whose
   prerequisites you have passed. The whole catalogue is open too — the queue is a suggestion.
   Not in the mood for one of them? **Bury** it and it is gone for the day and back tomorrow,
   in the same box and on the same due date. The Buried band in Today undoes it early.
2. Opening a task starts an **attempt**: a fresh seed and an active-seconds timer that pauses
   when the tab is hidden. The left pane renders the task's `README.md` — Why / You get /
   You return / Rules / Read first — and the right pane is the editor with the stub.
3. **Run** saves your region into the file and runs that file's pytest test with the attempt's
   seed. Failures come back with the assertion lines mapped to editor line numbers.
4. **Hints** unlock one level per 60 active seconds; the **solution** unlocks after 3 attempts
   and 10 minutes, and taking it means the pass cannot promote the card.
5. **Pass** → computed grade → the card moves on the ladder → your code is archived into
   `progress.json` → the file is reset to the stub, so the next review starts blank.
6. The spec pane carries a **note**, one free-text box per task, saved as you type. It belongs
   to the task and not to the sitting: it survives a grade, a re-attempt and an abandon.

## Why

**Fresh data every sitting.** Each task ships a generator, so when a task comes back in 8 days
the IPs, names and numbers are different. You can't recall the answer because that exact answer
never existed. This is the one feature that stops spaced repetition from degrading into
memorising files.

**A 5-box ladder, not a fancy algorithm.** Pass a task and it returns in 2 → 4 → 8 → 16 → 28
days. Only a pass moves a card: a failing run costs an attempt and nothing else, and a pass you
took the solution for grades `struggled`, which leaves the card where it was. FSRS was the
obvious choice and was tried and rejected — see
[ADR 0001](adr/0001-leitner-not-fsrs.md) for the four reasons.

**Grades are computed, not self-reported.** First try under par = `quick` (+2 boxes). Two tries
= `pass` (+1). Slow, or three-plus tries = `struggled`. Looked at the solution = never promotes,
regardless of the tests going green. That last rule is the important one: hint-assisted passes
are how people finish a curriculum and still can't code.

**Par time is the grader's, not yours.** `minutes:` lives in each task's frontmatter because
`grade_of()` needs it to decide `quick`. It stops at the server: it is not in the browser
payload and not on any screen. The timer counts up and never turns a colour at some number you
were supposed to beat. Watching a clock you cannot meet is not information, it is pressure.

**Hints are gated.** Three levels — a nudge, then a strategy, then the same idea worked through
on *different* data. Levels are 60 s apart because clicking through hints is the best-documented
way to feel productive while learning nothing.

**Reviews come before new material,** capped at 2 new tasks a day, and they arrive interleaved
rather than blocked. Mixing confusable topics is the largest effect in the whole literature
(d ≈ 0.83), and it will feel worse than drilling one thing at a time. That feeling is documented
and wrong.
