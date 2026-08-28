"""The Windows tier: a restricted token at Low integrity, inside a job object.

Windows has no unprivileged equivalent of Landlock, and AppContainer — the only tier that
would also block reads — needs every path the interpreter reads to be ACLed for the package
SID, re-checked on every `pip install -U`. Neither browser uses it for hostile content
either. So this is write protection, not read protection, and `SECURITY.md` says so.

What holds: a task cannot modify anything outside the scratch directory, cannot exhaust
memory, and leaves nothing running. What does not: it can read whatever the account can
read, and it can reach the network.

`subprocess.run` is not usable here — a restricted token needs `CreateProcessAsUser` — so
the wait, the timeout and the decoding are ours. Output goes to files in the scratch
directory rather than pipes: at Low integrity the child can write there and nowhere else,
which is the same fact the sandbox rests on, and it avoids a reader thread per stream.
"""

import ctypes
import subprocess
import sys
import tempfile
from ctypes import wintypes
from functools import cache
from pathlib import Path

from .sandbox import environ

if sys.platform == "win32":
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    adv = ctypes.WinDLL("advapi32", use_last_error=True)

TOKEN_ASSIGN_PRIMARY, TOKEN_DUPLICATE = 0x0001, 0x0002
TOKEN_QUERY, TOKEN_ADJUST_DEFAULT = 0x0008, 0x0080
DISABLE_MAX_PRIVILEGE = 0x1
TOKEN_INTEGRITY_LEVEL = 25
SE_GROUP_INTEGRITY = 0x00000020
# SECURITY_MANDATORY_LOW_RID is 0x1000. Microsoft's own archived sample writes 1024, which
# is a different level entirely; the tier probe below is what catches a mistake here.
LOW_INTEGRITY = "S-1-16-4096"

CREATE_SUSPENDED, CREATE_UNICODE_ENVIRONMENT = 0x00000004, 0x00000400
CREATE_NO_WINDOW = 0x08000000
STARTF_USESTDHANDLES = 0x00000100
HANDLE_FLAG_INHERIT = 0x00000001
WAIT_OBJECT_0 = 0

JOB_EXTENDED_LIMIT_INFORMATION = 9
# deliberately no JOB_OBJECT_LIMIT_ACTIVE_PROCESS: task 033 grades `subprocess.run`, and
# the Linux and macOS tiers keep spawning legal for that reason. A cap of one would also
# break a uv virtualenv, whose python.exe is a trampoline that starts the real interpreter.
JOB_LIMIT_PROCESS_MEMORY = 0x00000100
JOB_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000


def _signatures():
    """ctypes assumes `c_int` for an unannotated argument, and `GetCurrentProcess` returns
    `(HANDLE)-1` — which raises `OverflowError` rather than doing anything visible."""
    handle, dword, boolean = wintypes.HANDLE, wintypes.DWORD, wintypes.BOOL
    phandle, void = ctypes.POINTER(handle), ctypes.c_void_p
    k32.GetCurrentProcess.restype, k32.GetCurrentProcess.argtypes = handle, []
    k32.CreateJobObjectW.restype = handle
    k32.CreateJobObjectW.argtypes = [void, wintypes.LPCWSTR]
    k32.SetInformationJobObject.argtypes = [handle, ctypes.c_int, void, dword]
    k32.AssignProcessToJobObject.argtypes = [handle, handle]
    k32.SetHandleInformation.argtypes = [handle, dword, dword]
    k32.ResumeThread.restype, k32.ResumeThread.argtypes = dword, [handle]
    k32.WaitForSingleObject.restype = dword
    k32.WaitForSingleObject.argtypes = [handle, dword]
    k32.GetExitCodeProcess.argtypes = [handle, ctypes.POINTER(dword)]
    k32.TerminateProcess.argtypes = [handle, ctypes.c_uint]
    k32.CloseHandle.argtypes = [handle]
    adv.OpenProcessToken.argtypes = [handle, dword, phandle]
    adv.CreateRestrictedToken.argtypes = [
        handle,
        dword,
        dword,
        void,
        dword,
        void,
        dword,
        void,
        phandle,
    ]
    adv.ConvertStringSidToSidW.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(void)]
    adv.SetTokenInformation.argtypes = [handle, ctypes.c_int, void, dword]
    adv.GetLengthSid.restype, adv.GetLengthSid.argtypes = dword, [void]
    adv.CreateProcessAsUserW.argtypes = [
        handle,
        wintypes.LPCWSTR,
        wintypes.LPWSTR,
        void,
        void,
        boolean,
        dword,
        void,
        wintypes.LPCWSTR,
        void,
        void,
    ]


