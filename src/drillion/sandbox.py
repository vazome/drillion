"""Confining graded code: what a task's process may touch, decided before it starts.

Everything here shapes the children `run` and `run_script` start (pytest for a python
task, a bare grading script for the other kinds), and nothing else. Landlock especially:
it is irreversible and inherited by every child, so it is applied in the forked child
from `preexec()` and never in the server process, which would sandbox the app — and the
language server with it — for the rest of its life.

Three tiers, strongest first, with `status()` saying which one is actually in force — read
back from a child that tried it, never from intent. drillion ships as a Linux image, so
Landlock is the tier that counts; the other two are what a contributor's checkout on
another OS, or a host kernel without Landlock, falls back to:

- **landlock** — the kernel decides. Reads are confined to the interpreter, the system
  libraries, `tasks/`, the pinned tools and their schemas, and the scratch directory;
  writes to the scratch directory; TCP is denied from ABI 4.
- **guard** — `drillion.guard`, a PEP 578 audit hook in the graded process. What stands in
  wherever Landlock does not reach: an old kernel, a container that blocks `prctl`, a
  checkout on macOS. A speed bump, not a boundary.
- **floor** — what is left when even that fails.

Underneath all three sits the floor itself: an allowlisted environment, a `HOME` and
`TMPDIR` pointed at the scratch directory, and POSIX resource limits.
"""

import ctypes
import os
import platform
import resource
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from functools import cache
from pathlib import Path

from .settings import settings

# ── the floor ────────────────────────────────────────────────────

# what a graded test genuinely needs. Everything else the learner's shell exported —
# AWS_*, GITHUB_TOKEN, SSH_AUTH_SOCK — stops here
_KEEP = (
    "PATH",
    "PYTHONPATH",
    "PYTHONIOENCODING",
    "PYTHONHASHSEED",
    "PYTHONUTF8",
    "LANG",
    "LC_ALL",
    "LC_CTYPE",
    "TZ",
)

# generous: boto3, moto and langchain-core all load into one graded process
ADDRESS_SPACE = 4 << 30
MAX_FILE = 64 << 20
# forks past what the machine already runs: a fork bomb reaches this, ordinary work does not
PROCESS_HEADROOM = 128


def environ(scratch, **extra):
    """The child's whole environment: an allowlist, plus a home that is an empty temp dir.

    Pointing `HOME` at the scratch directory is the single highest-value line in this file:
    `~/.aws/credentials`, `~/.ssh` and `~/.config` all resolve into somewhere empty."""
    out = {k: v for k in _KEEP if (v := os.environ.get(k)) is not None}
    out |= dict.fromkeys(
        (
            "HOME",
            "TMPDIR",
            "TEMP",
            "TMP",
            "XDG_CONFIG_HOME",
            "XDG_DATA_HOME",
            "XDG_CACHE_HOME",
        ),
        str(scratch),
    )
    # task files are UTF-8, and `_execute` decodes the pipes as UTF-8 whatever the locale
    out.setdefault("PYTHONIOENCODING", "utf-8")
    # tasks/ is read-only under Landlock, and a failed .pyc write is only noise
    out["PYTHONDONTWRITEBYTECODE"] = "1"
    out["DRILLION_SCRATCH"] = str(scratch)  # `drillion.guard` reads this
    return out | {k: str(v) for k, v in extra.items() if v is not None}


def _limits(cpu):
    """[(resource, (soft, hard))] — the POSIX floor, computed here so the child only calls
    syscalls. `cpu` tracks the caller's wall-clock timeout; without one there is no cap."""

    out = [
        (resource.RLIMIT_FSIZE, MAX_FILE),
        (resource.RLIMIT_AS, ADDRESS_SPACE),
        (resource.RLIMIT_CORE, 0),
    ]
    if cpu:
        out.append((resource.RLIMIT_CPU, int(cpu)))
    if (cap := _process_cap()) is not None:
        out.append((resource.RLIMIT_NPROC, cap))
    return [(what, _clamp(what, value)) for what, value in out]


def _clamp(what, value):
    """Never raise a limit, and never ask for more than the hard limit already allows."""

    soft, hard = resource.getrlimit(what)
    if hard != resource.RLIM_INFINITY:
        value = min(value, hard)
    if soft != resource.RLIM_INFINITY:
        value = min(value, soft)
    return (value, hard)


