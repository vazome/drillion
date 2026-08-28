# Security

## Threat model

drillion runs arbitrary Python on your machine, by design, and only on your machine. The
sharpest exposure is not a learner attacking themselves: `task.py` executes on import, and
171 of them ship inside the wheel, so a contributed task is code execution on every user's
machine. That is what the sandbox is for.

- **Graded code runs in a sandboxed pytest subprocess** (`src/drillion/sandbox.py`). What it
  can reach depends on what your kernel offers; `drillion doctor` prints the tier in force
  and, when it is not the strongest one, why. Docker is not required for any of it.
- **The server is local and single-user.** It binds `127.0.0.1`, and `TrustedHostMiddleware`
  refuses any host but `127.0.0.1` and `localhost` (`src/drillion/api.py`). There is no
  hosted or multi-user mode, no accounts, and none is planned. Do not expose the port.
- **A task folder is still code, not data.** The sandbox contains a task; it does not make
  reviewing one optional. A contributed task is reviewed the way a pull request is.

## The floor, on every platform

This holds whatever the kernel offers, and it removes the highest-value target on its own.

- **The environment is an allowlist.** `PATH`, `PYTHONPATH`, `LANG` and a few others. Nothing
  else your shell exported reaches task code — `AWS_*`, `GITHUB_TOKEN`, `SSH_AUTH_SOCK` all
  stop at the runner.
- **`HOME` and `TMPDIR` point at the scratch directory** the runner makes and deletes per
  run, so `~/.aws/credentials`, `~/.ssh` and `~/.config` resolve into an empty temp dir.
- **POSIX resource limits** in `preexec_fn`: address space, file size, core dumps, CPU time
  bounded by the run's own wall-clock timeout, and a process cap a fork bomb reaches. A limit
  the kernel refuses is skipped rather than fatal, so two of these are Linux-only in practice:
  macOS declines a finite address-space limit, and the process cap is counted from
  `/proc/loadavg`, which only Linux has.
- **Timeouts**, as before: 10 seconds per test, 60 seconds for the run.

## Tiers

`drillion doctor` names the one you have. Each is checked by reading the result back from a
child that actually tried it, never from what the code intended — a sandbox that fails open
while reporting success is worse than none, because it gets believed.

### `landlock` — Linux, kernel-enforced

The Landlock LSM, applied with `ctypes` and no new dependency, in the forked child before
`exec` so it can never reach the server or the language server. The ABI is queried and the
rights are rebuilt from the answer, because a right the kernel has not heard of makes the
whole ruleset fail.

- **Reads** are confined to the interpreter and its libraries, `/usr`, `/lib`, `/etc`,
  `/dev`, `tasks/`, the task being graded and the scratch directory. Your home directory,
  every other user's files, and everything else on the disk are denied. The data root is
  listable — pytest builds its collection tree from there — but the files under it, including
  `progress.json`, are not readable.
- **Writes** are confined to the scratch directory.
- **TCP** — every bind and connect is refused, on ABI 4 and above. UDP and Unix sockets are
  not covered by Landlock; on ABI 6 and above, abstract Unix sockets and signals are scoped
  to the sandbox.
- **Subprocesses are contained, not forbidden.** Task 033 grades `subprocess.run` against
  `echo` and `true`, so `/usr/bin` stays executable. A Landlock domain is inherited by every
  child, so what a task spawns is confined by the same ruleset the task is — a spawned `cat`
  cannot read your home directory either.

### `sandbox-exec` — macOS, kernel-enforced

The same shape as an SBPL profile wrapped around the pytest process: reads confined to the
interpreter, the system frameworks, `tasks/` and the scratch directory, writes confined to
the scratch directory, network denied. `sandbox-exec` is deprecated by Apple and its dialect
drifts, so the profile is run once against a do-nothing interpreter and the tier is only
claimed if that succeeded. **This tier has not been executed on a Mac** — it is written from
the documented dialect and gated behind that self-check; a Mac CI cell is what will confirm
it.

### `guard` — the in-process floor, wherever no kernel tier reaches

`src/drillion/guard.py`, a PEP 578 audit hook loaded into the graded process as
`-p drillion.guard`. It stands in on Windows, which has no unprivileged sandbox, and equally
on an old Linux kernel without Landlock or in a container that blocks `prctl`. It refuses
writes outside the scratch directory and connections to anything but loopback.

**This is not a security boundary and must not be described as one.** Task code shares the
interpreter with the hook, and `subprocess` stays open because task 033 grades it, so a
program that means harm walks around it. It is a speed bump against an accident. What
actually holds at this tier is the scrubbed environment and the redirected `HOME`.

### `floor`

Reported when even the audit hook did not load. The environment scrub, the redirected `HOME`
and the resource limits are all that is left, and `drillion doctor` says so plainly.

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/vazome/drillion/security/advisories/new).
Please do not open a public issue for something exploitable.
