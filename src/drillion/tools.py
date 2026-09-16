"""Pinned external graders, fetched once and verified every time.

A grader that decides whether a learner passed is part of the verdict, so its identity is
pinned by checksum rather than by version string, and checked before every run rather than
only after a download."""

import hashlib
import platform
import sys
from typing import NamedTuple

from .settings import settings

KUBECONFORM = "kubeconform"


class Unsupported(Exception):
    """No pin for this operating system and architecture."""


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
