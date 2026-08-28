"""The sandbox around graded code, checked the only way that means anything: by running a
task that tries to break out and watching it fail.

The probe is the one from issue #147, which on the unsandboxed runner reported a full read
of `$HOME`, a write into it, an arbitrary subprocess, 70 inherited environment variables and
a working socket — and was graded as a pass. Every escape here has a control run with the
sandbox removed, because a probe that is simply broken also reads as a pass."""

import ctypes
import os
import sys

import pytest

from drillion import guard, runner, sandbox
from drillion.settings import settings

KERNEL_TIERS = ("landlock", "sandbox-exec")
TIER = sandbox.status()[0]

# a file the parent wrote, so "cannot write outside" can never be satisfied by the target
# not being there in the first place
PROBE = '''
import os
import socket
import subprocess
from pathlib import Path

CANARY = Path({canary!r})


def refused(call):
    """The error a denial arrived as, or None if it did not arrive."""
    try:
        call()
    except OSError as err:
        return err
    return None


def test_solve():
{body}
'''

READ = """
    assert refused(CANARY.read_text), "read a file outside the sandbox"
    assert refused(lambda: os.listdir(CANARY.parent)), "listed a directory outside it"
"""
WRITE = """
    assert refused(lambda: CANARY.write_text("owned")), "wrote outside the sandbox"
    assert refused(lambda: (CANARY.parent / "new.txt").write_text("owned")), "created one"
"""
NETWORK = """
    err = refused(lambda: socket.create_connection(("1.1.1.1", 443), 2))
    assert isinstance(err, PermissionError), f"the socket was not refused: {err!r}"
"""
SUBPROCESS = """
    done = subprocess.run(["/bin/cat", str(CANARY)], capture_output=True, text=True)
    assert done.returncode != 0, "a subprocess read what its parent could not"
"""
ENVIRONMENT = """
    assert "AWS_SECRET_ACCESS_KEY" not in os.environ, "a credential reached task code"
    assert os.environ["HOME"] == os.getcwd(), "HOME still points at the learner's home"
    assert not Path("~/.ssh").expanduser().exists(), "~/.ssh resolved to the real one"
    assert not Path("~/.aws").expanduser().exists(), "~/.aws resolved to the real one"
"""
ESCAPED = """
    assert CANARY.read_text() == "written by the parent"
    CANARY.write_text("owned")
    done = subprocess.run(["/bin/echo", "spawned"], capture_output=True, text=True)
    assert done.stdout.strip() == "spawned"
"""


def grade(tmp_path, monkeypatch, *body):
    """Run one probe through the real grader and say whether it passed."""
    monkeypatch.setattr(settings, "root", tmp_path / "root")
    (tmp_path / "root").mkdir(exist_ok=True)
    canary = tmp_path / "outside" / "canary.txt"
    canary.parent.mkdir(exist_ok=True)
    canary.write_text("written by the parent")
    task = tmp_path / "root" / "tasks" / "999_probe" / "task.py"
    task.parent.mkdir(parents=True, exist_ok=True)
    task.write_text(PROBE.format(canary=str(canary), body="".join(body)))
    return runner.run_tests(task, seed=1)


def unconfined(args, scratch, cpu, **env):
    """`_run_pytest` as it was before the sandbox: the parent's whole environment, no
    `preexec_fn`, no profile. The control run every escape test is measured against."""
    return {
        "args": [sys.executable, "-m", "pytest", *args],
        "env": {**os.environ, **{k: str(v) for k, v in env.items()}},
        "cwd": str(scratch),
    }


def test_the_probe_escapes_when_the_sandbox_is_taken_away(tmp_path, monkeypatch):
    """The control. Without this, a probe broken in some unrelated way would read as proof
    that the sandbox works."""
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "hunter2")
    monkeypatch.setattr(sandbox, "confine", unconfined)
    passed, out = grade(tmp_path, monkeypatch, ESCAPED)
    assert passed, out


@pytest.mark.skipif(
    TIER == "floor", reason=f"no sandbox tier here: {sandbox.status()[1]}"
)
def test_a_task_cannot_write_outside_the_scratch_directory(tmp_path, monkeypatch):
    passed, out = grade(tmp_path, monkeypatch, WRITE)
    assert passed, out


@pytest.mark.skipif(
    TIER == "floor", reason=f"no sandbox tier here: {sandbox.status()[1]}"
)
def test_a_task_cannot_open_a_socket(tmp_path, monkeypatch):
    passed, out = grade(tmp_path, monkeypatch, NETWORK)
    assert passed, out


@pytest.mark.skipif(
    TIER not in KERNEL_TIERS, reason="reads are only confined by a kernel tier"
)
def test_a_task_cannot_read_outside_the_sandbox(tmp_path, monkeypatch):
    passed, out = grade(tmp_path, monkeypatch, READ)
    assert passed, out


