# drillion

[![PyPI](https://img.shields.io/pypi/v/drillion)](https://pypi.org/project/drillion/)
[![Python](https://img.shields.io/pypi/pyversions/drillion)](https://pypi.org/project/drillion/)
[![CI](https://github.com/vazome/drillion/actions/workflows/ci.yml/badge.svg)](https://github.com/vazome/drillion/actions/workflows/ci.yml)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/14269/badge)](https://www.bestpractices.dev/projects/14269)
[![License](https://img.shields.io/pypi/l/drillion)](https://github.com/vazome/drillion/blob/main/LICENSE)

TL;DR: self-hosted Python practice with a UI that stays out of your way. No streaks,
no leaderboard nonsense, no badges and no engagement bait. Made by a neurodivergent
engineer. It is simple, and it runs your code in a sandbox.

Longer: drillion is a local web app with 171 short Python tasks, each tagged with the
concept it drills so you can go straight at whatever you're worst at. No login, no
account, no server except the one on your laptop. Tasks are folders of Markdown and
Python. Your progress is a single JSON file.

| | Light | Dark |
| --- | --- | --- |
| **The editor**<br><sub>the editor completing a list method</sub> | [![The editor, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/completions-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/completions-light.png) | [![The editor, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/completions-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/completions-dark.png) |
| **A task**<br><sub>spec on the left, your code and the test output on the right</sub> | [![A task, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-screen-1-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-screen-1-light.png) | [![A task, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-screen-1-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-screen-1-dark.png) |
| **The catalogue**<br><sub>today's picks, the tags, the whole table</sub> | [![The catalogue, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/catalogue-screen-1-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/catalogue-screen-1-light.png) | [![The catalogue, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/catalogue-screen-1-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/catalogue-screen-1-dark.png) |
| **Progress**<br><sub>the ladder, what is due, where each topic sits</sub> | [![Progress, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/progress-1-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/progress-1-light.png) | [![Progress, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/progress-1-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/progress-1-dark.png) |

Every `solve()` says what it takes, so the editor knows what your value can do. Completions,
signatures and type errors come from a language server running next to the grader, on your
machine — nothing is sent anywhere.

## But why?

I have tried a lot of learning platforms. Some stuck better than others, and there was
plenty I did not like — the gamification and the ratings above all. I simply do not care
about them. I came for one thing: to keep my Python sharp and learn new things, not to
chat about it with peers.

I took heavy inspiration from Exercism, HackerRank and — surprisingly — Anki, and built
it from scratch.

Core ideas, and the reason each one is there:

- **A clean UI that does not gate the task.** Nothing stands between opening drillion and
  writing code. No modal, no tour, no "complete your profile".
- **Categorisation you can actually navigate.** Every task is tagged with the concept it
  drills, and a tag spans many tasks, so you can go straight at the thing you are worst at
  instead of grinding a track in order.
- **Anki-like progression.** A task comes back before you forget it, with a daily cap so a
  backlog cannot bury you. When one topic keeps beating you, Today names it rather than
  leaving you to notice.
- **An editor that behaves like an IDE without the complexity of one.** Every `solve()` is
  typed, so completions, signatures and inline type errors are real — they come from a
  language server running next to the grader, on your machine. Nothing writes the answer
  for you. The point is to know it, not to accept it.
- **Hints unlock; they are not free.** Three per task, escalating from a nudge to the same
  idea worked through on different data, and they open on attempts and time spent. After
  half an hour with no submission, drillion suggests taking one — you cannot brute-force
  something you are unaware of.
- **Grading is the real thing.** Your code is spliced into the task's own pytest file and
  run. No string matching, no hidden judge, and `drillion selfcheck` proves all 171 tasks
  still pass against their own reference solutions.
- **Your progress is yours.** One JSON file on your disk. drillion stamps it with a schema
  version and refuses to rewrite a file a newer version wrote, rather than quietly
  mangling it. It is the only thing here you cannot redo.
- **It is free, and it stays free.** No tier, no voucher, no account, no telemetry. If I
  stop working on it tomorrow, the copy you cloned still runs.

One consequence worth stating plainly: 171 tasks ship as executable Python, and `task.py`
runs on import. So the sandbox is not a badge I bolted on to look serious — it is the
price of shipping tasks as code, and it is why graded code is confined by the kernel
rather than by my word. **What running it does to your machine**, below, is the detail.

## Install

You do not need Python, and you do not need to know what a virtual environment is. Pick your
system below, run two commands, and drillion opens in your browser at
<http://127.0.0.1:8765>. It runs on your machine — nothing is uploaded and there is no account.

### Linux, macOS, or Windows with WSL

Open a terminal. Install [uv](https://docs.astral.sh/uv/), which is the one tool drillion needs:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Close the terminal and open a new one**, so it picks up the new command. Then:

```bash
uvx drillion
```

The first run takes a minute — it is fetching Python and drillion. After that it starts in
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
Linux and macOS — Windows blocks what it can write, not what it can read.
[SECURITY.md](SECURITY.md) says exactly which half is which.

### Using it day to day

- **Stop it**: press `Ctrl+C` in the terminal window.
- **Start it again**: `uvx drillion`, in any terminal.
- **Update**: nothing to do. `uvx` fetches the current version each time.
- **Your work is kept** between runs, and an update never overwrites it.

Want a permanent `drillion` command instead of typing `uvx` every time? Either of these
installs one:

```bash
uv tool install drillion    # uv tool upgrade drillion to update
pip install drillion        # the same, if you already have Python 3.13+ and no uv
```

### Docker

Same on every system, if you already run Docker:

```bash
docker run -p 127.0.0.1:8765:8765 -v drillion:/data ghcr.io/vazome/drillion
```

Open <http://127.0.0.1:8765> yourself — the container never opens a browser. The image carries
the tasks and the page; the named volume keeps your work across upgrades.
[compose.yaml](compose.yaml) is the same thing plus `restart: unless-stopped`, so drillion comes
back after a reboot; save that one file anywhere and `docker compose up -d`.

## Commands

```bash
drillion              # serve the web UI (default)
drillion selfcheck    # solve every task with its own reference — proves the set still works
drillion doctor       # say why a task folder would be skipped
```

## Your progress

Everything drillion owns lives under one root: `tasks/`, which is where your code is saved, and
`progress.json`, which holds your cards, notes and archived solutions. From a clone that root is
the checkout. Installed, it is a per-user data directory that the first run seeds from the tasks
inside the wheel. In Docker it is the volume at `/data`. An upgrade never writes over a root that
already has tasks in it, so nothing you have written is at risk.
See [docs/configuration.md](docs/configuration.md) for the environment variables and the Docker
bind-mount recipe.

## What running it does to your machine

drillion runs Python on your computer — the code you write, and the code that ships inside the
171 tasks. So it is worth saying plainly what that costs you.

- **Your submissions are confined by the kernel, not by a promise.** Landlock on Linux, an
  `sandbox-exec` profile on macOS, a restricted token at low integrity on Windows. On Linux and
  macOS graded code reads only the interpreter, the system libraries and the tasks, writes only
  to a scratch directory deleted after the run, and cannot open a network connection. Windows
  confines the writes but not the reads or the network. `drillion doctor` prints the tier you
  actually got, read back from a process that tried it.
- **Nothing leaves your machine.** No account, no telemetry, no fonts or scripts fetched from
  anyone. The server binds `127.0.0.1`, and refuses a request from a page it did not serve — so a
  website you happen to have open cannot drive your local drillion.
- **What you downloaded can be checked.** Every release carries provenance naming the workflow
  run that built it, attached to the release itself:

  ```bash
  gh attestation verify drillion-0.5.1-py3-none-any.whl --repo vazome/drillion
  gh attestation verify oci://ghcr.io/vazome/drillion:0.5.1 --repo vazome/drillion
  ```

[SECURITY.md](SECURITY.md) is the whole picture, including which half of it Windows does not
cover and how to report something.

## Docs

- [How a sitting works, and why](docs/how-it-works.md) — the learning loop, what is the ladder and grading rules.
- [Configuration](docs/configuration.md) — environment, data root, Docker, release verification
- [Authoring a task](docs/authoring-tasks.md) — tiers, difficulty, tags, the folder format
- [CONTEXT.md](CONTEXT.md) — the vocabulary the code, the API and the UI all use
- [DESIGN.md](DESIGN.md) — the UI brief; [`web/README.md`](web/README.md) for the frontend
- [docs/adr/](docs/adr/) — decisions worth their own page

## Contributing

The most useful contribution is a new task. Open an issue with the **New task** template first,
then read [CONTRIBUTING.md](CONTRIBUTING.md) for the dev loop and the contract a task is graded
against, and [AGENTS.md](AGENTS.md) for how the project decides things. Bugs and ideas go in
[Issues](https://github.com/vazome/drillion/issues); a vulnerability goes through
[SECURITY.md](SECURITY.md), which also spells out what running drillion does to your machine.

## License

MIT — see [LICENSE](LICENSE). 84 of the 171 tasks carry Markdown adapted from Exercism's Python
track (also MIT); each names its origin in a `source:` field and an attribution footer, and
[NOTICE](NOTICE) reproduces the notice that travels with them.
