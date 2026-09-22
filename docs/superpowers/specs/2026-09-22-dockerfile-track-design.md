# Dockerfile tasks: design

Status: built on `feat/docker-track`, stacked on `feat/helm-concept`.

## What the learner does

A Dockerfile task is a build context with one file missing. The task ships an app under
`context/` (`app.py`, `requirements.txt`, `main.go`, `package.json` and so on), shown read-only
in the same `FileTabs` strip a Helm chart uses. The learner writes the `Dockerfile`. Compose
is out on purpose: where Kubernetes runs things, the image is what crosses from a laptop to
production, and a Compose file rarely does.

## What grading can and cannot see

drillion grades inside a read-only container with every capability dropped, under Landlock,
with no network. There is no Docker daemon and no BuildKit, so nothing is built or run. A
learner never sees their image start. Running it is left to a future cloud tier that can
execute a learner's work remotely.

A submission goes through three checks in order, and stops at the first that fails:

1. **hadolint v2.15.1**, pinned by checksum like kubeconform and Helm, run as
   `--disable-ignore-pragma -f json` with drillion's own config. Errors and warnings fail;
   info findings are shown as advice and never fail. DL3008 and DL3018 (pin every apt or apk
   package version) are switched off: few teams follow them, since a pinned Debian version
   leaves the mirror. `# hadolint ignore=` comments are ignored, so a learner cannot silence
   a rule. A Dockerfile that does not parse is hadolint's DL1000, with its line.
2. **The build context.** Every `COPY` or `ADD` source that is not `--from` a stage must match
   a file in `context/`. This is the one "does not build" mistake that can be caught without
   building.
3. **`check(stages, brief)`** in the task's `grade.py`. `stages` is the Dockerfile parsed
   into its build stages, each `{"base", "name", "line", "globals", "steps"}`, and each step
   `{"cmd", "args", "flags", "exec", "words", "line"}`. `exec` is the JSON array of an
   exec-form instruction and `None` for shell form. `globals` are the `ARG`s above the first
   `FROM`, which belong to no stage.

Each hadolint diagnostic names the `Dockerfile` and its line, so the editor marks the line,
as it does for a Helm error in the learner's own file.

## How it fits

- A fourth kind, `docker`, built on the manifest kind: a seeded brief, a README rendered
  against it, `grade.py`, and an answer key in `solution.Dockerfile` filled with plain
  `str.format` placeholders. Braces a Dockerfile really needs (`${VAR}`) are doubled in it.
- `edits: Dockerfile`, as a Helm task names its hole. The learner's file on disk is
  `Dockerfile`.
- A verdict is fingerprinted `d1:`: the grader's files, the hadolint pin and drillion's
  hadolint config. kubeconform is not involved and is not required.
- Track `docker`, logo from devicon v2.16.0 like the others.

## The first ten tasks (289 to 298)

| # | Task | What it drills |
|---|------|----------------|
| 289 | first image | a tagged slim base, `WORKDIR`, `COPY`, exec-form `CMD`, `EXPOSE` |
| 290 | layer cache | dependency manifest copied and installed before the source |
| 291 | non-root | a system user with a numeric UID, `USER`, `COPY --chown` |
| 292 | ARG and ENV | build-time version against runtime config |
| 293 | apt done right | one `RUN`: update, `--no-install-recommends`, lists removed |
| 294 | ENTRYPOINT and CMD | exec form so PID 1 gets SIGTERM, CMD as default arguments |
| 295 | pinned base | a base image pinned by digest, OCI labels saying where it came from |
| 296 | multi-stage Go | static build, `scratch` or distroless runtime, only the binary copied |
| 297 | multi-stage Python | a virtualenv built in one stage, copied into a slim runtime |
| 298 | static site | a Node build stage served by an unprivileged nginx |

## Not now

- Building or running the image (the cloud tier).
- `.dockerignore` as the learner's file: `edits` allows only `Dockerfile` until a task needs it.
  The context check does not apply `.dockerignore` either.
