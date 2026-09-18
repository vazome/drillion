"""Pinned external graders, fetched once and verified every time.

A grader that decides whether a learner passed is part of the verdict, so its identity is
pinned by checksum rather than by version string, and checked before every run rather than
only after a download."""

import hashlib
import json
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

from .settings import PKG, settings

KUBECONFORM = "kubeconform"
TIMEOUT = (10, 60)  # connect, read
MAX_ARCHIVE = 64 << 20

_MANIFEST = json.loads((PKG / "_schemas" / "manifest.json").read_text(encoding="utf-8"))
KUBERNETES_VERSION = _MANIFEST["kubernetes_version"]
SCHEMAS = PKG / "_schemas" / f"{KUBERNETES_VERSION}-standalone-strict"


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


_KUBECONFORM_RELEASE = "https://github.com/yannh/kubeconform/releases/download/v0.8.0"

PINS: dict[str, dict[tuple[str, str], Pin]] = {
    KUBECONFORM: {
        # Upstream publishes a .tar.gz per platform, a .zip for Windows, and a CHECKSUMS
        # file covering the archives: https://github.com/yannh/kubeconform/releases.
        # `archive_sha256` is that file's line; `binary_sha256` is the member inside it,
        # which upstream does not publish and which is what `installed` rechecks on every
        # use. Both are recomputed by hand when the version moves.
        ("linux", "amd64"): Pin(
            "v0.8.0",
            f"{_KUBECONFORM_RELEASE}/kubeconform-linux-amd64.tar.gz",
            "9bc2bffbf71f261128533edaf912153948b7ff238f9a531ae6d34466ec287883",
            "kubeconform",
            "457722b36e98d7bdbc91525e594951ef5d7ea3a29da2d13b9b28a2fb8a5097b7",
        ),
        ("linux", "arm64"): Pin(
            "v0.8.0",
            f"{_KUBECONFORM_RELEASE}/kubeconform-linux-arm64.tar.gz",
            "1f53fc8e81258197a35e8603054162a5af1de8c5af13746c71ab680d9534ed87",
            "kubeconform",
            "7e77b104b3ae696389f91971c60fd58c72f1f3dc218f139df67a1b070959c012",
        ),
        ("darwin", "amd64"): Pin(
            "v0.8.0",
            f"{_KUBECONFORM_RELEASE}/kubeconform-darwin-amd64.tar.gz",
            "71dbc87ac9f24099a62b93570e65aa06312ba6ac8aea63b7f86e9d999edf5a92",
            "kubeconform",
            "2138fc51a0b15efe827f49c1ded8eb63da049d59864ae74a9384715f9ab6f94d",
        ),
        ("darwin", "arm64"): Pin(
            "v0.8.0",
            f"{_KUBECONFORM_RELEASE}/kubeconform-darwin-arm64.tar.gz",
            "f84f4dfbebf4a6b0b230385fa065a39ea35e02608c2b50d025dcf64775a69d67",
            "kubeconform",
            "858ceb584915c256262090195eda2579299149050c5c6a9788d0985076832313",
        ),
        ("win32", "amd64"): Pin(
            "v0.8.0",
            f"{_KUBECONFORM_RELEASE}/kubeconform-windows-amd64.zip",
            "e3f56102bcf4f50b034a567e2482a1c5330799983ddd655952310211aef73d93",
            "kubeconform.exe",
            "642bf8ea0d614a8c75d2bd012eb6042a90589ff846c69f04863afa446b30f2c1",
        ),
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


def schema_digest():
    """One digest over the whole packaged set: part of a manifest verdict's identity.

    Every field is length-prefixed, so no rename or split can reproduce another set's
    digest by concatenating to the same bytes."""
    h = hashlib.sha256()
    for path in sorted(SCHEMAS.rglob("*.json")):
        for field in (path.name.encode(), path.read_bytes()):
            h.update(b"%d:" % len(field))
            h.update(field)
    return h.hexdigest()


def schema_location():
    """kubeconform's local template. No remote location is ever passed, so a schema that
    is not packaged is an error rather than a silent download."""
    return str(SCHEMAS / "{{.ResourceKind}}{{.KindSuffix}}.json")


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
