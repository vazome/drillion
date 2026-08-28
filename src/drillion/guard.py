"""Doors shut from inside the process, wherever no kernel can shut them from outside.

A PEP 578 audit hook, loaded by `sandbox.confine` as `-p drillion.guard` whenever neither
Landlock nor `sandbox-exec` is in force — Windows, an old Linux kernel, a container that
blocks `prctl`, all the same case. pytest loads `-p` plugins before it imports any task
module, so the hook is in place before task code runs. It refuses writes outside the scratch
directory and connections to anything but loopback.

Be clear about what this is: a speed bump against an accident, not a boundary against
someone who means it. Task code shares the interpreter, and `subprocess` stays open because
task 033 grades it, so a program that means harm walks straight around this. What actually
holds at this tier is the scrubbed environment and the redirected `HOME` in
`sandbox.environ`.
"""

import os
import sys

# the scratch directory `runner._run_pytest` made, passed down by `sandbox.environ`
SCRATCH = os.path.realpath(os.environ.get("DRILLION_SCRATCH") or os.getcwd())
LOOPBACK = ("127.0.0.1", "::1", "localhost", "")

_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC
# audit event -> which of its arguments are paths that must stay inside the scratch dir
_PATH_ARGS = {
    "os.remove": (0,),
    "os.rename": (0, 1),
    "os.mkdir": (0,),
    "os.rmdir": (0,),
    "os.truncate": (0,),
    "os.chmod": (0,),
    "os.link": (0, 1),
    # a symlink's source is only text, so the file this creates is the second argument
    "os.symlink": (1,),
}


def _writing(mode, flags):
    """Did this `open` ask for a writable handle? `io.open` says so with a mode string,
    `os.open` with O_* flags."""
    if isinstance(mode, str):
        return any(c in mode for c in "wxa+")
    return isinstance(flags, int) and bool(flags & _WRITE_FLAGS)


def _outside(path):
    """True only for a real path that is provably not under the scratch directory: an fd,
    the null device, or anything that will not resolve, is left to the operating system."""
    if not isinstance(path, (str, bytes, os.PathLike)):
        return False
    try:
        real = os.path.realpath(path)
        return real != os.path.realpath(os.devnull) and (
            os.path.commonpath([real, SCRATCH]) != SCRATCH
        )
    except (OSError, ValueError):
        return False


def _remote(address):
    """True for an address that leaves the machine. A bare non-tuple address — a Unix
    socket path — is not something this hook judges."""
    return isinstance(address, tuple) and str(address[0]) not in LOOPBACK


def _hook(event, args):
    if event == "open" and _writing(args[1], args[2]) and _outside(args[0]):
        raise PermissionError(
            f"drillion sandbox: no writing outside {SCRATCH}: {args[0]!r}"
        )
    if any(_outside(args[i]) for i in _PATH_ARGS.get(event, ())):
        raise PermissionError(f"drillion sandbox: no changing files outside {SCRATCH}")
    if event in ("socket.connect", "socket.bind") and _remote(args[1]):
        raise PermissionError(f"drillion sandbox: no network: {args[1]!r}")


# Installed only in a process the runner started, which is the only process `sandbox.environ`
# sets DRILLION_SCRATCH for. An audit hook can never be removed once added, so importing this
# module for any other reason — a unit test, a REPL — has to leave the process alone.
if os.environ.get("DRILLION_SCRATCH"):
    sys.addaudithook(_hook)
