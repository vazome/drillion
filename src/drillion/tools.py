"""Pinned external graders, fetched once and verified every time.

A grader that decides whether a learner passed is part of the verdict, so its identity is
pinned by checksum rather than by version string, and checked before every run rather than
only after a download."""

import hashlib
import os
import platform
import stat
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import NamedTuple

import requests

from .settings import settings

KUBECONFORM = "kubeconform"
TIMEOUT = (10, 60)  # connect, read
MAX_ARCHIVE = 64 << 20


class Unsupported(Exception):
    """No pin for this operating system and architecture."""


class Rejected(Exception):
    """An acquisition that did not match its pin. Nothing was installed."""


class Pin(NamedTuple):
    version: str
    url: str
    archive_sha256: str
    member: str  # the one file inside the archive that is the executable
    binary_sha256: str


def host():
    """(platform, machine), normalised to the names the pins are keyed by."""
    machine = platform.machine().lower()
    return sys.platform, {"x86_64": "amd64", "aarch64": "arm64"}.get(machine, machine)


PINS: dict[str, dict[tuple[str, str], Pin]] = {
    KUBECONFORM: {
        # Filled in by the release gate. Upstream publishes .tar.gz per platform, a .zip
        # for Windows, and a separate CHECKSUMS file:
        # https://github.com/yannh/kubeconform/blob/v0.8.0/.goreleaser.yml
        ("linux", "amd64"): Pin("", "", "", "kubeconform", ""),
        ("linux", "arm64"): Pin("", "", "", "kubeconform", ""),
        ("darwin", "amd64"): Pin("", "", "", "kubeconform", ""),
        ("darwin", "arm64"): Pin("", "", "", "kubeconform", ""),
        ("win32", "amd64"): Pin("", "", "", "kubeconform.exe", ""),
    }
}


def pin_for(name):
    try:
        return PINS[name][host()]
    except KeyError:
        raise Unsupported(f"no pinned {name} for {host()[0]}/{host()[1]}") from None


def tools_dir():
    return settings.root / "tools"


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def installed(name):
    """The verified binary, or None. Never returns a path it has not just checked."""
    pin = pin_for(name)
    path = tools_dir() / pin.member
    if not path.is_file() or digest(path) != pin.binary_sha256:
        return None
    return path


def _download(url, into):
    """The archive, or Rejected. Bounded in both time and size, so an endpoint that hangs
    or never stops sending cannot take the app or the disk with it."""
    try:
        with requests.get(url, stream=True, timeout=TIMEOUT) as response:
            response.raise_for_status()
            size = 0
            with into.open("wb") as out:
                for block in response.iter_content(1 << 20):
                    size += len(block)
                    if size > MAX_ARCHIVE:
                        raise Rejected(f"{url} is larger than {MAX_ARCHIVE} bytes")
                    out.write(block)
    except requests.RequestException as exc:
        raise Rejected(f"{url} could not be fetched: {exc}") from exc
    return into


def _extract(archive, member, into):
    """Exactly one named regular file, read out by name rather than unpacked: a member
    called `../../escape` is never found, rather than having to be defended against. A
    directory, a symlink or a hard link where the executable belongs is a rejection."""
    if archive.name.endswith(".zip"):
        with zipfile.ZipFile(archive) as zf:
            info = zf.getinfo(member)  # KeyError if absent
            mode = info.external_attr >> 16  # unix mode, 0 when the zip carries none
            if info.is_dir() or (mode and not stat.S_ISREG(mode)):
                raise Rejected(f"{member} is not a regular file")
            data = zf.read(member)
    else:
        with tarfile.open(archive) as tf:
            info = tf.getmember(member)  # KeyError if absent
            if not info.isfile():
                raise Rejected(f"{member} is not a regular file")
            data = tf.extractfile(info).read()
    into.write_bytes(data)
    into.chmod(0o755)
    return into


def acquire(name):
    """Fetch, verify and install a pinned tool, and hand back where it landed.

    On any failure nothing is replaced: everything happens in a scratch directory inside
    the tools directory, the archive is checked before it is opened and the binary before
    it moves, and the move itself is a rename on one filesystem. A tool that already
    verified is still there, and still verifies, after a failed run."""
    pin = pin_for(name)
    if not pin.url:
        raise Rejected(f"{name} has no pin for {host()[0]}/{host()[1]} yet")
    target = tools_dir()
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target) as scratch:
        scratch = Path(scratch)
        suffix = ".zip" if pin.url.endswith(".zip") else ".tar.gz"
        archive = _download(pin.url, scratch / f"{name}{suffix}")
        if digest(archive) != pin.archive_sha256:
            raise Rejected(f"{pin.url} does not match its pinned archive checksum")
        try:
            binary = _extract(archive, pin.member, scratch / pin.member)
        except KeyError:
            raise Rejected(f"{pin.url} has no member {pin.member!r}") from None
        if digest(binary) != pin.binary_sha256:
            raise Rejected(f"{pin.member} does not match its pinned checksum")
        os.replace(binary, target / pin.member)
    return target / pin.member


def report():
    """(tool, status) for every pinned tool, for `drillion doctor`."""
    out = []
    for name in PINS:
        try:
            pin = pin_for(name)
        except Unsupported as exc:
            out.append((name, str(exc)))
            continue
        if not pin.url:
            out.append(
                (name, f"no pin for this platform yet ({pin.version or 'unset'})")
            )
        elif installed(name):
            out.append((name, f"{pin.version}, verified"))
        else:
            out.append((name, "missing or altered: run `drillion doctor --fetch`"))
    return out