@pytest.mark.skipif(
    TIER not in KERNEL_TIERS or sys.platform == "win32",
    reason="a kernel tier and a POSIX /bin/cat are both needed",
)
def test_a_subprocess_inherits_the_sandbox(tmp_path, monkeypatch):
    """Task 033 grades `subprocess.run`, so spawning stays legal. What must not survive is
    the escape: whatever a task starts is confined by the same ruleset it was."""
    passed, out = grade(tmp_path, monkeypatch, SUBPROCESS)
    assert passed, out


def test_a_task_sees_an_allowlisted_environment_and_an_empty_home(
    tmp_path, monkeypatch
):
    """The floor, and it holds at every tier: 70 inherited variables became an allowlist,
    and `~/.aws/credentials` now resolves into an empty temp directory."""
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "hunter2")
    passed, out = grade(tmp_path, monkeypatch, ENVIRONMENT)
    assert passed, out


def test_grading_survives_a_machine_with_no_kernel_tier(tmp_path, monkeypatch):
    """Degrading has to be invisible to a learner. Forced down to the bare floor, an
    ordinary task still grades."""
    monkeypatch.setattr(sandbox, "_landlock_works", lambda: False)
    monkeypatch.setattr(sandbox, "_sandbox_exec_works", lambda: False)
    monkeypatch.setattr(sandbox, "_guard_works", lambda: False)
    monkeypatch.setattr(sandbox, "status", lambda: ("floor", "forced by a test"))
    monkeypatch.setattr(settings, "root", tmp_path)
    task = tmp_path / "task.py"
    task.write_text("def test_solve():\n    assert 1 + 1 == 2\n")
    passed, out = runner.run_tests(task, seed=1)
    assert passed, out


def test_status_names_the_tier_and_why_a_stronger_one_is_missing():
    tier, why = sandbox.status()
    assert tier in ("landlock", "sandbox-exec", "guard", "floor")
    assert why
    if tier != "landlock" and sys.platform == "linux":
        assert "Landlock" in why


def test_the_audit_hook_actually_refuses_a_write(tmp_path):
    """The in-process floor, read back from a child rather than assumed — the same check
    `status()` makes before it will name the tier."""
    assert sandbox._guard_works()


def test_the_audit_hook_leaves_alone_what_it_cannot_judge():
    """A file descriptor, the null device and loopback are all outside its remit; guessing
    at them would break `subprocess` and every task that mocks an HTTP layer."""
    assert guard._outside(3) is False
    assert guard._outside(os.devnull) is False
    assert guard._outside(os.path.join(guard.SCRATCH, "inside.txt")) is False
    assert guard._outside(os.path.join(os.sep, "definitely-not-scratch")) is True
    assert guard._remote(("127.0.0.1", 8765)) is False
    assert guard._remote("/run/some.sock") is False
    assert guard._remote(("1.1.1.1", 443)) is True


def test_the_write_test_reads_both_an_open_mode_and_open_flags():
    assert guard._writing("r", None) is False
    assert guard._writing("rb+", None) is True
    assert guard._writing(None, os.O_RDONLY) is False
    assert guard._writing(None, os.O_WRONLY | os.O_CREAT) is True


@pytest.mark.skipif(sandbox.abi() == 0, reason="this kernel has no Landlock")
def test_the_ruleset_only_asks_for_rights_this_kernel_knows():
    """Landlock is ABI 1..7 and a right the kernel has never heard of makes the whole
    ruleset fail, so the masks are rebuilt from the reported version. The judge is the
    kernel itself: it accepts the attrs, or the whole tier would have failed open."""
    assert (
        sandbox._mask(1, ("truncate", "ioctl_dev", "read_file"))
        == sandbox._FS["read_file"][0]
    )
    assert sandbox._mask(5, ("ioctl_dev",)) == sandbox._FS["ioctl_dev"][0]
    for version in range(1, 8):
        expected = 8 * (1 + (version >= 4) + (version >= 6))
        assert len(sandbox._ruleset(version)) == expected

    attrs = sandbox._ruleset(sandbox.abi())
    fd = sandbox._libc().syscall(
        ctypes.c_long(sandbox._SYS_CREATE),
        attrs,
        ctypes.c_size_t(len(attrs)),
        ctypes.c_uint32(0),
    )
    assert fd >= 0, f"kernel refused the ruleset: errno {ctypes.get_errno()}"
    os.close(fd)


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX resource limits")
def test_the_resource_limits_never_raise_what_the_machine_already_allows():
    """A cap is a cap: `_limits` may lower a limit and must never hand a learner's process
    more than it had, whatever the numbers in this file say."""
    import resource

    for what, (soft, _) in sandbox._limits(60):
        before_soft, before_hard = resource.getrlimit(what)
        if before_soft != resource.RLIM_INFINITY:
            assert soft <= before_soft
        if before_hard != resource.RLIM_INFINITY:
            assert soft <= before_hard
    assert any(what == resource.RLIMIT_CPU for what, _ in sandbox._limits(60))
    assert not any(what == resource.RLIMIT_CPU for what, _ in sandbox._limits(None))
