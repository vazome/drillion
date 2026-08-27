# Changelog

Hand-written, newest first. drillion follows [semantic versioning](CONTRIBUTING.md#versioning)
against its public surface: the CLI, the HTTP API, the `progress.json` schema, and the
task-folder format. The version is declared once, in `pyproject.toml`.

## Unreleased

- The run button's keyboard hint reads `Ctrl/⌘+Enter`, since the binding fires on either.

## 0.2.0 — 2026-08-27

- Tests run in a throwaway scratch directory rather than in the folder that holds
  `progress.json`, so a file a solution writes to a relative path is swept away with the
  scratch directory instead of littering the data root.
- The client ships its own fonts. Nothing is fetched from Google any more, so the page
  renders in IBM Plex Sans and Spline Sans Mono offline and behind a firewall, and opening
  it tells no one.
- A first run says what the ladder is: one dismissible note above Today, shown only while
  nothing has been passed and nothing is open, with a link to `docs/how-it-works.md`.
- Today names the tag that keeps beating you once two of its tasks are flagged, and the chip
  sets the focus to it.
- `/` anywhere goes to the catalogue and focuses the search box; `Enter` there opens the first
  row of the filtered list.
- The catalogue's list scrolls sideways below about 840px instead of squeezing its columns.
- A pass now shows your code and the reference side by side, changed lines marked, instead of
  the reference alone as a code block. Read-only both sides, themed in light and dark.
- The task page stacks its two panes below 1000px — spec first, then the editor, both full
  width — so a tablet can read a spec and run it. Editing code there is still not the point.
- The task page header carries the same quiet marks the catalogue rows do: `buried today`, and
  `struggled N×` once a task has beaten you enough times.
- The progress page looks both ways: a 14-day due-load forecast with the daily cap drawn on
  it, a year of practice as a heatmap, and one strip per topic showing where its tasks sit on
  the ladder — sortable, stuck first, each tag a link into the catalogue (`#/?tag=…`).
  `GET /api/progress` gains `today`, `forecast`, `cap` and `days`; `per_tag` rows gain
  `boxes`, `lapses` and `due7`.
- The half-hour nudge is a card in the corner rather than a banner over the editor: take a
  hint, or bury the task and go read up.
- `POST …/hint` and `POST …/solution` answer with the whole task, the same shape as `GET /api/task`.
- Catalogue rows carry `blocked` (the prereq slugs not yet passed) instead of `prereqs`, and
  `today.no_new` names the one reason there are no new picks; the page no longer re-derives either.
- `ladder` rides the catalogue, progress and task payloads; `region_start` is gone.
- A pass returns `next`, the scheduler's suggestion, so the page stops refetching the catalogue.
- The source distribution, the wheel and the image are unchanged in what they carry.

## 0.1.1 — 2026-08-26

- The source distribution no longer carries `web/node_modules`. 0.1.0's sdist was 39 MB, of
  which 113 MB uncompressed was somebody else's JavaScript, redistributed with none of its
  licences. hatchling reads only the root `.gitignore`, so the `node_modules/` line in
  `web/.gitignore` never reached it, and the build is clean until something runs
  `pnpm install` first — which is what CI does and a local build does not. The wheel was
  never affected. `pyproject.toml` now names those paths itself, and CI builds an sdist
  with `node_modules` on disk and fails if any of them come back.

## 0.1.0 — 2026-08-26

The first numbered drillion. Everything below is the starting surface, not a change from
anything earlier.

- 171 tasks under `tasks/`, graded by splicing the learner's region into the task file and
  running its own `test_solve` in a pytest subprocess.
- A Leitner-style scheduler over `progress.json`: boxes, a daily review queue with a backlog
  cap, and hint/solution gates that open on attempts and time spent.
- `drillion` serves the React page and the JSON API on 127.0.0.1:8765; `drillion selfcheck`
  solves every task with its own reference; `drillion doctor` says why a task folder would be
  skipped.
- `drillion --version` and `GET /api/health` report the installed version, and the page shows
  it in the header.
- Bury a task to push it out of today's queue; it comes back tomorrow on its own.
- A free-text note per task, kept in `progress.json` alongside the card.
- A container image that runs the same app against a mounted content root, and carries the
  tasks itself when nothing is mounted over them.
- The wheel ships the 171 tasks and the built page. An install with no checkout copies them
  once into a per-user directory (`XDG_DATA_HOME` and its platform equivalents) and practises
  there; a root that already has `tasks/` is used as it is and never written over.

### Releasing

Bump `version` in `pyproject.toml`, add a dated heading above, then tag the release commit.
CI refuses a tag whose name disagrees with the declared version.

```bash
git tag -a v0.2.0 -m "drillion 0.2.0" && git push origin v0.2.0
```
