# Changelog

Hand-written, newest first. drillion follows [semantic versioning](CONTRIBUTING.md#versioning)
against its public surface: the CLI, the HTTP API, the `progress.json` schema, and the
task-folder format. The version is declared once, in `pyproject.toml`.

## 0.8.1 — 2026-09-11

Documentation and packaging only. The 0.8.0 wheel is unchanged in what it does.

- The install instructions settle on `uv tool install drillion`, so the command is
  `drillion` from then on and an update is `uv tool upgrade drillion`. The `uvx` route
  refetched on every start and left nothing on the machine to upgrade.
- The README says what an upgrade actually does to a root: drillion's half of each task
  follows the release, the code you wrote is spliced into it, a task drillion no longer ships
  moves to `tasks/_retired/<slug>/`, and a task you wrote yourself is left alone. It had
  promised since #219 that an upgrade never writes into a root that already has tasks, which
  stopped being true when the splice landed. `docs/configuration.md` had it right all along.
- The provenance examples verify 0.8.0 rather than 0.5.1, so both commands work as written.
- The client has a favicon, and the README opens with the project banner.
- `tasks/.shipped` is ignored. `seed()` writes it per environment to record which task files
  are drillion's, so it belongs to a machine the way `progress.sqlite3` does.

## 0.8.0 — 2026-09-11

0.7.5, 0.7.6 and 0.7.7 were tagged but never published: the release run failed on an
attestation upload that GitHub could not persist, so the last release anyone can install is
0.7.0. Everything those three tags carried ships here.

- **Python 3.14 is the minimum.** It is drillion's packaging floor, its default interpreter,
  and the only version CI tests. An environment on 3.13 must move up before upgrading.
- **The catalogue is 267 tasks, up from 189.** Twelve give a second, contrasting practice
  context to every tag that had only one, so no concept is taught by a single exercise.
  Sixty-six more cover the three areas the catalogue had left alone: the object model past
  `@property` (descriptors, `__slots__`, metaclasses, the MRO), about thirty stdlib modules
  it never touched (`sqlite3`, `pickle`, `graphlib`, `codecs`, `array`, `queue`, `operator`
  and the rest), and the classical algorithms, from dynamic programming to string search.
  Every prerequisite still points backward and `drillion doctor` still enforces it.
- **A failed run shows the case that failed.** The arguments, what your code returned and
  what was expected, side by side, instead of a wall of pytest output you have to read
  backward. Long values wrap inside their box with their own lines numbered, so a line too
  wide for the panel cannot be mistaken for two.
- **Settings is a dialog rather than a page**, opened over whatever you are working on, with
  Editor and Data grouped across the top. `#/settings` still works as a link. The editor
  reads a per-browser preference for font, size, ligatures, tab size, word wrap and relative
  line numbers, applied to the editor already on screen, and the practice timer can be
  hidden. Key bindings are a three-position control: standard, Vim, or Emacs, the last of
  these new here and sharing the status line under the editor.
- **New picks never pause.** A deep backlog used to stop new tasks from arriving until you
  had caught up, which stopped the learning to protect the schedule. Reviews are still
  capped per day; the daily new picks now stand whatever the queue looks like. The
  catalogue's Recent activity band is a way back in rather than a history, so it shows four
  rows.
- **An upgrade replaces the grader and keeps what is yours.** Installing a new version used
  to leave the original grading machinery on every task you had opened, and to delete any
  task you had written yourself. Your code is now spliced into the new machinery through the
  same gate the editor writes through, a task drillion no longer ships moves to
  `tasks/_retired/<slug>/` instead of vanishing, and a task you added is left alone.
- **A restore lands completely or not at all.** Every region in a bundle is validated before
  anything is written, and a write that fails puts the earlier ones back. A restore that
  reports success succeeded.
- **Which Python graded a task is now on the record.** The interpreter appears in
  `/api/health`, beside the version in the header, and under `drillion doctor`'s sandbox
  line. An archived pass keeps the seed its cases came from, the interpreter that produced
  the verdict, and a hash of the machinery it was graded against, which matters once an
  upgrade can splice a new grader around unchanged code.
- **Tasks using time zones now pass on Windows**, which ships no time-zone database of its
  own; `tzdata` is a dependency there.
- The web design system moved to CSS Modules, keeping component styles local with no change
  to the pixels or the behavior.
- Playwright now walks the loop with no pointer at all, audits the catalogue, a task,
  progress and the Settings dialog against WCAG A and AA, checks reflow at 200% zoom, and
  runs the suite in Firefox and WebKit as well as Chromium.

## 0.7.0 — 2026-09-08

- Seven new tasks bring the catalogue to 189 and close the last of the single-exposure
  concepts: every concept the curriculum teaches is now practised in at least two different
  contexts. `heapq`, `functools.cache`, `pathlib`, enums, `match`, dataclasses and the walrus
  operator each get a second task that is not a restatement of the first.
- A prerequisite that pointed at the first half of a split exercise now points at the last
  half. Thirteen tasks were the second half of a split and gated nothing at all, so a learner
  could reach the task that depends on them having done only half the material. 58 tasks
  changed one number each; `drillion doctor` still enforces that every edge points backward.
- Whatever your own `print()` wrote comes back in the results panel whether the tests passed
  or failed. It used to appear only on a failure, which read as the print never having run.
  On Windows it did not appear at all: the restricted-token sandbox handed its output back
  with the line endings the child wrote, and every other tier had them translated.
- Settings can turn on Vim keys in the editor, off by default, with the current mode shown
  under the editor. Run and Submit keep their shortcuts in either mode. The setting lives in
  the browser rather than in your progress, so a backup does not carry it.
- Settings has a danger zone that erases all progress and puts every task back to its stub.
  It is confirmed by typing `erase progress` rather than by clicking, the server checks the
  same phrase, and it writes `backup-before-reset.zip` in your root first, which is the only
  way back. It deletes the stored progress rather than emptying it, so nothing survives to be
  imported on the next read.
- Burying a task is gone, along with `POST /api/task/{slug}/bury` and the `buried` field on
  every payload. It bought a queue you could rearrange rather than one you could work, and it
  cost a control on every row and a band under the Today panel. Progress written by an older
  build still loads; the stored field is ignored.
- The task toolbar no longer re-wraps and pushes the editor down when the unsaved marker
  appears mid-keystroke, and two prerequisites arriving at one task no longer share a single
  arrowhead in the lineage graph.
- CI counts the shipped tasks from the checkout instead of a written-down number, so adding a
  task no longer fails the packaging jobs on a figure the author had no reason to know about.

## 0.6.0 — 2026-09-06

- Running a task and submitting it are now separate actions. Run executes the tests without
  spending an attempt or moving the card; Submit is the deliberate grading action. Task headers
  and catalogue rows also expose the full prerequisite lineage, so a learner can see what a task
  builds on and open every dependency directly. The built client now revalidates its entry page,
  so returning after an upgrade no longer leaves an old interface in the browser cache.
- The catalogue is now a curriculum rather than a collection with incidental numbers. The 182
  tasks put the fundamentals first, every declared prerequisite points backward, and `drillion
  doctor` enforces that invariant. Twelve new coding tasks teach `while`, `match`, inheritance,
  `heapq.merge`, variadic and keyword-only arguments, lazy `map`/`filter`, class and static
  methods, `bisect`, exact prefix and suffix removal, assignment expressions, `yield from`, and
  `frozenset`. The interview take-home quiz and its private-project framing are gone, as is the
  imported tutorial prose that duplicated each task's own specification and bypassed gated hints.
  This reordering changes task slugs, so progress recorded against an old slug can become orphaned.
- A saved progress file is now stamped with the schema of the build that last wrote it, rather
  than keeping the stamp from the build that first created it. Compatibility tests use frozen
  copies of every shipped schema, so a future format change cannot silently leave a new file
  claiming to be old.
- Installation and safety documentation now starts from the reader's operating system, explains
  that uv can obtain Python, and states exactly what running learner code may access on Linux,
  macOS, and Windows. Artifact verification covers GitHub Releases, PyPI, and ghcr.
- CI builds and scans the image once, skips the expensive matrix for prose-only changes, and
  overlaps image scanning with smoke tests without dropping checks. The Python, web, image, and
  workflow dependencies are current for this release.

## 0.5.1 — 2026-08-28

- A release can now be checked without trusting the index it came from. The wheel and the sdist
  are attested where they are built and the provenance travels with them as a release asset, so
  `gh attestation verify drillion-0.5.1-py3-none-any.whl --repo vazome/drillion` answers from a
  plain download. ghcr has carried the image's provenance and SBOM since 0.4.6 and PyPI keeps its
  own; what was missing was anything on the releases page itself, which is where somebody who does
  not use either registry actually gets the file.
- The editor is on the current Monaco. It sat eleven majors behind, on 25.x, because the packages
  it needs only work as one set and a partial upgrade produced two incompatible copies of the same
  types — so every offered bump failed and the whole family stayed frozen. It is on 36 now, which
  matters because completions, signatures and the type errors underlined as you write all come
  from a language server wired to that API: staying behind meant drifting away from anything
  upstream documents or fixes. Nothing changes in how the editor behaves.
- The image builds on node 25, and on whatever node comes after it. The web stage assumed
  `corepack` was in the base image; node stopped shipping it, so the build died on `corepack: not
  found` and every node bump was blocked. pnpm is still pinned in exactly one place, and still
  resolves to that version.

## 0.5.0 — 2026-08-28

- `progress.json` now says which format it is. Every file drillion writes carries a `version`,
  and a build refuses to open a file written by a newer drillion rather than rewriting it: it
  says so, tells you to upgrade, and leaves the file exactly as it found it. Nothing changes for
  a file written before this release — no version means version 1, and it loads as it always
  did. The reason to add it now is that the option expires. drillion ships on PyPI, on ghcr and
  as a clone, those three do not move in step, and `pip install drillion==0.5` beside a file a
  0.6 wrote is an ordinary Tuesday. `CONTRIBUTING.md` has promised a schema contract since 0.4;
  this is the number behind it.
- Task 033 can be passed on Windows. It shelled out to `echo`, `true` and `false`, which are
  `cmd` builtins rather than programs, so your solution *and* the grader's own reference both
  raised `FileNotFoundError` — the task was unpassable on any Windows account that did not
  happen to have Git's unix tools on `PATH`. CI had them, which is why CI never saw it. It now
  runs a Python child on every platform and still grades exit code, captured stdout, captured
  stderr and `check=False`.
- An asset request can no longer leave the task's own `assets/` folder. The guard was a list of
  forbidden characters, and a symlink contains none of them — so a symlink inside `assets/` was
  followed and served, including one pointing at the task's `task.py` with its reference
  solution in it. The route now checks that the resolved path is still inside the folder, which
  does not depend on guessing what to forbid. A Windows drive-relative name such as
  `C:progress.json` was the other way past the old list and closes with the same change.
- The published image has no known fixable vulnerability left in it. OpenSSL is current, the
  base images are pinned by digest so the image you pull is the image that was scanned, and the
  interpreter's own `pip` is gone — drillion runs from a `uv`-built virtualenv and never invoked
  it, but the packages it vendored were still counted against the image.
- Internals, for anyone building on this: the release workflow no longer leaves a credential on
  disk or trusts a cache a pull request could have written, the test suite and all 171 graded
  tasks now run nightly against freshly resolved dependencies instead of only when someone
  pushes, and the workflow audit fails the build rather than filing a report nobody reads.

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