def _process_cap():
    """RLIMIT_NPROC counts every *thread* the user already has, not just ours, so the cap
    has to start from that count — a flat number refuses the first fork on a busy desktop.

    The last-but-one field of /proc/loadavg is `runnable/threads` system-wide, which is a
    one-line over-estimate of this user's share, and over-estimating is the safe direction.

    ponytail: Linux-only; on other POSIX platforms there is no fork-bomb cap."""
    try:
        with open("/proc/loadavg") as handle:
            return int(handle.read().split()[3].partition("/")[2]) + PROCESS_HEADROOM
    except OSError, ValueError, IndexError:
        return None


# ── Linux: Landlock ──────────────────────────────────────────────────────────────

_SYS_CREATE, _SYS_ADD, _SYS_RESTRICT = 444, 445, 446
_PR_SET_NO_NEW_PRIVS = 38
_RULE_PATH_BENEATH = 1
_NET_ALL = (1 << 0) | (1 << 1)  # bind + connect TCP, ABI 4
_SCOPE_ALL = (1 << 0) | (1 << 1)  # abstract unix sockets + signals, ABI 6

# right -> (bit, first ABI that knows it). A right the kernel has never heard of makes the
# whole ruleset fail, so every mask below is rebuilt from the ABI the kernel reports.
_FS = {
    "execute": (1 << 0, 1),
    "write_file": (1 << 1, 1),
    "read_file": (1 << 2, 1),
    "read_dir": (1 << 3, 1),
    "remove_dir": (1 << 4, 1),
    "remove_file": (1 << 5, 1),
    "make_char": (1 << 6, 1),
    "make_dir": (1 << 7, 1),
    "make_reg": (1 << 8, 1),
    "make_sock": (1 << 9, 1),
    "make_fifo": (1 << 10, 1),
    "make_block": (1 << 11, 1),
    "make_sym": (1 << 12, 1),
    "refer": (1 << 13, 2),
    "truncate": (1 << 14, 3),
    "ioctl_dev": (1 << 15, 5),
}
_READ = ("read_file", "read_dir")
# .so files are mapped executable, and `preexec_fn` runs *before* the interpreter itself is
# exec'd, so the interpreter's own tree needs this too
_EXEC = ("read_file", "read_dir", "execute")
_DEV = ("read_file", "write_file", "read_dir", "ioctl_dev")


