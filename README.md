# drillion

[![PyPI](https://img.shields.io/pypi/v/drillion)](https://pypi.org/project/drillion/)
[![Python](https://img.shields.io/pypi/pyversions/drillion)](https://pypi.org/project/drillion/)
[![CI](https://github.com/vazome/drillion/actions/workflows/ci.yml/badge.svg)](https://github.com/vazome/drillion/actions/workflows/ci.yml)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/14269/badge)](https://www.bestpractices.dev/projects/14269)
[![License](https://img.shields.io/pypi/l/drillion)](https://github.com/vazome/drillion/blob/main/LICENSE)

TL;DR: Self-hosted python practices in effective UI. With no social engagment bait, public rating bullshit and no achievements. Pragmatic and simple by nature.

`drillion` is a local web app with 171 short Python tasks, each tagged with the concept it
practises so you can go straight at what you want to get better at. There is no login, no account and no server but yours: the tasks are folders of Markdown and Python on your disk, and your progress is one JSON file.

| | Light | Dark |
| --- | --- | --- |
| **The editor**<br><sub>the editor completing a list method</sub> | [![The editor, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/completions-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/completions-light.png) | [![The editor, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/completions-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/completions-dark.png) |
| **A task**<br><sub>spec on the left, your code and the test output on the right</sub> | [![A task, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-screen-1-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-screen-1-light.png) | [![A task, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-screen-1-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/task-screen-1-dark.png) |
| **The catalogue**<br><sub>today's picks, the tags, the whole table</sub> | [![The catalogue, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/catalogue-screen-1-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/catalogue-screen-1-light.png) | [![The catalogue, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/catalogue-screen-1-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/catalogue-screen-1-dark.png) |
| **Progress**<br><sub>the ladder, what is due, where each topic sits</sub> | [![Progress, light](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/progress-1-light.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/progress-1-light.png) | [![Progress, dark](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/progress-1-dark.png)](https://raw.githubusercontent.com/vazome/drillion/main/docs/images/progress-1-dark.png) |

Every `solve()` says what it takes, so the editor knows what your value can do. Completions,
signatures and type errors come from a language server running next to the grader, on your
machine — nothing is sent anywhere.

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