class _SidAndAttributes(ctypes.Structure):
    _fields_ = [("Sid", ctypes.c_void_p), ("Attributes", wintypes.DWORD)]


class _TokenMandatoryLabel(ctypes.Structure):
    _fields_ = [("Label", _SidAndAttributes)]


class _StartupInfo(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.c_void_p),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]


class _ProcessInformation(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]


class _IoCounters(ctypes.Structure):
    _fields_ = [
        (name, ctypes.c_ulonglong)
        for name in (
            "ReadOperationCount",
            "WriteOperationCount",
            "OtherOperationCount",
            "ReadTransferCount",
            "WriteTransferCount",
            "OtherTransferCount",
        )
    ]


class _BasicLimits(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.POINTER(wintypes.ULONG)),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BasicLimits),
        ("IoInfo", _IoCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


def _check(ok, what):
    """Fail closed. A tier that cannot be established must raise, never quietly hand the
    work to an unsandboxed `subprocess.run`."""
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error(), f"{what} failed")
    return ok


def _low_token():
    """Our own token, every privilege dropped, relabelled Low."""
    mine = wintypes.HANDLE()
    _check(
        adv.OpenProcessToken(
            k32.GetCurrentProcess(),
            TOKEN_DUPLICATE | TOKEN_ADJUST_DEFAULT | TOKEN_QUERY | TOKEN_ASSIGN_PRIMARY,
            ctypes.byref(mine),
        ),
        "OpenProcessToken",
    )
    token = wintypes.HANDLE()
    _check(
        adv.CreateRestrictedToken(
            mine, DISABLE_MAX_PRIVILEGE, 0, None, 0, None, 0, None, ctypes.byref(token)
        ),
        "CreateRestrictedToken",
    )
    sid = ctypes.c_void_p()
    _check(
        adv.ConvertStringSidToSidW(LOW_INTEGRITY, ctypes.byref(sid)),
        "ConvertStringSidToSid",
    )
    label = _TokenMandatoryLabel()
    label.Label.Sid = sid
    label.Label.Attributes = SE_GROUP_INTEGRITY
    _check(
        adv.SetTokenInformation(
            token,
            TOKEN_INTEGRITY_LEVEL,
            ctypes.byref(label),
            ctypes.sizeof(label) + adv.GetLengthSid(sid),
        ),
        "SetTokenInformation",
    )
    k32.CloseHandle(mine)
    return token


def _job(memory_bytes):
    """Caps memory and kills whatever is still running when the last handle closes, so a
    task that leaves a process behind does not outlive the run."""
    job = _check(k32.CreateJobObjectW(None, None), "CreateJobObject")
    limits = _ExtendedLimits()
    limits.BasicLimitInformation.LimitFlags = (
        JOB_LIMIT_PROCESS_MEMORY | JOB_LIMIT_KILL_ON_JOB_CLOSE
    )
    limits.ProcessMemoryLimit = memory_bytes
    _check(
        k32.SetInformationJobObject(
            job,
            JOB_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        ),
        "SetInformationJobObject",
    )
    return job


def label_low(scratch):
    """Give the scratch directory a Low label, inherited by what is created inside it.

    Without this the tier is useless in the other direction: a Low-integrity process cannot
    write into a Medium-integrity directory, so the task could not write its own output —
    and neither could pytest."""
    done = subprocess.run(
        ["icacls", str(scratch), "/setintegritylevel", "(OI)(CI)L"],
        capture_output=True,
        check=False,
    )
    _check(done.returncode == 0, f"icacls /setintegritylevel ({done.stderr!r})")


def _env_block(mapping):
    r"""The K=V\0...\0\0 buffer CREATE_UNICODE_ENVIRONMENT expects."""
    return ctypes.create_unicode_buffer(
        "".join(f"{k}={v}\0" for k, v in mapping.items()) + "\0"
    )


def _inheritable(stream):
    import msvcrt

    handle = wintypes.HANDLE(msvcrt.get_osfhandle(stream.fileno()))
    _check(
        k32.SetHandleInformation(handle, HANDLE_FLAG_INHERIT, HANDLE_FLAG_INHERIT),
        "SetHandleInformation",
    )
    return handle


