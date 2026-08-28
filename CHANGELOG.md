# Changelog

Hand-written, newest first. drillion follows [semantic versioning](CONTRIBUTING.md#versioning)
against its public surface: the CLI, the HTTP API, the `progress.json` schema, and the
task-folder format. The version is declared once, in `pyproject.toml`.

## 0.4.6 — 2026-08-28

- Code you submit no longer runs with your account's reach. A graded task used to be able to
  read `~/.aws/credentials`, write anywhere you can, see every environment variable your shell
  exported and open a socket — and still be graded as a pass. It is now confined by the kernel
  where the kernel can do it: Landlock on Linux, an `sandbox-exec` profile on macOS, a restricted
  token at Low integrity in a job object on Windows. On Linux and macOS reads are limited to the
  interpreter, the system libraries, `tasks/` and a scratch directory, writes to that scratch
  directory alone, and TCP is refused. Windows confines the writes and caps memory but not the
  reads or the network — integrity levels are write-only protection, and the one tier that would
  block reads needs every path the interpreter reads ACLed at install and re-checked every run.
  `SECURITY.md` says which half is the kernel's. Underneath, on every platform, `HOME` and
  `TMPDIR` point at the scratch directory, the environment is an allowlist, and resource limits
  cap file size, memory and CPU. `drillion doctor` names the tier you actually got, read back
  from a process that tried it rather than assumed.
- Spawning a subprocess stays legal, because task 033 grades `subprocess.run`. What it cannot do
  is escape: a Landlock domain is inherited, so anything a task starts is bound by the same
  rules. Where no kernel tier exists — an older Linux, a container that blocks `prctl` — an audit
  hook stands in, and on Windows it rides along with the token for the network the token does not
  cover. That is a speed bump, not a boundary, and `SECURITY.md` says so.
- drillion works on Windows. It did not before: every `task.py` contains a `═`, task files were
  read with the locale encoding, and on a cp1252 console that raised — which the catalogue
  reported as "is not valid UTF-8", leaving an empty catalogue and all 171 tasks falsely
  accused. Text is now read and written as UTF-8 everywhere, failures name the task the same way
  on every platform, and CI runs on Windows and macOS as well as Linux, plus Python 3.14.
- The server refuses a request from a page it did not serve, so a website you happen to have open
  cannot drive your local drillion.
- Every task that takes arguments now says what it takes. The 18 left bare at 0.4.0 are done,
  apart from one rate-limiter callback that has no honest type to give it.
- Supply chain: the 18 Dependabot alerts are cleared, Trivy scans the source, the workflows and
  the published image on every push and weekly, the image no longer ships an npm it never runs
  or a uv cache, and it is built for arm64 as well as amd64 with an SBOM attached. Releases are
  cut from this file automatically on tag, and can only publish from `main`.
- There is no 0.4.5. It was tagged from a commit that was never on `main`, the release gate
  refused to publish it, and version tags here are immutable — so this is 0.4.6.

## 0.4.0 — 2026-08-27

- The editor knows what your code means. Typing `rows.` offers the methods that value actually
  has, with the signature and the docstring beside them, and a real type error is underlined
  while you write rather than after you run. A language server runs next to the grader, on your
  machine, over a new `/lsp` websocket — nothing is sent anywhere.
- Every task's `solve()` now says what it takes — `def solve(rows: list[tuple[str, float]])` —
  which is what those completions read: with no type on the parameter there is nothing to infer
  from, and no editor can help. 96 of the 114 tasks that take arguments are fully annotated. The
  remaining 18 keep a bare callback or AWS client, because annotating those means putting an
  import into the code you open.
- The editor is Monaco rather than CodeMirror 6. `Ctrl/⌘+Enter` still runs the tests, `/` still
  goes to the catalogue unless you are typing in the editor, and the colours still come from the
  same design tokens as the fenced code in the spec pane.
- Two costs, since they are yours to pay: the page is 3.7 MB gzipped instead of 275 KB, and an
  install now pulls basedpyright, which is 280 MB with its bundled Node runtime. Both are spent
  on your own machine, and the page is served from it.

## 0.3.0 — 2026-08-27

- A tag link from the progress page now filters the catalogue even when the catalogue is
  already open, instead of only on the way in from another page.
- Focus rings appear for keyboard focus only; a mouse click no longer draws one on inputs, toggles and table rows.
- A hint or solution notice on the task page no longer disappears while you are reading it.
- The "not saved — syntax" marker no longer follows you to the next task.
- The HTTP API no longer sends fields nothing reads: `marker_line` on a task, `hints` on an
  attempt, `col` and `exhausted` on errors, and `status`/`root` on `/api/health`. An archived
  answer the server keeps closed is now `"code": null` instead of a missing key, and an error
  without a line reports `"line": null` (breaking: the next release is a minor bump under 0.x).
- The run button's keyboard hint reads `Ctrl/⌘+Enter`, since the binding fires on either.
- Burying the last unstarted task no longer reads as "that is today's new material, 0 done".
  Today names the bury as the reason there is nothing new, so unburying is the obvious way out.
- A card you have never touched no longer lands in `progress.json` just because a page read it.

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
