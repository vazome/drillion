# drillion

[![PyPI](https://img.shields.io/pypi/v/drillion.svg)](https://pypi.org/project/drillion/)
[![CI](https://github.com/vazome/drillion/actions/workflows/ci.yml/badge.svg)](https://github.com/vazome/drillion/actions/workflows/ci.yml)

Python practice drills that come back before you forget them. Graded by pytest, runs on your machine.

drillion is a local web app with 171 short Python tasks, each tagged with the concept it
practises so you can go straight at what you want to get better at. Every task ships its own
pytest test and generates fresh random data each time you open it, so you cannot pass it by
remembering last week's answer. Pass one and it returns in 2, 4, 8, 16 then 28 days; fail and it
costs you nothing but the attempt. There is no login, no account and no server but yours: the
tasks are folders of Markdown and Python on your disk, and your progress is one JSON file.

## Install

```bash
uvx drillion                                   # run it without installing anything
pip install drillion && drillion               # or install it
docker run -p 127.0.0.1:8765:8765 -v drillion:/data ghcr.io/vazome/drillion
```

Needs Python 3.13. It serves <http://127.0.0.1:8765> and opens your browser.

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
