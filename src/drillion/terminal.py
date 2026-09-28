"""The learner's shell for a git task: bash on a PTY, confined like a grade, piped to one
page over a WebSocket. Page to server is JSON text, `{"i": keys}` or `{"r": [cols, rows]}`;
server to page is the PTY's bytes, as binary frames."""

import asyncio
import collections
import contextlib
import ctypes
import fcntl
import json
import os
import signal
import struct
import subprocess
import tempfile
import termios
import threading

from . import gitrepo, manifest, sandbox

MAX_SHELLS = 4
# per process: bounds a runaway command without timing out a shell someone is thinking in
CPU_SECONDS = 600
# 4002: bash itself exited; the page offers to reconnect
MOVED, RESET, EXITED = 4000, 4001, 4002
RC = r"""
[ -r /usr/share/bash-completion/completions/git ] && . /usr/share/bash-completion/completions/git
[ -r /usr/lib/git-core/git-sh-prompt ] && . /usr/lib/git-core/git-sh-prompt
shopt -s histappend
HISTSIZE=-1
HISTFILESIZE=-1
HISTCONTROL=
PROMPT_COMMAND='history -a'
PS1='\W$(type __git_ps1 >/dev/null 2>&1 && __git_ps1 " (%s)")\$ '
command -v vim >/dev/null || alias vim=vi
export EDITOR=nano VISUAL=nano
trap 'kill -HUP $(jobs -p) 2>/dev/null' EXIT
"""
_live = {}
# slug -> sockets starting or running a shell on it; its length is the shells in use
_claims = collections.Counter()
# slug -> [holders and waiters, lock]; dropped when unused, since a lock binds to one loop
_locks = {}
# set while a restore or an erase runs; see `quiet`
_quiet = None
# sockets between the gate and a registered shell (or a refusal)
_starting = 0
# `_release` tasks, held so none is collected while shielded
_releasing = set()


class _Shell:
    def __init__(self, proc, fd, ws):
        self.proc, self.fd, self.ws = proc, fd, ws
        self.done = False
        self.ended = asyncio.Event()

    async def end(self, code=1000):
        """SIGHUP the shell's process group, SIGKILL it two seconds later, close the socket.
        A second call waits for the first to finish."""
        if self.done:
            await self.ended.wait()
            return
        self.done = True
        try:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(self.proc.pid, signal.SIGHUP)
            try:
                await asyncio.wait_for(asyncio.to_thread(self.proc.wait), 2)
            except TimeoutError:
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(self.proc.pid, signal.SIGKILL)
                await asyncio.to_thread(self.proc.wait)
            # bash hands SIGHUP on to every job before it exits.
            # ponytail: a job started with nohup or setsid outlives the shell; a cgroup per
            # shell if that ever matters
            with contextlib.suppress(Exception):
                await self.ws.close(code)
        finally:
            self.ended.set()


@contextlib.asynccontextmanager
async def turn(slug):
    """Hold `slug`'s lock: one shell starts, is replaced or is reset at a time per task."""
    entry = _locks.setdefault(slug, [0, asyncio.Lock()])
    entry[0] += 1
    try:
        async with entry[1]:
            yield
    finally:
        entry[0] -= 1
        if not entry[0]:
            del _locks[slug]


_rc_lock = threading.Lock()


def _rc(folder):
    """`RC` as a file in `folder`, beside every sitting and inside none, so the shell can
    read it and never write it. Replaced only when it differs: a shell starting on another
    task holds a Landlock grant on the file that is there now."""
    rc = folder / ".drillionrc"
    # two tasks' shells start on worker threads at once; the second must find the first's file
    with _rc_lock:
        try:
            if rc.read_text(encoding="utf-8") == RC:
                return rc
        except OSError:
            pass
        fd, tmp = tempfile.mkstemp(dir=folder, prefix=".drillionrc.")
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            out.write(RC)
        os.replace(tmp, rc)
        return rc


