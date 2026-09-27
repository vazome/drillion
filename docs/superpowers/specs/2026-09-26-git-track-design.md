# Git tasks: design

Status: agreed in conversation up to grading (the terminal, real git, the image cost, the
scope and the editors). The shell's sandbox and lifetime, the surfaces, the first tasks and
testing below are for review.

## Scope

Four areas, every one offline:

- **Everyday local work**: `status`, `add -p`, `commit`, `--amend`, `restore`, `stash`,
  `.gitignore`, `log` and `diff` with filters.
- **Merging and conflicts**: fast-forward and merge commits, a conflict resolved in an
  editor, `merge --abort`, `cherry-pick`.
- **Rewriting and rescue**: `rebase`, `rebase -i` (squash, fixup, reword, drop,
  `--autosquash`), `reset --soft/--mixed/--hard`, `reflog`, `revert`, `bisect`.
- **Remotes**: a bare `origin.git` beside the repo stands in for the server. `fetch`,
  `pull --rebase`, `push -u`, tracking branches, `--force-with-lease`, a diverged `main`.

Out: hosting (pull requests, GitHub), submodules, LFS, signing, hooks as a subject, and any
network transport.

## What the learner does

A git task is a repository in a state, and a spec saying what state it should be in. The
learner gets a real terminal, a real `bash` and real `git`, opened inside that repository.
They work the way they would at their desk, with `git log` as the "You get", and press Run
to check the repository as it stands (free) or Submit to be graded, as in every other kind.

```
tasks/339_git_first_commit/
  README.md     kind: git, track: git, tags, prereqs, minutes; spec with {placeholders}
  grade.py      brief(r), setup(repo, b), and optionally probes(b), check(repo, b)
  solution.sh   the answer key, the commands, with the same {placeholders}
  history.sh    the learner's file: their shell history, empty as shipped
```

- `brief(r)` picks the sitting's parameters, as a Dockerfile task's does: file names, branch
  names, the string a commit introduced. It is stored on the sitting and the README is
  rendered against it.
- `setup(repo, b)` builds the starting state with git itself, through `tasks/_git.py`, a
  small helper that commits files with a clock that advances one minute per commit from a
  fixed epoch, so a seed always yields the same SHAs. It can leave work uncommitted, a stash,
  a merge half done, and a bare `origin.git` a "teammate" has pushed to.
- `solution.sh` is a bash script run with `set -e`, rendered with `str.format` like
  `solution.Dockerfile` (braces bash needs are doubled). An interactive step is scripted:
  `GIT_SEQUENCE_EDITOR="sed -i ..." git rebase -i`, or a file written with `printf`.

**The learner's artifact is `history.sh`**: bash appends every command to it as it runs
(`PROMPT_COMMAND='history -a'`, `HISTFILE` pointed at it). It is one text file, like every
other kind's, so attempts, the archive, backup, the pending-reset machinery and ADR 0008's
upgrade rule all handle it unchanged. The archive shows a pass as the commands that
produced it. The page never writes this file: the git kind's `validate` returns what is on
disk, and its `etag` is a constant, so a Run or Submit from the page cannot overwrite what
bash wrote.

**The repository is work in progress, and never the artifact.** It lives in
`<root>/.sittings/<slug>/` (`repo/`, `origin.git/`, `home/`), stamped with the sitting's
`started` in `<root>/.sittings/<slug>.started`, beside it: the shell owns everything inside
the sitting, so the server never writes a file there once it is built, nor trusts one. It survives a reload and a restart. It is built when the terminal connects and
finds no directory, or one stamped for another sitting, which is how a pass, an abandon and an
upgrade all end up with a fresh repo without a hook in any of them. When an upgrade rebuilt
the repository of an attempt still open, the terminal says so before the prompt, and a Run
that finds it first refuses without spending the attempt. A restore or an erase is
not lazy about it: the route ends every open terminal and deletes `<root>/.sittings` outright
before it returns, so the next connect still finds nothing and builds fresh, just already
emptied rather than found stale.
**Reset repository** (a button beside Submit) ends the shell, deletes the directory, and
appends `# repository reset` to `history.sh`; the next connect builds it again from the
stored brief and seed.

## How it is graded

