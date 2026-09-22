# A Dockerfile task is graded without building it

Where Kubernetes runs production, the image is what crosses from a laptop to the cluster, and
the Dockerfile is what every team still writes, reviews and gets paged over. Compose rarely
leaves the laptop, so drillion drills Dockerfiles and leaves Compose out. The question was how
to grade one when the grader runs in a read-only container with every capability dropped,
under Landlock, and with no network.

The design is
[docs/superpowers/specs/2026-09-22-dockerfile-track-design.md](../superpowers/specs/2026-09-22-dockerfile-track-design.md).

## Considered options

**Build it with BuildKit, rootless, inside the image.** Rejected. It needs user namespaces and
a looser seccomp profile inside the one container learners are told to run hardened, it needs
the network to pull base images, and it turns a verdict that takes milliseconds into one that
takes minutes. Seeing an image build and run is worth having, and it belongs in a cloud tier
that can run a learner's work somewhere else, not here.

**`docker build --check`.** Rejected for the same reason: BuildKit's lint rules run inside
BuildKit, which needs a daemon.

**Grade the Dockerfile as text: hadolint, the build context, then `check()`.** Taken. hadolint
is one static binary with published checksums, pinned the same way as kubeconform and Helm.
It parses the Dockerfile, reports syntax errors with their line, and runs shellcheck over every
`RUN`. drillion's config lets errors and warnings fail and keeps info as advice, and switches
off DL3008 and DL3018 (pin every apt or apk package version), which few teams follow because
a pinned Debian version leaves the mirror. `--disable-ignore-pragma` stops a learner silencing
a rule with a comment. Then every `COPY` source is looked for in the task's build context,
which catches the one "does not build" mistake visible without building. Then the task's own
`check(stages, brief)` reads the parsed stages.

## Consequences

- **A passing Dockerfile has never been built.** A binary compiled for the wrong libc, or a
  `CMD` naming the wrong file, pass unless the task's `check()` asks about them, and the tasks
  that teach those things do.
- **A Dockerfile task needs no kubeconform**, and its verdict is fingerprinted `d1:`: the
  grader's files, the hadolint pin and drillion's hadolint config.
- **The build context is shown in the chart's tabs**, reusing `FileTabs` with its own words.
- **`.dockerignore` is not applied** by the context check, and no task makes it the learner's
  file yet. A task that teaches it widens `edits` and the check together.
