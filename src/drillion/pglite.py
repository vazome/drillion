"""PGlite, the Postgres a SQL task is graded on: fetched once, verified before every run.

Postgres compiled to WASM, run by the Node that basedpyright already ships. Every other
pinned grader is one executable; this one is a directory, so its pin covers the tarball on
download and the unpacked tree on every use. `doctor --fetch` also builds the data directory
every grade starts from, since running initdb would cost each grade two seconds."""

import hashlib
import os
import subprocess
import tarfile
import tempfile
from functools import cache
from pathlib import Path, PurePosixPath

import nodejs_wheel

from . import tools

NAME = "pglite"
VERSION = "0.5.8"
URL = f"https://registry.npmjs.org/@electric-sql/pglite/-/pglite-{VERSION}.tgz"
# the registry's tarball; `TREE_SHA256` is ours, over what `unpack` keeps of it, and both are
# recomputed by hand when the version moves
TARBALL_SHA256 = "d71088d246d86e946c5d53b152a23c6b79ee65c8bc43dab69670af53b57c788d"
TREE_SHA256 = "1a1fc56f752d9d7d8df12cf72983db1e597030aaea46b278bbfeeb2e2da40777"
SNAPSHOT = "datadir.tar.gz"
# V8 compiling a module this size dies under the sandbox's 4 GB RLIMIT_AS without both: no
# 10 GB bounds-check reservation, and the baseline compiler only
NODE_FLAGS = ("--disable-wasm-trap-handler", "--liftoff-only")
RUNNER = Path(__file__).with_name("sqlrun.mjs")
# what runs; source maps, types and the extension tarballs stay in the download
KEEP = (".js", ".cjs", ".mjs", ".wasm", ".data")
SNAPSHOT_SECONDS = 120


def node():
    return Path(nodejs_wheel.__file__).parent / "bin" / "node"


def home():
    return tools.tools_dir() / NAME


def tree_digest(root):
    """Length-prefixed, as `tools.schema_digest` is, over each file's path and bytes. The
    snapshot is left out: it is built here, never downloaded, and checked on its own."""
    h = hashlib.sha256()
    skip = {SNAPSHOT, SNAPSHOT + ".sha256"}
    for path in sorted(
        p for p in root.rglob("*") if p.is_file() and p.name not in skip
    ):
        for field in (path.relative_to(root).as_posix().encode(), path.read_bytes()):
            h.update(b"%d:" % len(field))
            h.update(field)
    return h.hexdigest()


def unpack(archive, into):
    """The regular files under `package/dist/` whose suffix runs, and nothing else. Links,
    directories and any name that climbs out are never written."""
    into.mkdir(parents=True)
    with tarfile.open(archive) as tf:
        for info in tf.getmembers():
            parts = PurePosixPath(info.name).parts
            if not info.isfile() or parts[:2] != ("package", "dist") or ".." in parts:
                continue
            if not parts[-1].endswith(KEEP):
                continue
            target = into.joinpath(*parts[2:])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(tf.extractfile(info).read())
    return into


def _stamp(root):
    return tuple(
        (p.as_posix(), st.st_size, st.st_mtime_ns, st.st_ctime_ns)
        for p in sorted(root.rglob("*"))
        if p.is_file() and (st := p.stat())
    )


@cache
def _verified(root, stamp):
    """Keyed by every file's stat, so repeat grades skip hashing the whole tree."""
    root = Path(root)
    snap, sha = root / SNAPSHOT, root / (SNAPSHOT + ".sha256")
    return (
        tree_digest(root) == TREE_SHA256
        and snap.is_file()
        and sha.is_file()
        and tools.digest(snap) == sha.read_text().strip()
    )


def installed():
    """The verified directory, or None."""
    root = home()
    if not (root / "index.js").is_file():
        return None
    return root if _verified(str(root), _stamp(root)) else None


def _snapshot(tree):
    """Start PGlite once, outside any sandbox (this is drillion's own code), and keep the
    data directory it made."""
    try:
        done = subprocess.run(
            [
                str(node()),
                *NODE_FLAGS,
                str(RUNNER),
                "--snapshot",
                str(tree),
                str(tree / SNAPSHOT),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=SNAPSHOT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise tools.Rejected(f"PGlite did not start: {exc}") from None
    if done.returncode != 0 or not (tree / SNAPSHOT).is_file():
        raise tools.Rejected(f"PGlite did not start: {done.stderr.strip()[-500:]}")
    (tree / (SNAPSHOT + ".sha256")).write_text(tools.digest(tree / SNAPSHOT))


def acquire():
    """Fetch, verify, unpack and snapshot PGlite. Everything happens in a scratch directory
    inside the tools directory, and a verified install is only swapped out at the end."""
    target = tools.tools_dir()
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target) as scratch:
        scratch = Path(scratch)
        archive = tools._download(URL, scratch / "pglite.tgz")
        if tools.digest(archive) != TARBALL_SHA256:
            raise tools.Rejected(f"{URL} does not match its pinned archive checksum")
        tree = unpack(archive, scratch / NAME)
        if tree_digest(tree) != TREE_SHA256:
            raise tools.Rejected("the unpacked PGlite does not match its pinned digest")
        _snapshot(tree)
        if home().exists():
            os.replace(home(), scratch / "previous")
        os.replace(tree, home())
    return home()


def status():
    """One line for `drillion doctor`, as `tools.report` gives the others."""
    if installed():
        return f"{VERSION}, verified"
    return "missing or altered: run `drillion doctor --fetch`"
