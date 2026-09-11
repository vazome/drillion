# How a sitting works, and why it works that way

## The loop

1. **Today** shows due reviews first, most overdue first and at most 12 of them, then up to 2
   new tasks whose prerequisites you have passed. The review cap is there so a backlog cannot
   bury you, and it never costs you the new picks: a deep queue is a reason to review, not a
   reason to stop learning something new. The whole catalogue is open either way; the queue is
   a suggestion, so not being in the mood for one of them costs nothing — open another, or
   open none.
2. Opening a task starts an **attempt**: a fresh seed and an active-seconds timer that pauses
   when the tab is hidden. The first minute of it is free — the clock sits at 00:00 while you
   read, and a corner notice says so ten seconds in. The left pane renders the task's `README.md` — Why / You get /
   You return / Rules / Read first — and the right pane is the editor with the stub.
3. **Run** saves your region into the file and runs that file's pytest test with the attempt's
   seed. Failures come back with the assertion lines mapped to editor line numbers, and
   whatever your own `print()` wrote is shown above them whether the tests passed or failed.
   A Run grades nothing — it is free and repeatable, however green it comes back. **Submit** is the
   same execution plus the claim that you are done: it costs an attempt, and on green it is
   what grades the pass and sets when the task comes back.
4. **Hints** are three levels deep. The first is there from the start; the second opens at two
   minutes of active time and the third at three. Half an hour of reading with nothing run and
   no hint taken, and the page offers one unprompted — the gate opens silently, which is no use
   to someone who is not looking at the panel, and you cannot brute-force something nobody has
   told you about. The **solution** opens after 3 submitted attempts and 10 active minutes,
   and taking it means the pass cannot push the task further out.
5. **Pass** → computed grade → the task's next sighting moves in or out → your code is archived
   into `progress.sqlite3` → the file is reset to the stub, so the next review starts blank. The
   archive keeps what produced that grade beside the code: the seed the cases came from, the
   Python that ran them, and which grader was on disk at the time. The header names that same
   Python, and so does `drillion doctor`.
6. The spec pane carries a **note**, one free-text box per task, saved as you type. It belongs
   to the task and not to the sitting: it survives a grade, a re-attempt and an abandon.

## Why

**Fresh data every sitting.** Nearly every task ships a generator — 255 of the 267 — so when a
task comes back in 8 days the IPs, names and numbers are different. You can't recall the answer
because that exact answer never existed. This is the one feature that stops spaced repetition
from degrading into memorising files.

**A fixed schedule, not a fancy algorithm.** Seven numbers: pass a task and it returns in 2
days, then 4, 8, 16, 28, 60, 120. The screens never show you those seven — they say *learning*
(back within a few days), *familiar* (a week to a month) or *solid* (two months or more), because
a seven-rung climb is a thing to be intimidated by and "how well do I know this" is the only
question the number answers. The tail past 28 is what keeps review load from growing without
bound — while 28 was the ceiling, everything you had mastered still came back monthly. FSRS was the obvious choice and was tried and rejected; see
[ADR 0001](adr/0001-leitner-not-fsrs.md) for the four reasons.

**Grades are computed, not self-reported.** First try under par = `quick`, worth two steps
further out. Two tries, or one slow one, = `pass`, worth one. Anything slower or past two tries =
`struggled`, worth one step back in, with the shortest interval as the floor. Looking at the solution grades `struggled` however green the
tests go — that last rule is the important one, because hint-assisted passes are how people
finish a curriculum and still can't code. A struggle is also counted against the task, and four of
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

## Why these numbers

The constants live in `src/drillion/scheduler.py`; the reasoning lives here, because the next
issue that says "make it 20" needs it.

- **`LADDER = [2, 4, 8, 16, 28, 60, 120]`.** Fixed intervals over a season of practice, sized
  near the 10–20 % of the retention interval that Cepeda 2008 found best, rather than fitted per
  card — a seven-element list beats a dependency with 21 trained weights and no data to fit
  them. The tail past 28 is what keeps review load from growing without bound: while 28 was the
  ceiling, every card you had mastered still came back monthly, and a finished catalogue settled
  at ~6 reviews a day before a single new pick. 60 and 120 shed that load without a fifth status
  for "retired" — the card is simply `done`, and a done card you keep getting right comes back
  rarely.
- **`GRACE_SECS = 60`.** Reading is not the work. Without it the clock is running while you
  are still finding out what the task wants, which prices reading into the grade and teaches
  the one habit the spec pane exists to prevent — skimming and typing. A minute is enough for
  a spec of this size and small enough that it cannot be farmed: it is granted once per open,
  not once per sitting, and the same grace applies to the hint and solution gates, so nothing
  in the attempt disagrees about what time it is.
- **`REVIEWS_PER_DAY = 12`.** Unbounded, the day you come back from three weeks away is 100 rows
  deep and the ladder never recovers. Anki ships 200 reviews against 20 new, a 10:1 ratio; a
  drillion review is a whole coding task rather than a flashcard, so 12 against 2 is roughly the
  same hour. A constant: Settings holds your data and your editor keys, not the scheduler's.
- **`LAPSE_LIMIT = 4`.** Anki suspends a flashcard at 8 lapses; a drillion lapse costs a sitting
  rather than seconds, so the same wasted time arrives around 4. It is a flag only: nothing is
  suspended, hidden or rescheduled by it.
- **`GRADES = {"struggled": -1, "pass": +1, "quick": +2}`.** Without a negative step the ladder
  is not adaptive at all: a task that fights you every sitting would hold the top box and its
  120-day gap forever, on the same schedule as one you have aced. −1 rather than back to box 0
  because `struggled` is the grade for anything slow, anything over two runs and anything
  peeked — it is common — and a repeated struggle still walks the card all the way down.

## What Settings can do to all of it

Settings is a dialog over whatever you are looking at, so changing something does not cost
you the task you had open. **The editor card** holds the font, its size, ligatures, the key
binding — standard, Vim or Emacs — tab size, word wrap and relative line numbers, plus whether the practice timer is on
screen — hiding it changes nothing about the time, which is still counted and still decides
the grade. Those are preferences of the browser, not of your practice, so they are not in a
backup.

**Back up** writes your cards, notes, log, archive and the code in every task to one file, and
**Restore** reads one back after telling you what it brings and what it replaces. Both keep a
copy of what they overwrote.

**Erase all progress**, under the danger zone, is the one action that destroys something. It
deletes the stored progress instead of emptying it and puts every task back to its stub, so
the next run is a first run. It asks you to type `erase progress`, and it writes
`backup-before-reset.zip` in your root before it starts, which is the only way back.