class _PathBeneath(ctypes.Structure):
    _pack_ = 1
    # the kernel struct is packed, which is exactly what MSVC layout plus `_pack_` gives:
    # 3.14 deprecates leaving it implicit, and ctypes ignores the name before then
    _layout_ = "ms"
    _fields_ = [("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int32)]


@cache
def _libc():
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    libc.prctl.restype = ctypes.c_int
    return libc


@cache
def abi():
    """What this kernel's Landlock knows, or 0 for none. Ask, never assume: the ABI runs
    1..7 and each version added rights the ones before it reject."""
    if sys.platform != "linux":
        return 0
    try:
        version = _libc().syscall(
            ctypes.c_long(_SYS_CREATE), None, ctypes.c_size_t(0), ctypes.c_uint32(1)
        )
    except OSError, AttributeError, ValueError:
        return 0
    return max(version, 0)


def _mask(version, names):
    return sum(bit for name in names for bit, since in [_FS[name]] if since <= version)


def _ruleset(version):
    """`struct landlock_ruleset_attr`, only as long as this kernel's version defines it."""
    fields = [_mask(version, _FS)]
    if version >= 4:
        # no allow rule ever follows, so every TCP bind and connect is refused
        fields.append(_NET_ALL)
    if version >= 6:
        fields.append(_SCOPE_ALL)
    return struct.pack("=" + "Q" * len(fields), *fields)


STALE_SECONDS = 3600


def scratch_root():
    """Where a sandboxed child's scratch folders go: one hidden folder under the data root,
    so a run killed before its cleanup leaves nothing beside the learner's files. Each call
    clears leftovers older than an hour, far past the longest a grade may run."""
    home = settings.root / ".scratch"
    home.mkdir(exist_ok=True)
    cutoff = time.time() - STALE_SECONDS
    for old in home.iterdir():
        try:
            if old.stat().st_mtime < cutoff:
                shutil.rmtree(old, ignore_errors=True)
        except OSError:
            pass
    return home


def _roots(scratch, targets):
    """(path, rights) for every place the graded process may reach; everything else is
    denied, `$HOME` above all.

    An allowlist rather than a deny-list because `sys.base_prefix` routinely lives *inside*
    `$HOME` — uv keeps its interpreters under `~/.local/share` — so "deny $HOME" would deny
    the interpreter."""
    # lazily, so that `tools` stays free to import `sandbox` to confine a grader run
    from . import tools

    interpreter = (
        Path(sys.executable).resolve().parent.parent,
        sys.prefix,
        sys.base_prefix,
    )
    roots = [
        *(((scratch, tuple(_FS)),) if scratch else ()),
        ("/dev", _DEV),
        (settings.tasks_dir, _READ),
        # pytest builds its collection tree downwards from `--rootdir`, which the runner
        # pins to the data root. Listing it is all pytest needs — its config comes from the
        # `-c` file inside the scratch dir — so every file under the root stays closed,
        # `progress.sqlite3` and a checkout's `.git/config` included.
        (settings.root, ("read_dir",)),
        # the pinned graders, executable for the same reason /usr/bin is: a manifest is
        # graded by running kubeconform, and whatever it starts inherits this sandbox
        (tools.tools_dir(), _EXEC),
        (tools.SCHEMAS, _READ),
        *((t, _READ) for t in targets),
        ("/etc", _READ),
        # /usr/bin and /bin are executable on purpose: task 067 grades `subprocess.run` by
        # starting a child Python, and anything a task starts inherits this sandbox, so it is
        # contained rather than forbidden (SECURITY.md). /bin, /sbin and /lib64 are symlinks
        # into /usr on a merged-/usr system and real directories on an older one.
        *(
            (p, _EXEC)
            for p in (*interpreter, "/usr", "/lib", "/lib64", "/bin", "/sbin")
        ),
    ]
    # one rule per real path, rights unioned: a task file that happens to sit *at* the data
    # root would otherwise be readable as a directory and not as a file
    merged = {}
    for path, rights in roots:
        real = Path(path).resolve()
        if real.exists():
            merged.setdefault(os.fsencode(str(real)), set()).update(rights)
    return list(merged.items())


def _plan(scratch, targets):
    """Everything the child needs, packed in the parent: between fork and exec the only
    safe move is a syscall, not an allocation."""
    version = abi()
    return _ruleset(version), [
        (path, _PathBeneath(_mask(version, rights), 0))
        for path, rights in _roots(scratch, targets)
    ]


def _restrict(plan):
    """Apply the ruleset to this process. Irreversible, and inherited by every child."""
    libc = _libc()
    ruleset, rules = plan
    if libc.prctl(_PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0:  # or the ruleset is refused
        raise OSError(ctypes.get_errno(), "prctl(PR_SET_NO_NEW_PRIVS)")
    fd = libc.syscall(
        ctypes.c_long(_SYS_CREATE),
        ruleset,
        ctypes.c_size_t(len(ruleset)),
        ctypes.c_uint32(0),
    )
    if fd < 0:
        raise OSError(ctypes.get_errno(), "landlock_create_ruleset")
    for path, attr in rules:
        attr.parent_fd = os.open(path, os.O_PATH | os.O_CLOEXEC)
        added = libc.syscall(
            ctypes.c_long(_SYS_ADD),
            ctypes.c_int(fd),
            ctypes.c_int(_RULE_PATH_BENEATH),
            ctypes.byref(attr),
            ctypes.c_uint32(0),
        )
        os.close(attr.parent_fd)
        if added != 0:
            raise OSError(ctypes.get_errno(), f"landlock_add_rule {path!r}")
    if libc.syscall(ctypes.c_long(_SYS_RESTRICT), ctypes.c_int(fd), ctypes.c_uint32(0)):
        raise OSError(ctypes.get_errno(), "landlock_restrict_self")
    os.close(fd)


@cache
def _landlock_works():
    """Fork, sandbox the child, and check the sandbox actually bit.

    A tier that reports success while quietly doing nothing is worse than no tier at all,
    because it gets believed. `/` is never granted, so a child that can still open it is a
    child nothing happened to."""
    if abi() == 0:
        return False
    plan = _plan(None, ())
    if (pid := os.fork()) == 0:
        code = 1
        try:
            _restrict(plan)
            try:
                os.close(os.open("/", os.O_RDONLY))
            except OSError:
                code = 0
        except BaseException:  # noqa: BLE001 - nothing may escape a forked child
            code = 1
        os._exit(code)
    return os.waitpid(pid, 0)[1] == 0


# ── the in-process floor, wherever no kernel tier reaches ────────────────────────

# The parent hands the child a canary it made outside the scratch directory: "cannot write
# outside" must not be satisfiable by the file simply not being there.
_GUARD_CHECK = """
import sys
import drillion.guard
try:
    open(sys.argv[1], "a")
except PermissionError as err:
    sys.exit(0 if "drillion sandbox" in str(err) else 2)
sys.exit(1)
"""


@cache
def _guard_works():
    """Ask a child whether the audit hook actually refused a write, rather than trusting
    that importing it would have."""
    with (
        tempfile.TemporaryDirectory() as outside,
        tempfile.TemporaryDirectory() as scratch,
    ):
        canary = Path(outside, "canary.txt")
        canary.write_text("written by the parent")
        try:
            done = subprocess.run(
                [sys.executable, "-c", _GUARD_CHECK, str(canary)],
                cwd=scratch,
                env=environ(scratch),
                capture_output=True,
                timeout=60,
                check=False,
            )
        except OSError:
            return False
    return done.returncode == 0


# ── what is actually in force ────────────────────────────────────────────────────


def _no_kernel_tier():
    """Why the kernel is not doing this, in one clause — the half of `status()` that keeps
    a weaker tier from reading as a choice."""
    if sys.platform != "linux":
        return f"drillion runs on Linux, in its image; {sys.platform} has no Landlock"
    return (
        "this kernel has no Landlock"
        if abi() == 0
        else f"Landlock ABI {abi()} is reported but the ruleset did not take effect "
        "(seccomp or a container policy blocking prctl, most likely)"
    )


@cache
def status():
    """(tier, what that means here) — for `drillion doctor`, and for anyone deciding
    whether to believe the sandbox.

    Every branch is read back from a child that actually tried it, never from intent: a
    sandbox that fails open while reporting success is worse than none, because it gets
    believed."""
    if _landlock_works():
        return "landlock", (
            f"kernel Landlock ABI {abi()}: reads confined to the interpreter, system "
            f"libraries, tasks/, tools/, the packaged schemas and a scratch HOME; "
            f"writes to scratch only; "
            f"{'TCP denied' if abi() >= 4 else 'no network control below ABI 4'}"
        )
    if _guard_works():
        return "guard", (
            f"{_no_kernel_tier()} — falling back to a PEP 578 audit hook in the graded "
            "process: it refuses writes outside the scratch directory and non-loopback "
            "connections, on top of the scrubbed environment, the redirected HOME and the "
            "resource limits. A speed bump, not a boundary: task code shares the "
            "interpreter and can spawn subprocesses"
        )
    return "floor", (
        f"{_no_kernel_tier()}, and the audit hook did not load either — the scrubbed "
        "environment, the redirected HOME and the resource limits are all that is left"
    )


def preexec(scratch, targets, cpu):
    """The callable `subprocess` runs in the child between fork and exec.

    This is the only place Landlock may ever be applied. Applying it in the parent would
    sandbox the server, the language server and every future request, irreversibly."""

    limits = _limits(cpu)
    plan = _plan(scratch, targets) if _landlock_works() else None

    def child():
        for what, soft_hard in limits:
            try:
                resource.setrlimit(what, soft_hard)
            except OSError, ValueError:
                # Darwin refuses a finite RLIMIT_AS. One limit the kernel will not take is
                # a weaker floor, not a reason to refuse to grade at all
                pass
        if plan:
            _restrict(plan)

    return child


def grading_python():
    """The interpreter every graded run uses: `run` builds its command from sys.executable,
    so the version that answers here is the version that decides a verdict."""
    return platform.python_version()


def run(args, scratch, cpu, **env):
    """Grade pytest `args` under the strongest tier this machine has, and hand back what
    `subprocess.run` would have."""
    child = ["-m", "pytest", *args]
    if status()[0] == "guard":
        # `-p` plugins load before pytest imports any task module, and `_PYTEST` already
        # passes `-p no:cacheprovider`, so this needs no new mechanism
        child += ["-p", "drillion.guard"]
    return _execute(child, scratch, cpu, **env)


def run_script(args, scratch, cpu, **env):
    """A bare interpreter under the same tier as a graded run. The script installs the
    guard itself, since there is no pytest here to load it as a plugin."""
    return _execute(args, scratch, cpu, **env)


def _execute(child, scratch, cpu, **env):
    """The one place a confined child starts."""
    plan = confine(child, scratch, cpu, **env)
    return subprocess.run(
        **plan,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        timeout=cpu,
    )


def confine(child, scratch, cpu, **env):
    """What `subprocess.run` needs to run `python *child` under the strongest tier this
    machine has. `cpu` is the caller's wall-clock timeout, reused as the CPU limit."""
    scratch = Path(scratch)
    targets = sorted(
        {
            str(Path(a).resolve().parent)
            for a in child
            if a.endswith(".py") and Path(a).is_file()
        }
    )
    return {
        "args": [sys.executable, *child],
        "env": environ(scratch, **env),
        "cwd": str(scratch),
        "preexec_fn": preexec(scratch, targets, cpu),
    }