def run(command, scratch, timeout=None, memory_bytes=4 << 30, **env):
    """`subprocess.run`'s shape, for a Low-integrity child. `command` is the whole argv,
    interpreter included. Raises `TimeoutExpired`."""
    _signatures()
    scratch = Path(scratch)
    label_low(scratch)

    token, job = _low_token(), _job(memory_bytes)
    out_path, err_path = scratch / "_stdout", scratch / "_stderr"
    # opened here, at our own integrity, and inherited: the child never creates them
    with open(out_path, "wb") as out, open(err_path, "wb") as err:
        info = _StartupInfo()
        info.cb = ctypes.sizeof(info)
        info.dwFlags = STARTF_USESTDHANDLES
        info.hStdOutput, info.hStdError = _inheritable(out), _inheritable(err)
        process = _ProcessInformation()
        _check(
            adv.CreateProcessAsUserW(
                token,
                None,
                ctypes.create_unicode_buffer(subprocess.list2cmdline(command)),
                None,
                None,
                True,
                CREATE_SUSPENDED | CREATE_NO_WINDOW | CREATE_UNICODE_ENVIRONMENT,
                _env_block(environ(scratch, **env)),
                str(scratch),
                ctypes.byref(info),
                ctypes.byref(process),
            ),
            "CreateProcessAsUser",
        )
        # assigned while suspended, so nothing runs outside the job even briefly
        _check(
            k32.AssignProcessToJobObject(job, process.hProcess),
            "AssignProcessToJobObject",
        )
        _check(k32.ResumeThread(process.hThread) != 0xFFFFFFFF, "ResumeThread")

        wait_ms = 0xFFFFFFFF if timeout is None else int(timeout * 1000)
        waited = k32.WaitForSingleObject(process.hProcess, wait_ms)
        code = wintypes.DWORD()
        if waited == WAIT_OBJECT_0:
            k32.GetExitCodeProcess(process.hProcess, ctypes.byref(code))
        else:
            k32.TerminateProcess(process.hProcess, 1)
        for handle in (process.hThread, process.hProcess, job, token):
            k32.CloseHandle(handle)

    if waited != WAIT_OBJECT_0:
        # unreachable without a timeout: an INFINITE wait does not return early
        raise subprocess.TimeoutExpired(command, timeout or 0.0, _text(out_path))
    return subprocess.CompletedProcess(
        command, code.value, _text(out_path), _text(err_path)
    )


def _text(path):
    """The child wrote UTF-8 because the environment told it to; never fail on a stray byte."""
    return path.read_bytes().decode("utf-8", "replace")


_READ_BACK = (
    "import ctypes;from ctypes import wintypes as w;"
    "k=ctypes.WinDLL('kernel32');a=ctypes.WinDLL('advapi32');"
    "k.GetCurrentProcess.restype=w.HANDLE;k.GetCurrentProcess.argtypes=[];"
    "a.OpenProcessToken.argtypes=[w.HANDLE,w.DWORD,ctypes.POINTER(w.HANDLE)];"
    "a.GetTokenInformation.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,"
    "w.DWORD,ctypes.POINTER(w.DWORD)];"
    "a.ConvertSidToStringSidW.argtypes=[ctypes.c_void_p,ctypes.POINTER(w.LPWSTR)];"
    "t=w.HANDLE();a.OpenProcessToken(k.GetCurrentProcess(),8,ctypes.byref(t));"
    "n=w.DWORD();a.GetTokenInformation(t,25,None,0,ctypes.byref(n));"
    "b=ctypes.create_string_buffer(n.value);"
    "a.GetTokenInformation(t,25,b,n,ctypes.byref(n));"
    "s=ctypes.cast(b,ctypes.POINTER(ctypes.c_void_p))[0];x=w.LPWSTR();"
    "a.ConvertSidToStringSidW(ctypes.c_void_p(s),ctypes.byref(x));print(x.value)"
)


@cache
def works():
    """Whether a child really came up at Low integrity — asked of the child, not assumed.

    Uses `-c` rather than the pytest path `run()` builds, because this has to answer before
    there is anything to grade."""
    if sys.platform != "win32":
        return False
    with tempfile.TemporaryDirectory() as scratch:
        try:
            done = run([sys.executable, "-c", _READ_BACK], scratch, timeout=60)
        except (OSError, subprocess.SubprocessError):
            return False
    return done.stdout.strip().endswith(LOW_INTEGRITY)
