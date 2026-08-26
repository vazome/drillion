# Changelog

Hand-written, newest first. drillion follows [semantic versioning](CONTRIBUTING.md#versioning)
against its public surface: the CLI, the HTTP API, the `progress.json` schema, and the
task-folder format. The version is declared once, in `pyproject.toml`.

## 0.1.0 — unreleased

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
- A container image that runs the same app against a mounted content root.

### Releasing

Bump `version` in `pyproject.toml`, move the heading above from `unreleased` to the date, then
tag the release commit. CI refuses a tag whose name disagrees with the declared version.

```bash
git tag -a v0.1.0 -m "drillion 0.1.0" && git push origin v0.1.0
```
