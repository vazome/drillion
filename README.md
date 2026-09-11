# drillion

[![PyPI](https://img.shields.io/pypi/v/drillion)](https://pypi.org/project/drillion/)
[![Python](https://img.shields.io/pypi/pyversions/drillion)](https://pypi.org/project/drillion/)
[![CI](https://github.com/vazome/drillion/actions/workflows/ci.yml/badge.svg)](https://github.com/vazome/drillion/actions/workflows/ci.yml)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/14269/badge)](https://www.bestpractices.dev/projects/14269)
[![License](https://img.shields.io/pypi/l/drillion)](https://github.com/vazome/drillion/blob/main/LICENSE)

TL;DR: self-hosted Python practice with a UI that stays out of your way. No streaks,
no leaderboard nonsense, no badges and no engagement bait. Made by a neurodivergent
engineer. It is simple, and it runs your code in a sandbox.

Longer: drillion is a local web app with 267 short Python tasks, each tagged with the
concept it drills so you can go straight at whatever you're worst at. No login, no
account, no server except the one on your laptop. Tasks are folders of Markdown and
Python. Your progress is a single SQLite file you can copy, back up and carry.

| | Light | Dark |
| --- | --- | --- |
| **The editor**<br><sub>the editor completing a list method</sub> | [![The editor, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/completions-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/completions-light.png) | [![The editor, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/completions-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/completions-dark.png) |
| **A task**<br><sub>spec on the left, your code and the test output on the right</sub> | [![A task, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-screen-1-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-screen-1-light.png) | [![A task, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-screen-1-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-screen-1-dark.png) |
| **A failed run**<br><sub>the case that failed, your output beside what was expected</sub> | [![A failed run, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-failed-1-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-failed-1-light.png) | [![A failed run, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-failed-1-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-failed-1-dark.png) |
| **A pass**<br><sub>your answer against the reference, and when it comes back</sub> | [![A pass, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-passed-1-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-passed-1-light.png) | [![A pass, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-passed-1-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-passed-1-dark.png) |
| **The catalogue**<br><sub>today's picks, the tags, the whole table</sub> | [![The catalogue, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/catalogue-screen-1-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/catalogue-screen-1-light.png) | [![The catalogue, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/catalogue-screen-1-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/catalogue-screen-1-dark.png) |
| **Lineage**<br><sub>what gates a task, and what it gates in turn</sub> | [![Lineage, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/lineage-1-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/lineage-1-light.png) | [![Lineage, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/lineage-1-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/lineage-1-dark.png) |
| **Progress**<br><sub>the ladder, what is due, where each topic sits</sub> | [![Progress, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/progress-1-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/progress-1-light.png) | [![Progress, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/progress-1-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/progress-1-dark.png) |
| **Settings**<br><sub>the editor set up the way you have it everywhere else</sub> | [![Settings, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/settings-1-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/settings-1-light.png) | [![Settings, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/settings-1-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/settings-1-dark.png) |

Every `solve()` says what it takes, so the editor knows what your value can do. Completions,
signatures and type errors come from a language server running next to the grader, on your
machine, and nothing is sent anywhere.

## But why?

I have tried some learning platforms. Some stuck better than others, and there were
plenty of things I did not like about all of them, the gamification and the ratings
above all. I simply do not care about them. I came for one thing: to keep my Python
sharp and learn new things, not to chat about it with peers.

I took heavy inspiration from Exercism, HackerRank and, surprisingly, Anki, and built it
from scratch.

Core ideas I'm keeping in mind during the development:

- **A clean UI that does not gate the task.** Nothing stands between opening drillion and
  writing code.
- **Categorisation.** Every task is tagged with the concept it drills, and a tag spans
  many tasks, so you can go straight at the thing you are worst at instead of grinding a
  track in order.
- **Anki-like progression.** A task comes back before you forget it, with a daily cap so a
  backlog cannot bury you.
- **An editor that behaves like an IDE without the complexity of one.** Every `solve()` is
  typed, so completions, signatures and inline type errors are real as they come from a
  language server running next to the grader, on your machine.
- **Hints unlock and they are not free.** Three per task, escalating from a nudge to the
  same idea worked through on different data. After half an hour with no submission,
  drillion suggests taking one as you cannot brute-force something you are unaware of.
- **Grading is the real.** Your code is spliced into the task's own pytest file and run.
- **YOUR progress.** One SQLite file on your disk, stamped with a schema version, and a
  build refuses to rewrite a file a newer one wrote rather than quietly mangling it. Settings
  turns it into a backup you can carry, and can erase the lot if you want to start over.
- **It is free, and it stays free.** No tier, no voucher, no account, no telemetry,
  open-source.

One consequence worth stating plainly: 267 tasks ship as executable Python, and `task.py`
runs on import. Shipping tasks as code is what makes the sandbox necessary, so graded code
is confined by the kernel and you do not have to take my word for it. **What running it
does to your machine**, below, is the detail.

## Install

You do not need Python, and you do not need to know what a virtual environment is. Pick your
system below, run two commands, and drillion opens in your browser at
<http://127.0.0.1:8765>. It runs on your machine, so nothing is uploaded and there is no
account.

### Linux, macOS, or Windows with WSL

Open a terminal. Install [uv](https://docs.astral.sh/uv/), which is the one tool drillion needs:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Close the terminal and open a new one**, so it picks up the new command. Then:

```bash
uvx drillion
```

The first run takes a minute while it fetches Python and drillion. After that it starts in
seconds.

### Windows

Open **PowerShell** from the Start menu. Install uv:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Close PowerShell and open it again**, then:

```powershell
uvx drillion
```

One difference worth knowing: the code you submit is sandboxed less tightly on Windows than on
Linux and macOS. Windows blocks what it can write, but not what it can read.
[SECURITY.md](SECURITY.md) says exactly which half is which.

### Using it day to day

- **Stop it**: press `Ctrl+C` in the terminal window.
- **Start it again**: `uvx drillion`, in any terminal.
- **Update**: nothing to do. `uvx` fetches the current version each time.
- **Your work is kept** between runs. An update replaces drillion's half of each task and
  leaves the code you wrote where it is.

Want a permanent `drillion` command instead of typing `uvx` every time? Either of these
installs one:

```bash
uv tool install drillion    # uv tool upgrade drillion to update
pip install drillion        # the same, if you already have Python 3.14+ and no uv
```

### Docker

Same on every system, if you already run Docker:

```bash
docker run -p 127.0.0.1:8765:8765 -v drillion:/data ghcr.io/vazome/drillion
```

Open <http://127.0.0.1:8765> yourself, since the container never opens a browser. The image carries
the tasks and the page; the named volume keeps your work across upgrades.
[compose.yaml](compose.yaml) is the same thing plus `restart: unless-stopped`, so drillion comes
back after a reboot; save that one file anywhere and `docker compose up -d`.

## Commands

```bash
drillion              # serve the web UI (default)
drillion selfcheck    # solve every task with its own reference, proving the set still works
drillion doctor       # say why a task folder would be skipped
```

## Your progress

Everything drillion owns lives under one root: `tasks/`, which is where your code is saved, and
`progress.sqlite3`, which holds your cards, notes and archived solutions. From a clone that root is
the checkout. Installed, it is a per-user data directory that the first run seeds from the tasks
inside the wheel. In Docker it is the volume at `/data`. An upgrade brings that root back in line
with the version you are running: drillion's half of each task follows the new release, and the
code you wrote is spliced into it, so a grader fix reaches you without touching what you typed. A
task drillion no longer ships moves to `tasks/_retired/<slug>/` instead of being deleted, and a
task you wrote yourself is left alone.
See [docs/configuration.md](docs/configuration.md) for the environment variables and the Docker
bind-mount recipe.

A `progress.json` written by an older drillion is imported on first access, with its own bytes
left as they are. SQLite is the source of truth from then on, so that JSON is a snapshot of the
moment before the upgrade rather than a second copy that keeps up. The danger zone below deletes
it along with the database, since a reset that left it there would import it straight back.

**Settings → Back up** writes everything you would miss to one file: your cards, notes, log and
archive, plus the code you have written in every task. Restore it on another machine or after a
reinstall and you pick up where you left off. A restore replaces what is there now, and saves
what it replaced to `backup-before-restore.zip` in the same root first.

**Settings → Danger zone** is the way back to a first run: it deletes the stored progress and
puts every task back to its stub. You confirm it by typing `erase progress`, and it writes
`backup-before-reset.zip` in the same root before it does anything, which is the only way to
undo it.

**Settings → Editor** sets the editor up the way you have it everywhere else: font and size,
ligatures, Vim or Emacs keys, tab size, word wrap, relative line numbers, and whether the practice
timer is on screen. Those live in the browser rather than in your progress, so a backup does
not carry them.

## What running it does to your machine

drillion runs Python on your computer: the code you write, and the code that ships inside the
267 tasks. So it is worth saying plainly what that costs you.

- **Your submissions are confined by the kernel.** Landlock on Linux, an
  `sandbox-exec` profile on macOS, a restricted token at low integrity on Windows. On Linux and
  macOS graded code reads only the interpreter, the system libraries and the tasks, writes only
  to a scratch directory deleted after the run, and cannot open a network connection. Windows
  confines the writes but not the reads or the network. `drillion doctor` prints the tier you
  actually got, read back from a process that tried it.
- **Nothing leaves your machine.** No account, no telemetry, no fonts or scripts fetched from
  anyone. The server binds `127.0.0.1`, and refuses a request from a page it did not serve, so
  a website you happen to have open cannot drive your local drillion.
- **What you downloaded can be checked.** Every release carries provenance naming the workflow
  run that built it, attached to the release itself:

  ```bash
  gh attestation verify drillion-0.5.1-py3-none-any.whl --repo vazome/drillion
  gh attestation verify oci://ghcr.io/vazome/drillion:0.5.1 --repo vazome/drillion
  ```

[SECURITY.md](SECURITY.md) is the whole picture, including which half of it Windows does not
cover, and how to report something.

## Docs

- [How a sitting works, and why](docs/how-it-works.md): the learning loop, what the ladder
  is, and the grading rules.
- [Configuration](docs/configuration.md): environment, data root, Docker, release verification
- [Authoring a task](docs/authoring-tasks.md): tiers, difficulty, tags, the folder format
- [CONTEXT.md](CONTEXT.md): the vocabulary the code, the API and the UI all use
- [DESIGN.md](DESIGN.md): the UI brief; [`web/README.md`](web/README.md) for the frontend
- [docs/adr/](docs/adr/): decisions worth their own page

## Contributing

The most useful contribution is a new task. Open an issue with the **New task** template first,
then read [CONTRIBUTING.md](CONTRIBUTING.md) for the dev loop and the contract a task is graded
against, and [AGENTS.md](AGENTS.md) for how the project decides things. Bugs and ideas go in
[Issues](https://github.com/vazome/drillion/issues); a vulnerability goes through
[SECURITY.md](SECURITY.md), which also spells out what running drillion does to your machine.

## License

MIT. See [LICENSE](LICENSE). 89 of the 267 tasks adapt a problem from Exercism's Python track
(also MIT), 13 adapt reference code from Fluent Python's examples and six from
TheAlgorithms/Python (both MIT), and one restates a problem from MBPP (CC-BY-4.0); each
names its origin in a `source:` field and an
attribution footer, and [NOTICE](NOTICE) reproduces the notices that travel with them.
