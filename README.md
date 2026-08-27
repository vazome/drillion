# drillion

[![PyPI](https://img.shields.io/pypi/v/drillion.svg)](https://pypi.org/project/drillion/)
[![CI](https://github.com/vazome/drillion/actions/workflows/ci.yml/badge.svg)](https://github.com/vazome/drillion/actions/workflows/ci.yml)

Python practice drills that come back before you forget them. Graded by pytest, runs on your machine.

drillion is a local web app with 171 short Python tasks, each tagged with the concept it
practises so you can go straight at what you want to get better at. Every task ships its own
pytest test, and many draw fresh data each time you open them, so you cannot pass by remembering
last week's answer. Pass one and it comes back in 2 days, then 4, 8, 16, and on up to 120; fail
and it costs you nothing but the attempt. There is no login, no account and no server but yours: the
tasks are folders of Markdown and Python on your disk, and your progress is one JSON file.

## Install

Any of these serves <http://127.0.0.1:8765>. The first three need Python 3.13 or newer and open
your browser for you; Docker needs nothing but Docker, and opens nothing.

### Try it — `uvx`

```bash
uvx drillion
```

Downloads, runs, and leaves nothing installed. Your progress still persists between runs; only
drillion itself is temporary.

### Keep it — `uv tool install`

```bash
uv tool install drillion
drillion
```

Puts `drillion` on your PATH. `uv tool upgrade drillion` updates it.

### Keep it — `pip`

```bash
pip install drillion
drillion
```

The same thing without uv. Use a virtualenv if you keep your system Python clean.

### Docker

```bash
docker run -p 127.0.0.1:8765:8765 -v drillion:/data ghcr.io/vazome/drillion
```

The image carries the tasks and the page; the named volume keeps your work across upgrades.
Open <http://127.0.0.1:8765> yourself — the container never opens a browser.
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

- [How a sitting works, and why](docs/how-it-works.md) — the loop, the ladder, the grading rules
- [Configuration](docs/configuration.md) — environment, data root, Docker, release verification
- [Authoring a task](docs/authoring-tasks.md) — tiers, difficulty, tags, the folder format
- [CONTEXT.md](CONTEXT.md) — the vocabulary the code, the API and the UI all use
- [DESIGN.md](DESIGN.md) — the UI brief; [`web/README.md`](web/README.md) for the frontend
- [docs/adr/](docs/adr/) — decisions worth their own page

## Contributing

The most useful contribution is a new task. Open an issue with the **New task** template first,
then read [CONTRIBUTING.md](CONTRIBUTING.md) for the dev loop and the contract a task is graded
against, and [AGENTS.md](AGENTS.md) for how the project decides things. Bugs and ideas go in
[Issues](https://github.com/vazome/drillion/issues).

## License

MIT — see [LICENSE](LICENSE). 84 of the 171 tasks carry Markdown adapted from Exercism's Python
track (also MIT); each names its origin in a `source:` field and an attribution footer, and
[NOTICE](NOTICE) reproduces the notice that travels with them.