def _spawn(meta, sitting):
    """bash on a fresh PTY in the sitting's repository, under the sandbox."""
    if not (sitting / "repo").is_dir():
        raise manifest.Rejected(
            "there is no repository here any more: Reset repository builds it again"
        )
    home = sitting / "home"
    rc = _rc(sitting.parent)
    master, slave = os.openpty()
    env = sandbox.environ(
        sitting,
        HOME=home,
        TERM="xterm-256color",
        LANG="C.UTF-8",
        HISTFILE=meta["path"],
        **gitrepo.environ(sitting),
    )
    try:
        proc = subprocess.Popen(
            ["bash", "--noprofile", "--rcfile", str(rc), "-i"],
            stdin=slave,
            stdout=slave,
            stderr=slave,
            cwd=sitting / "repo",
            env=env,
            start_new_session=True,
            # the child only makes syscalls, all planned in the parent: see `sandbox.preexec`
            preexec_fn=sandbox.preexec(  # noqa: PLW1509
                sitting, [rc], CPU_SECONDS, writes=[meta["path"]], tty=True
            ),
        )
    except BaseException:
        os.close(master)
        raise
    finally:
        os.close(slave)
    os.set_blocking(master, False)
    return proc, master


async def _write(fd, data):
    view = memoryview(data)
    while view:
        try:
            view = view[os.write(fd, view) :]
        except BlockingIOError:
            await asyncio.sleep(0.01)


async def _out(shell):
    """PTY to page, until the shell has gone."""
    loop = asyncio.get_running_loop()
    ready = asyncio.Event()
    loop.add_reader(shell.fd, ready.set)
    try:
        while True:
            await ready.wait()
            ready.clear()
            try:
                data = os.read(shell.fd, 65536)
            except BlockingIOError:
                continue
            except OSError:  # EIO: every holder of the other end has closed it
                return
            if not data:
                return
            await shell.ws.send_bytes(data)
    finally:
        loop.remove_reader(shell.fd)


_SYS_PIDFD_OPEN = 434  # the same number on every Linux architecture


def _pidfd(pid):
    """`os.pidfd_open`, which uv's standalone Pythons are built without."""
    if hasattr(os, "pidfd_open"):
        return os.pidfd_open(pid)
    fd = sandbox._libc().syscall(
        ctypes.c_long(_SYS_PIDFD_OPEN), ctypes.c_int(pid), ctypes.c_uint(0)
    )
    if fd < 0:
        raise OSError(ctypes.get_errno(), "pidfd_open")
    return fd


async def _exited(proc):
    """Until bash exits, whatever jobs still hold its PTY."""
    loop = asyncio.get_running_loop()
    try:
        fd = _pidfd(proc.pid)
    except OSError, AttributeError:
        # macOS, or a kernel older than 5.3: a worker thread waits instead
        await asyncio.to_thread(proc.wait)
        return
    gone = asyncio.Event()
    loop.add_reader(fd, gone.set)
    try:
        await gone.wait()
    finally:
        loop.remove_reader(fd)
        os.close(fd)


async def _in(shell):
    """Page to PTY: keys, and the window's size."""
    while True:
        message = json.loads(await shell.ws.receive_text())
        if "i" in message:
            await _write(shell.fd, str(message["i"]).encode())
        elif "r" in message:
            cols, rows = (max(1, min(int(v), 1000)) for v in message["r"])
            fcntl.ioctl(
                shell.fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0)
            )


async def end(slug, code=RESET):
    """End the shell open on `slug`, if there is one."""
    shell = _live.pop(slug, None)
    if shell:
        await shell.end(code)


async def close(slug, code=1000):
    """End `slug`'s shell once its attempt has closed, after any shell still starting on it
    has registered, so a tab mid-setup cannot outlive the attempt."""
    async with turn(slug):
        await end(slug, code)