Run and Submit grade `.sittings/<slug>/` where it lies. The grading child gets it as a
read-only Landlock root and runs every git in it with `GIT_OPTIONAL_LOCKS=0`, which git
provides so that `status` never takes the index lock. Nothing is copied, so a FIFO or a
huge file the learner made costs the grader nothing. In the same sandboxed child, the
answer key is built in scratch: `setup()` from the sitting's seed, then `solution.sh` run
in it with `GIT_EDITOR=true`. The same probes then read both.

**Commit identity without dates.** The learner's commits carry today's date and the key's
carry another, so SHAs never agree. Each commit is compared by a **content id**: the hash of
its subject, its tree hash and its parents' content ids in order. A tree hash depends only
on file contents and names, so a commit rebuilt with the same files, message and history has
the same content id whoever made it and when. A merge commit's parents stay in order, so
merging the wrong way round differs.

**Default probes**, over the local repository and over `origin.git` alike:

| Probe | Compared |
|---|---|
| every ref the answer key ends with | its content id; tags included |
| every ref `setup()` made that the key deleted | it must be gone |
| `HEAD` | the branch checked out, or detached |
| the index and working tree | `git status --porcelain=v1 -z --untracked-files=all`, and each changed path's staged and unstaged content by blob id (a non-regular file by its type, never opened) |
| an operation in progress | `MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`, `rebase-merge/`, `rebase-apply/`, `BISECT_LOG` |
| `refs/stash` | each entry's contents (its tree, index and untracked blobs), not only the count |

Refs the learner made that the key does not have are ignored: a backup branch before a
rebase is good practice, and failing it would teach the opposite.

Content ids make typed text exact: a subject is compared as written, and a file's bytes are
part of its tree. So a spec gives every commit message it expects, in a code span, and a
conflict task says what the resolved file must contain. Where the learner's own wording is
the point (a reworded message, a hand-merged paragraph), the task skips the ref probe and
asks in `check()` instead: the subject starts with the ticket number, both sides' lines are
present and no marker is left.

