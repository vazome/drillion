"""Pinned external graders: verified on every use, never trusted because they exist."""

import hashlib

import pytest

from drillion import tools
from drillion.settings import settings


def test_a_binary_that_does_not_match_its_pin_is_not_installed(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "root", tmp_path)
    binary = tmp_path / "tools" / "kubeconform"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"not kubeconform")
    assert tools.installed("kubeconform") is None


def test_a_matching_binary_is_installed(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "root", tmp_path)
    binary = tmp_path / "tools" / "kubeconform"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"pretend")
    pin = tools.pin_for("kubeconform")
    monkeypatch.setitem(
        tools.PINS["kubeconform"],
        tools.host(),
        pin._replace(binary_sha256=hashlib.sha256(b"pretend").hexdigest()),
    )
    assert tools.installed("kubeconform") == binary


def test_an_unsupported_platform_says_so(monkeypatch):
    monkeypatch.setattr(tools, "host", lambda: ("plan9", "vax"))
    with pytest.raises(tools.Unsupported):
        tools.pin_for("kubeconform")


@pytest.mark.xfail(reason="pins are filled at the phase 2 release gate", strict=True)
def test_every_pin_is_filled_in():
    """A placeholder pin is a release blocker, not a TODO."""
    for name, by_host in tools.PINS.items():
        for host, pin in by_host.items():
            assert pin.version and pin.url.startswith("https://"), (name, host)
            assert len(pin.archive_sha256) == 64 and len(pin.binary_sha256) == 64, (
                name,
                host,
            )