async def end_all(code=RESET):
    """End every open shell."""
    await asyncio.gather(*(end(slug, code) for slug in list(_live)))


async def shutdown():
    """End every shell and wait out the releases still running, which the loop would
    otherwise drop with their bash unreaped. Run as the server stops."""
    await end_all()
    while _releasing:
        await asyncio.gather(*_releasing, return_exceptions=True)


async def _unquiet():
    while _quiet is not None:
        await _quiet.wait()


@contextlib.asynccontextmanager
async def admitted():
    """Wait out a restore or an erase, and hold the next one off until this is done."""
    global _starting
    await _unquiet()
    _starting += 1
    try:
        yield
    finally:
        _starting -= 1


@contextlib.asynccontextmanager
async def quiet():
    """Held across a restore or an erase: shells in setup finish, every shell ends, and a
    new socket waits until it is released, so it reads the state that came after."""
    global _quiet
    await _unquiet()
    _quiet = asyncio.Event()
    try:
        while _starting:
            await asyncio.sleep(0.05)
        await end_all()
        yield
    finally:
        _quiet.set()
        _quiet = None


async def bridge(ws, slug, find):
    """One page's terminal on one sitting, until either end goes. `find()` gives (meta,
    the open attempt), or None when there is no git sitting to open. A second socket for
    the same task ends the first: the newer tab wins."""
    global _starting
    await _unquiet()
    _starting += 1
    starting, claimed, shell, pumps, code = True, False, None, [], 1000
    try:
        found = await asyncio.to_thread(find)
        if found is None:
            await ws.close(code=1008)
            return
        meta, o = found
        # claimed before the next await, so shells still starting count against the limit
        if slug not in _claims and len(_claims) >= MAX_SHELLS:
            await ws.close(code=1013)
            return
        _claims[slug] += 1
        claimed = True
        async with turn(slug):
            await end(slug, MOVED)
            try:
                # ponytail: a bridge cancelled while this runs (a shutdown) loses its bash;
                # spawn under shield if shutdowns ever leave shells behind
                sitting, replaced = await asyncio.to_thread(gitrepo.ensure, meta, o)
                if replaced:
                    await ws.send_bytes(f"drillion: {gitrepo.REBUILT}\r\n".encode())
                proc, fd = await asyncio.to_thread(_spawn, meta, sitting)
            except manifest.Rejected as err:
                await ws.send_bytes(f"drillion: {err}\r\n".encode())
                await ws.close(code=1011)
                return
            shell = _live[slug] = _Shell(proc, fd, ws)
            starting = False
            _starting -= 1
        await ws.send_bytes(
            f"drillion: this shell is confined by {sandbox.status()[0]}\r\n".encode()
        )
        pumps = [
            asyncio.create_task(_out(shell)),
            asyncio.create_task(_in(shell)),
            # a job holding the PTY keeps `_out` reading after bash exits
            asyncio.create_task(_exited(proc)),
        ]
        await asyncio.wait(pumps, return_when=asyncio.FIRST_COMPLETED)
        if proc.poll() is not None:
            code = EXITED
    finally:
        if starting:
            _starting -= 1
        # shielded whole: a cancelled bridge, a server shutting down, still ends its shell
        release = asyncio.ensure_future(_release(slug, shell, pumps, claimed, code))
        _releasing.add(release)
        release.add_done_callback(_releasing.discard)
        await asyncio.shield(release)


async def _release(slug, shell, pumps, claimed, code):
    """Stop the pumps, end the shell, close its PTY, give the claim back."""
    try:
        for task in pumps:
            task.cancel()
        await asyncio.gather(*pumps, return_exceptions=True)
        if shell:
            if _live.get(slug) is shell:
                del _live[slug]
            await shell.end(code)
            os.close(shell.fd)
    finally:
        if claimed:
            _claims[slug] -= 1
            if not _claims[slug]:
                del _claims[slug]
