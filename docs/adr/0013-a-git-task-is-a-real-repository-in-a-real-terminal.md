# A git task is a real repository in a real terminal

Every team that ships code lives inside git, and the parts that actually cost time are the
parts a syntax quiz cannot reach: an editor opened mid-rebase, a conflict with both sides
still in the file, a remote that has moved since the last fetch. The question was how to
give a learner that, inside a container that is read-only, has every capability dropped, runs
under Landlock, and has no network.

The design is
[docs/superpowers/specs/2026-09-26-git-track-design.md](../superpowers/specs/2026-09-26-git-track-design.md).

## Considered options

**In-browser git**, as git-practice.com runs it with isomorphic-git. Rejected: no rebase and
no `merge --continue`, so the two areas most worth drilling are the two it cannot teach.

**A git-only command list, with no shell underneath it.** Rejected. `nano` and `vim` still
need a PTY to run at all, so a task that reaches a conflict or an interactive rebase needs one
regardless; this option is the one taken below with the shell removed and the PTY kept, which
buys nothing.

**A VM in the browser.** Rejected. It is a 30 MB boot before a learner types anything, and
grading would have to trust state a browser sandbox reports back rather than reading a
repository on disk itself.

**Real git on a PTY, in the sandboxed child every other kind grades in.** Taken. `bash` and
`git` run exactly as they do at a real desk; a `setup()` builds the starting repository with
`tasks/_git.py`, the learner works in it over a WebSocket terminal, and a grade reads the
result straight off disk with the same plumbing every probe already uses.

**`check()`-first grading, with the answer key only proving a task is solvable.** Rejected.
Every task would then carry its own hand-written grader, and whatever an author forgot to
forbid would quietly pass. Taken instead: the default grade compares the learner's repository
with the one the same `setup()` and the answer key build, ref by ref, content id by content
id, the working tree, the stash, and `origin.git` alike; a task turns off a comparison with
`SKIP` and states a rule in `check()` only where the learner's own wording is the point. The
comparison checks everything a task did not think to exempt, and the break harness in
`tests/test_git_tasks.py` proves each rule actually fails when broken.

## Consequences

- **The image grows by 34 Debian packages and about 100 MB**: git alone is 49 MB and pulls in
  perl, another 49 MB, as a hard dependency, plus `libcurl-gnutls`, krb5, ldap and libssh2 that
  a `file://`-only setup never exercises. `nano`, `vim-tiny` and `less` (git's pager) add
  little beside it. trivy's count rises, and that is the price of the package, not a
  regression to chase down.
- **The terminal is confined by Landlock where the kernel offers it**, the same as any other
  grade, and runs unconfined as the user who started drillion where it does not; the
  terminal's first line says which.
- **A pass records the repository's end state, never how the learner got there.** `history.sh`
  is kept for the archive and for a learner to reread, but grading never opens it, so
  `--force` and `--force-with-lease` pass alike, and a task that cares about the difference
  has nothing to grade it with yet.
- **A git task's in-progress repository is never in a backup or the archive.** The card's
  progress and `history.sh` are backed up like any other kind's; the repository under
  `.sittings/<slug>/` is not, and a restore, an erase or an upgrade mid-attempt starts a fresh
  one from the stored brief rather than resuming the one the learner was looking at.
- **A grade reads the repository as it stands when Submit arrives.** A command still running
  in the terminal at that moment can go on changing it after the read starts; the usual
  symptom is an unfinished merge or rebase, which the `operation` probe catches by name. This
  is a known limit, not a bug to fix by making Submit wait on the shell.
- **The verdict is fingerprinted `g1:`**: the grader's files, `solution.sh`, `tasks/_git.py`,
  the git version, and drillion's `GIT_*` environment.
