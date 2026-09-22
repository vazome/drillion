<picture align="center">
  <img alt="drillion" src="https://raw.githubusercontent.com/vazome/drillion/main/docs/images/drillion-github-banner-transparent.svg">
</picture>

---

# drillion: Python practice, on your machine

[![CI](https://github.com/vazome/drillion/actions/workflows/ci.yml/badge.svg)](https://github.com/vazome/drillion/actions/workflows/ci.yml)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/14269/badge)](https://www.bestpractices.dev/projects/14269)
[![License](https://img.shields.io/github/license/vazome/drillion)](https://github.com/vazome/drillion/blob/main/LICENSE)

TL;DR: self-hosted Python practice with a UI that stays out of your way. No streaks,
no leaderboard nonsense, no badges and no engagement bait. Made by a neurodivergent
engineer. It is simple, and it runs your code in a sandbox.

Longer: drillion is a local web app with 305 short tasks, 267 in Python, 18 Kubernetes
manifests, 10 Helm charts and 10 Dockerfiles, each tagged with the
concept it drills so you can go straight at whatever you're worst at. No login, no
account, no server except the one on your laptop. Tasks are folders of Markdown, Python and
YAML. Your progress is a single SQLite file you can copy, back up and carry.

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
- **Anki-like progression.** Tasks return on a fixed review ladder, with a daily cap so a
  backlog cannot bury you.
- **An editor that behaves like an IDE without the complexity of one.** Every `solve()` is
  typed, so completions, signatures and inline type errors are real as they come from a
  language server running next to the grader, on your machine.
- **Hints unlock and they are not free.** Three per task, escalating from a nudge to the
  same idea worked through on different data. After half an hour with no submission,
  drillion suggests taking one as you cannot brute-force something you are unaware of.
- **Grading is real.** A Python answer is spliced into the task's own pytest file and run; a
  manifest is validated by kubeconform, then checked against the task's own rules.
- **YOUR progress.** One SQLite file on your disk, stamped with a schema version, and a
  build refuses to rewrite a file a newer one wrote rather than quietly mangling it. Settings
  turns it into a backup you can carry, and can erase the lot if you want to start over.
- **It is free, and it stays free.** No tier, no voucher, no account, no telemetry,
  open-source.

One consequence worth stating plainly: every task ships executable Python, a manifest or Helm task's in
its `grade.py`, and it runs on import. Shipping tasks as code is what makes the sandbox necessary, so graded code
is confined by the kernel and you do not have to take my word for it. **What running it
does to your machine**, below, is the detail.

## Run

Drillion is distributed as a Docker image. Install Docker Engine on Linux or Docker Desktop on
macOS or Windows, then start it:

```bash
docker run -d --name drillion --restart unless-stopped -p 127.0.0.1:8765:8765 -v drillion:/data ghcr.io/vazome/drillion
```

Open <http://127.0.0.1:8765>. The image never opens a host browser. Your work lives in the
`drillion` volume, which outlives the container. [compose.yaml](compose.yaml) runs the same
container read-only with every capability dropped: save it anywhere and `docker compose up -d`.

To update, pull the new image and replace the container. Removing the container keeps the volume:

```bash
docker pull ghcr.io/vazome/drillion && docker stop drillion && docker rm drillion && docker run -d --name drillion --restart unless-stopped -p 127.0.0.1:8765:8765 -v drillion:/data ghcr.io/vazome/drillion
```

With Compose, `docker compose pull && docker compose up -d` from the folder holding
`compose.yaml`. Compose names its volume after that folder, so it is not the `drillion` volume.

For a reproducible rollback, replace `ghcr.io/vazome/drillion` with `ghcr.io/vazome/drillion:<version>`
or the immutable `ghcr.io/vazome/drillion@sha256:...` reference in that release's notes **only when that
release is compatible with the data already in the volume**. Before a major upgrade, back up from
**Settings → Back up**. To return to an older, incompatible release, restore that backup into a
separate volume rather than reusing the upgraded one.

## Commands

```bash
docker exec drillion drillion selfcheck  # solve every task with its own reference
docker exec drillion drillion doctor     # report why a task folder would be skipped
```

## What running it does to your machine

drillion runs Python on your computer: the code you write, and the code that ships inside the
305 tasks. So it is worth saying plainly what that costs you.

- **Your submissions are confined by the Linux kernel, where it allows.** The image runs them with
  Landlock: they read only the interpreter, system libraries and tasks, and write only to a scratch
  directory deleted after the run. On Landlock ABI 4 and newer (Linux 6.7) they cannot open a TCP
  connection either. An older kernel, or a container policy that blocks Landlock, leaves only an
  in-process guard that is a speed bump rather than a boundary; `drillion doctor` prints the tier a
  probe process actually obtained. `compose.yaml` also runs the container read-only with every
  capability dropped, so even then nothing outside `/data` and `/tmp` can be changed.
- **Nothing leaves your machine.** No account, no telemetry, no fonts or scripts fetched from
  anyone. The server binds `127.0.0.1`, and refuses a request from a page it did not serve, so
  a website you happen to have open cannot drive your local drillion.
- **What you downloaded can be checked.** Every image carries provenance naming the workflow run
  that built it:

  ```bash
  gh attestation verify oci://ghcr.io/vazome/drillion:0.8.0 --repo vazome/drillion
  ```

[SECURITY.md](SECURITY.md) is the whole picture and explains how to report something.

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

MIT. See [LICENSE](LICENSE). 89 of the 305 tasks adapt a problem from Exercism's Python track
(also MIT), 13 adapt reference code from Fluent Python's examples and six from
TheAlgorithms/Python (both MIT), and one restates a problem from MBPP (CC-BY-4.0); each
names its origin in a `source:` field and an
attribution footer, and [NOTICE](NOTICE) reproduces the notices that travel with them.