**What a task adds.** `SKIP`, a tuple in `grade.py`, drops default probes by name (`refs`,
`deleted`, `head`, `status`, `operation`, `stash`): a task about `stash` may not care what
`HEAD` is. `probes(b)` returns `{sentence: argv}`, git commands run in both repositories
and compared, the sentence being what the learner reads when they differ ("the files git
ignores"). `check(repo, b)` is optional, for rules a comparison
cannot express, githug-style: "the commit lost to `reset --hard` is reachable from `main`
again", "the tag points at the first bad commit". It gets the `_git.Repo` helper over
the graded repository, with `git(...)`, `log(ref)` and `ref(name)`, and fails with `AssertionError`.

**The failure message** is the first difference, in the learner's words, and in full: there
is no hidden dataset, so nothing needs hiding. `main is 4 commits ahead of where it should
be; the 3rd from the tip is "wip", expected "add parser"`. `HEAD is on feature, expected
main`. `a merge is still in progress: finish it with git commit or back out with git merge
--abort`. `origin/main is missing "fix typo"`.

**The repository is untrusted input to the grader.** The learner controls `.git/config`, and
config can run commands (`core.fsmonitor`, `diff.external`) or change output (`log.*`,
`format.*`). Probes use plumbing with explicit formats (`for-each-ref`, `rev-list`,
`cat-file`, `rev-parse`, `status --porcelain`) and run with `GIT_CONFIG_NOSYSTEM=1`,
`GIT_CONFIG_GLOBAL=/dev/null` and `-c core.fsmonitor= -c core.hooksPath=/dev/null`, and `GIT_NO_REPLACE_OBJECTS=1` so `git replace` cannot rewrite history for the grader. The repository
is graded inside the same sandbox as every other grade, so whatever config is left runs
confined.

**Verdict fingerprint** `g1:`: the grader's files, `solution.sh`, `tasks/_git.py`, the git
version (`git --version`), and drillion's `GIT_*` environment.

## The terminal

**Transport.** A WebSocket at `/terminal/{slug}`, origin-checked like `/lsp`, refused
without an open attempt. Server to page: binary frames, the PTY's bytes as they come. Page
to server: JSON text frames, `{"i": "<keys>"}` for input and `{"r": [cols, rows]}` for a
resize, applied with `TIOCSWINSZ`. Nothing else crosses: no file channel, no side protocol.

**The shell.** `bash --noprofile --rcfile <root>/.sittings/.drillionrc` on a PTY from `os.openpty`,
started through `subprocess.Popen` with the sandbox's `preexec` plus `setsid()` and
`TIOCSCTTY`, so Ctrl-C reaches `git` and Ctrl-Z can suspend `vim`. No new Python
dependency: stdlib `pty`, `fcntl`, `termios`, with the read side on the event loop through
`loop.add_reader`. The rc file sets a prompt with the branch (`__git_ps1` from
`/usr/lib/git-core/git-sh-prompt`), loads git's bash completion, and sets `HISTFILE`,
`PROMPT_COMMAND`, `EDITOR=nano` and `VISUAL=nano`. Debian's `vim-tiny` installs only `vi`, so the rc file aliases `vim` to it,
and `export EDITOR=vi` switches git's editor.

**The sandbox.** The shell is a sandboxed child like any grade, with the sitting directory
as its scratch (read, write, execute), `history.sh` added as the one writable file
outside it, and the rc file as one it may read. Landlock's existing roots already allow what `bash`, `git`, `nano` and `vim`
read (`/usr`, `/etc`, `/lib`), and `/dev` already carries `ioctl_dev`, which a TTY needs
for raw mode on ABI 5 and later. TCP stays denied. The environment is `sandbox.environ` with
`HOME` at `home/`, plus `TERM=xterm-256color`, `LANG=C.UTF-8`, and git's own isolation:

- `GIT_CEILING_DIRECTORIES=<root>/.sittings`: in a checkout the data root sits inside
  drillion's own repository, and git would otherwise walk up into it.
- `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=<home>/.gitconfig`, which drillion writes
  with a learner identity and `init.defaultBranch=main`.
- `GIT_ALLOW_PROTOCOL=file`: remotes are local paths and nothing else.

`RLIMIT_CPU` is per process, so it bounds a runaway command without timing out a shell
someone is thinking in. The process cap is the sandbox's usual headroom.

**Lifetime.** One shell per task: a second socket for the same slug ends the first (the
newer tab wins). At most four shells at once, past which the socket closes with 1013, as
`/lsp` does. The socket closing sends `SIGHUP` to the shell's process group and `SIGKILL`
two seconds later. The repository is on disk, so a reload loses the scrollback and nothing
else. No idle timeout: an idle `bash` costs nothing, and the socket's life bounds it.

**On a tier without Landlock** (a macOS checkout, a kernel without it) the shell still
starts, with the environment and rlimits but without the filesystem confinement: a shell as
the user who started drillion, on their own machine. The terminal's first line says which
tier it runs under, from `sandbox.status()`.

## Engine and image

Debian's `git` (2.47.3 in `python:3.14-slim` today), `nano`, `vim-tiny` and `less` (git's
pager), installed with `--no-install-recommends` in the runtime stage, before `useradd`.
Measured: 34 packages and
about 100 MB (git 49 MB, perl 49 MB as git's hard dependency), bringing `libcurl-gnutls`,
krb5, ldap and libssh2 that a `file://`-only setup never exercises. The existing
`apt-get upgrade` line keeps them current; trivy's count rises and the ADR says so. Not a
pinned tool in `tools.py`: git publishes no static build, and Debian's patches are the
point.

A checkout uses the host's `git`, `bash` and `nano`. A git task with no `git` on `PATH` says
so and names the install, as a manifest task with kubeconform absent names `doctor --fetch`.
`doctor` reports the git version, and opening a git task refuses a git older than 2.40.

## Surfaces

- **Task page.** The spec on the left, the terminal where the editor sits. No file tabs.
  Run, Submit, Reset repository, hints, the solution and Abandon, as for other kinds. The
  editor keybinding setting (vim, emacs) does not apply to the terminal, and the page's own
  shortcuts must not take keys a shell needs (Ctrl-R, Ctrl-W, Ctrl-A, Escape): inside the
  terminal only Submit's shortcut is the page's.
- **Terminal component.** xterm.js (`@xterm/xterm` 6 with `@xterm/addon-fit`), themed with
  drillion's colours in light and dark. A new UI component, requested from the maintainers
  per AGENTS.md; the socket protocol above is the whole contract between it and the server.
  A new web dependency, signed off with the component.
- **Result panel.** The failure message and the probe that produced it, through the
  diagnostics list the other non-Python kinds already render.
- **Solution and archive.** `solution.sh` rendered for the sitting, and each archived pass's
  `history.sh`, highlighted with Monaco's `shell` language.
- **Catalogue.** Track `git`, logo from devicon like the others. Tags follow the tag rule:
  `staging`, `commits`, `branches`, `merging`, `conflicts`, `rebase`, `history-rewriting`,
  `undo`, `stash`, `remotes`, `history-search`, `tagging`. Each is on at least two tasks.
- **Entry points.** Catalogue, task page, lineage panel, a review and a new pick all open the
  same page; none needs its own path. Backup carries `history.sh` through the kinds'
  artifact set; a restored sitting gets a fresh repository on its next connect.
- **Run modes.** The image carries git; a checkout uses the host's. Verified in the image.

## Proof

- **selfcheck** runs `solution.sh` as the learner in a fresh `setup()` and requires a pass,
  and grades the untouched `setup()` repository and requires a fail, so no task is solved
  by doing nothing.
- **doctor** rejects a git task with a tier or `edits`, or without `solution.sh`,
  `history.sh` or a `setup` in `grade.py`, checks placeholders as for the other kinds, and
  prints the git version. It does not ask that `history.sh` be empty: doctor reads the
  learner's own root, where an open sitting has filled it.
- **pytest**: content ids (same content on other dates agree; swapped merge parents do not),
  each default probe on a hand-built pair of repositories, the failure messages, a repo whose
  config sets `core.fsmonitor` graded without running it, and the terminal bridge (spawn,
  echo, resize, the newer socket ending the older, kill on close) against a plain shell.
- **screens**: one git task added to the Playwright set, light and dark.

## Docs

- ADR 0013, "a git task is a real repository in a real terminal": the options were an
  in-browser git (isomorphic-git, which has no rebase and no `merge --continue`), a
  git-only command list without a shell, and a browser VM. Real git on a PTY was taken, with
  the image cost stated.
- `CONTEXT.md`: **sitting repository**, **probe**, **content id**; the task counts.
- `docs/authoring-tasks.md`: a git section (`setup`, `_git.py`, `probes`, `check`,
  scripting an interactive step in `solution.sh`).
- `SECURITY.md`: the terminal, and what it can reach on each tier.

## The first eighteen tasks (339 to 356)

Numbered after the SQL track's 324 to 338, which is ahead of this one; if git lands first,
it takes the numbers from 324 and SQL moves up.

| # | Task | Area | What it drills |
|---|------|------|----------------|
| 339 | first commit | local | `status`, staging two of three files, `.gitignore` for the third |
| 340 | stage part of a file | local | `add -p`, one file's changes split into two commits |
| 341 | fix the last commit | local | `--amend` with a forgotten file and a better message |
| 342 | undo changes | local | `restore` a file, `restore --staged` another |
| 343 | stash and switch | local | `stash -u`, a fix on another branch, `stash pop` |
| 344 | find the commit | local | `log -S`, `--author`, a pathspec; tag what was found |
| 345 | merge a branch | merging | fast-forward, then a merge commit for the next branch |
| 346 | resolve a conflict | merging | a conflict fixed in an editor, `add`, `commit` |
| 347 | backport a fix | merging | `cherry-pick` onto a release branch |
| 348 | tidy a branch | rewriting | `rebase -i`: fixup, reword, drop |
| 349 | fixup commits | rewriting | `commit --fixup`, `rebase -i --autosquash` |
| 350 | rebase onto main | rewriting | `rebase` through a conflict, then a fast-forward merge |
| 351 | undo commits | rewriting | `reset --soft` to recommit, `reset --hard` to throw away |
| 352 | rescue with reflog | rescue | a deleted branch and a `reset --hard` undone |
| 353 | first push | remotes | `push -u`, tracking, a new branch pushed |
| 354 | revert, do not rewrite | rescue | `revert` a commit that is already on `origin` |
| 355 | bisect | rescue | `bisect run` with a check script the repo ships; tag the culprit |
| 356 | a teammate pushed first | remotes | `pull --rebase --autostash`, `push --force-with-lease` on your own branch |

## Not now

- A live commit graph beside the terminal, as Learn Git Branching and Oh My Git! draw. A
  good second UI request once the terminal exists.
- Grading how the learner got there (`--force` against `--force-with-lease` leaves the same
  repository): `history.sh` is kept, and a task that needs it can read it in a later version.
- Hooks, submodules, worktrees, LFS, signing, and anything that needs a network.
