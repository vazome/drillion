# drillion

A single-user, local web app for getting better at Python by practice: a catalogue of short
tasks, each graded on freshly generated data, each returning on a spaced-repetition ladder.

These are the words the code, the API, the UI and the docs all use. Reach for one of these
before minting a synonym. The rules for *choosing* a tier, difficulty, track or tag when
authoring a task are in [authoring-tasks.md](docs/authoring-tasks.md); this file only says what the
words mean.

## Language

### The catalogue

**Task**:
The unit of practice: one folder under `tasks/`, holding one spec, one stub to fill in, and one
test that grades it. There are 171.
_Avoid_: exercise, drill, problem, kata, question

**Slug**:
A task's folder name, `<NNN>_<name>`, and its identifier everywhere one is needed.
_Avoid_: key, filename

**Topic**:
A task's number — the `NNN` in its slug. An identifier and a default ordering, nothing more.
_Avoid_: reading it as a subject area, which is what **tag** means

**Tier**:
How far into the language a task reaches, and whether stock Python can run it: `core`,
`advanced`, `packages`.
_Avoid_: level, category, section

**Difficulty**:
How hard a task is to get right the first time: `easy`, `medium`, `hard`. Not how long it takes.
_Avoid_: complexity, hardness; and never `easy` as a **grade**

**Track**:
An optional themed run through the catalogue that cuts across tiers, at most one per task.
_Avoid_: course, path, series, curriculum

**Tag**:
A Python concept a task practises — and one that some other task could practise too.
_Avoid_: topic, label, keyword, category

**Prereqs**:
The tasks that must already be passed before this one is offered as a **new pick**.
_Avoid_: dependencies, requirements, blockers

**Source**:
Where a task came from. Provenance, and never a concept you can practise.
_Avoid_: origin, author, credit

**Spec**:
The guidance a task shows you: Why / You get / You return / Rules.
_Avoid_: description, prompt, statement, brief

**Region**:
The part of a task file that is yours to write. Everything below the **machinery marker**
belongs to the grader.
_Avoid_: editable section, solution area, user code

**Machinery marker**:
The line dividing your **region** from the grader's code beneath it.
_Avoid_: separator, fence, boundary comment

**Hint**:
One of three graded nudges per task — a nudge, a strategy, then the same idea worked through on
different data — each opened by spending **active seconds**.
_Avoid_: tip, clue, help

**Solution**:
The reference answer. It opens only after real effort, and taking it means the pass cannot
promote the **card**.
_Avoid_: answer, answer key, model answer

**Par time**:
The minutes a task is expected to take. It is an input to the **grade** and never leaves the
server.
_Avoid_: estimate, time limit, target, budget

### The ladder

**Card**:
Your standing with one task: which **box** it is in, when it is next **due**, how many
times you have passed it and how many **lapses** it has cost you. The task is the material;
the card is your relationship to it.
_Avoid_: entry, record, progress item

**Box**:
One of five rungs on the **ladder**. Counted `0`–`4` in stored state and shown as 1–5.
_Avoid_: level, stage, bucket, bin

**Ladder**:
The five fixed return intervals — 2, 4, 8, 16, 28 days — that a **card** climbs by passing
and steps back down on a **lapse**.
_Avoid_: schedule, algorithm, SRS, curve

**Due**:
The date a **card** returns. A card is due once that date has arrived or passed.
_Avoid_: next review, scheduled date

**Seen**:
How many times a **card** has been passed. Only a pass increments it.
_Avoid_: reading it as views, opens or **runs**

**Lapse**:
A sitting graded `struggled`, counted per **card** and never reset. Reaching the lapse limit
flags the task as one that keeps beating you — a message about the task, not a punishment on
the schedule.
_Avoid_: fail, miss, leech

**Status**:
What a task is to you right now: `new`, `due`, `open`, `done`. Exactly four.
_Avoid_: state, phase; and inventing a fifth

**Bury**:
Putting one **card** out of today's queue by hand — a **review** or a **new pick** alike. It
touches nothing the ladder owns: the box, the **due** date, the **seen** count and the **lapses**
are all exactly as they were, so a bury costs one day of not being asked and can lose nothing.
It ends by itself tomorrow, and it is never a fifth **status** — a buried card is still `due`.
_Avoid_: skip, snooze, hide, postpone; and above all **suspend**, which is a different feature
(indefinite, ended only by hand) that drillion does not have yet

**Review**:
A **due** card, offered back to you. Capped per day: past the cap the rest of the backlog
waits, and today's panel says how many it is holding.
_Avoid_: repeat, redo, revision

**New pick**:
An unseen task whose **prereqs** are cleared, offered as new material. Capped per day, and
held entirely while the backlog is over the **review** cap.
_Avoid_: suggestion, recommendation, next up

**Focus**:
One word that narrows which **new picks** are offered, matched against a task's **tier**,
**track** and **tags** alike. Reviews and the open catalogue ignore it.
_Avoid_: filter, mode, goal, theme

### The attempt

**Attempt**:
One sitting at one task, from the first time you open it until you pass or abandon it. It
carries the timer, the data seed and the hints taken.
_Avoid_: session, try; and never the count of **runs** inside it

**Run**:
One execution of a task's test.
_Avoid_: attempt, submission, execution

**Active seconds**:
Time actually spent on an **attempt**: each touch adds the gap since the last one, capped at
two minutes, so a break is not study.
_Avoid_: elapsed time, duration, time spent

**Grade**:
What a pass was worth, computed and never self-reported: `quick`, `pass`, `struggled`,
`abandoned`.
_Avoid_: score, rating, mark; and never `easy`, which is a **difficulty**

**Gate**:
The rule that a **hint** or the **solution** must be earned — in **runs** and **active
seconds** — before it opens.
_Avoid_: lock, timer, paywall

**Archive**:
Every version of your code that got anywhere, kept per task, passed or abandoned alike.
_Avoid_: history, backup, snapshots

**Note**:
What you wrote down about a **task**, in your own words. One per task, edited in place — no
history, no versions, and never one per **attempt**. It belongs to the task and not to the
sitting, so a **grade**, a new attempt and an abandon all leave it alone; clearing it deletes it.
The one thing on the task page drillion did not generate.
_Avoid_: comment, annotation, journal, memo; and above all "notes" plural on a single task

**Log**:
The record of passes — one row each, with its date, **grade**, **runs** and time.
_Avoid_: journal, feed, timeline

**Recent**:
Tasks worked within the **window**, newest first: the way back into what you were last doing.
An open **attempt** counts, and counts first.
_Avoid_: history, activity feed, continue

**Practised**:
Distinct days worked within the **window**. A rolling count, never a streak — one missed day
costs one point.
_Avoid_: streak, consistency, days in a row

**Window**:
The trailing span, in days, that **recent** and **practised** are measured over.
_Avoid_: period, range, lookback
