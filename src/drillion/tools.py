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


_KUBECONFORM_RELEASE = (
    "https://github.com/vazome/kubeconform/releases/download/v0.8.0-drillion.3"
)

PINS: dict[str, dict[tuple[str, str], Pin]] = {
    KUBECONFORM: {
        # Upstream publishes a .tar.gz per platform, a .zip for Windows, and a CHECKSUMS
        # file covering the archives: https://github.com/yannh/kubeconform/releases.
        # `archive_sha256` is that file's line; `binary_sha256` is the member inside it,
        # which upstream does not publish and which is what `installed` rechecks on every
        # use. Both are recomputed by hand when the version moves.
        ("linux", "amd64"): Pin(
            "v0.8.0-drillion.3",
            f"{_KUBECONFORM_RELEASE}/kubeconform-linux-amd64.tar.gz",
            "ab8eef9c7846a63f01f9df30e53ed01c1aaa9afe1fec30a918bbd44ffea103ab",
            "kubeconform",
            "4b3e14698051fcebf6a04c0438fc40a044e5a0989a3e92f5ff3c52c9d40feba9",
        ),
        ("linux", "arm64"): Pin(
            "v0.8.0-drillion.3",
            f"{_KUBECONFORM_RELEASE}/kubeconform-linux-arm64.tar.gz",
            "b98a72aa072620d80370e526a8442aec128d498dd630ca9c043d9ea8b8612482",
            "kubeconform",
            "5db1ce5c7e712468ddd2f8dac883671156586a09cb71fe1cbde6b7225d0ac3ab",
        ),
        ("darwin", "amd64"): Pin(
            "v0.8.0-drillion.3",
            f"{_KUBECONFORM_RELEASE}/kubeconform-darwin-amd64.tar.gz",
            "3487e750c96b0b6b40a5700d744780653d62b31f3b26562401c5cd45f8f371b0",
            "kubeconform",
            "217d797587fa6527acb1d22caace116651b90d74d661d998ab69bf594ae2cb07",
        ),
        ("darwin", "arm64"): Pin(
            "v0.8.0-drillion.3",
            f"{_KUBECONFORM_RELEASE}/kubeconform-darwin-arm64.tar.gz",
            "12d12f56ccba69f75b0f42085ebbebaa6a25c0c2936ff39aa2fa552ba4a5dea3",
            "kubeconform",
            "19bd3a2e82bfd717e7a6a9cc54df9bdb9639e01953878d872f92fa602e1fde3e",
        ),
        ("win32", "amd64"): Pin(
            "v0.8.0-drillion.3",
            f"{_KUBECONFORM_RELEASE}/kubeconform-windows-amd64.zip",
            "f3870f91f4f60e3f0ff508b62f45f48b43f6d5511b7025a984dac58e9198969a",
            "kubeconform.exe",
            "8025d1fd64783a578961b6d7092a40a083beeb5ae9fb9510f3ee2c9d6f49704e",
        ),
    }
}


def pin_for(name):
    try:
        return PINS[name][host()]
    except KeyError:
        raise Unsupported(f"no pinned {name} for {host()[0]}/{host()[1]}") from None


def tools_dir():
    return Path(os.environ.get("DRILLION_TOOLS_DIR", settings.root / "tools"))


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
        # Git may check a text schema out as CRLF on Windows. The validator accepts either
        # spelling, so the verdict identity must not depend on the checkout platform.
        content = path.read_bytes().replace(b"\r\n", b"\n")
        for field in (path.name.encode(), content):
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
