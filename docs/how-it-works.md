# How a sitting works, and why it works that way

## The loop

1. **Today** shows due reviews first, most overdue first and at most 12 of them, then up to 2
   new tasks whose prerequisites you have passed. While the backlog is deeper than that review
   cap you are *behind*, and drillion offers nothing new until you are not — starting new
   material while already behind only makes the backlog worse. The whole catalogue is open
   either way; the queue is a suggestion. Not in the mood for one of them? **Bury** it and it
   is gone for the day and back tomorrow, in the same box and on the same due date. The Buried
   band in Today undoes it early.
2. Opening a task starts an **attempt**: a fresh seed and an active-seconds timer that pauses
   when the tab is hidden. The left pane renders the task's `README.md` — Why / You get /
   You return / Rules / Read first — and the right pane is the editor with the stub.
3. **Run** saves your region into the file and runs that file's pytest test with the attempt's
   seed. Failures come back with the assertion lines mapped to editor line numbers.
4. **Hints** are three levels deep. The first is there from the start; the second opens at two
   minutes of active time and the third at three. Half an hour of reading with nothing run and
   no hint taken, and the page offers one unprompted — the gate opens silently, which is no use
   to someone who is not looking at the panel, and you cannot brute-force something nobody has
   told you about. The **solution** opens after 3 attempts and 10 active minutes, and taking it
   means the pass cannot promote the card.
5. **Pass** → computed grade → the card moves on the ladder → your code is archived into
   `progress.json` → the file is reset to the stub, so the next review starts blank.
6. The spec pane carries a **note**, one free-text box per task, saved as you type. It belongs
   to the task and not to the sitting: it survives a grade, a re-attempt and an abandon.

## Why

**Fresh data every sitting.** Nearly every task ships a generator — 167 of the 171 — so when a
task comes back in 8 days the IPs, names and numbers are different. You can't recall the answer
because that exact answer never existed. This is the one feature that stops spaced repetition
from degrading into memorising files.

**A fixed ladder, not a fancy algorithm.** Seven boxes and seven numbers: pass a task and it
returns in 2 days, then 4, 8, 16, 28, 60, 120. The tail past 28 is what keeps review load from
growing without bound — while 28 was the ceiling, every card you had mastered still came back
monthly. FSRS was the obvious choice and was tried and rejected; see
[ADR 0001](adr/0001-leitner-not-fsrs.md) for the four reasons.

**Grades are computed, not self-reported.** First try under par = `quick`, worth +2 boxes. Two
tries, or one slow one, = `pass`, worth +1. Anything slower or past two tries = `struggled`,
worth −1, with box 0 as the floor. Looking at the solution grades `struggled` however green the
tests go — that last rule is the important one, because hint-assisted passes are how people
finish a curriculum and still can't code. A struggle is also counted on the card, and four of
them flag the task as beating you: at that point the task is the problem, not the sitting.

**Par time is the grader's, not yours.** `minutes:` lives in each task's frontmatter because
`grade_of()` needs it to decide `quick`. It stops at the server: it is not in the browser
payload and not on any screen. The timer counts up and never turns a colour at some number you
were supposed to beat. Watching a clock you cannot meet is not information, it is pressure.

**Hints escalate.** A nudge, then a strategy, then the same idea worked through on *different*
data. They are spaced apart in active seconds because clicking through hints is the
best-documented way to feel productive while learning nothing.

**Reviews come before new material,** capped at 2 new tasks a day, and they arrive interleaved
rather than blocked. Mixing confusable topics is the largest effect in the whole literature
(d ≈ 0.83), and it will feel worse than drilling one thing at a time. That feeling is documented
and wrong.
