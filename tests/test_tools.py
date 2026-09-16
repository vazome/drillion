"""Pinned external graders: verified on every use, never trusted because they exist."""

import hashlib
import io
import tarfile

import pytest
import responses

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


def _archive(member, payload):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        info = tarfile.TarInfo(member)
        info.size = len(payload)
        info.mode = 0o755
        tar.addfile(info, io.BytesIO(payload))
    return buf.getvalue()


def _link_archive(member, payload):
    """A payload member plus a symlink named `member` that points at it, so following the
    link (rather than rejecting it outright) would successfully return real bytes."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        payload_info = tarfile.TarInfo("payload")
        payload_info.size = len(payload)
        payload_info.mode = 0o644
        tar.addfile(payload_info, io.BytesIO(payload))
        link_info = tarfile.TarInfo(member)
        link_info.type = tarfile.SYMTYPE
        link_info.linkname = "payload"
        tar.addfile(link_info)
    return buf.getvalue()


def _pin(monkeypatch, blob, binary_sha256):
    """Point the kubeconform pin at a fake endpoint serving `blob`."""
    monkeypatch.setitem(
        tools.PINS["kubeconform"],
        tools.host(),
        tools.Pin(
            "0.8.0",
            "https://example.invalid/k.tar.gz",
            hashlib.sha256(blob).hexdigest(),
            "kubeconform",
            binary_sha256,
        ),
    )
    responses.add(responses.GET, "https://example.invalid/k.tar.gz", body=blob)


@responses.activate
def test_acquire_verifies_the_archive_then_the_binary(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "root", tmp_path)
    payload = b"pretend kubeconform"
    blob = _archive("kubeconform", payload)
    _pin(monkeypatch, blob, hashlib.sha256(payload).hexdigest())
    path = tools.acquire("kubeconform")
    assert path.read_bytes() == payload and tools.installed("kubeconform") == path


@responses.activate
def test_a_tampered_archive_is_rejected_and_the_old_tool_survives(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "root", tmp_path)
    good = tmp_path / "tools" / "kubeconform"
    good.parent.mkdir(parents=True)
    good.write_bytes(b"the one that already worked")
    responses.add(
        responses.GET, "https://example.invalid/k.tar.gz", body=b"wrong bytes"
    )
    monkeypatch.setitem(
        tools.PINS["kubeconform"],
        tools.host(),
        tools.Pin(
            "0.8.0",
            "https://example.invalid/k.tar.gz",
            "00" * 32,
            "kubeconform",
            "11" * 32,
        ),
    )
    with pytest.raises(tools.Rejected):
        tools.acquire("kubeconform")
    assert good.read_bytes() == b"the one that already worked"


@responses.activate
def test_an_archive_member_that_escapes_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "root", tmp_path)
    blob = _archive("../../escape", b"nope")
    _pin(monkeypatch, blob, "11" * 32)
    with pytest.raises(tools.Rejected):
        tools.acquire("kubeconform")
    assert not (tmp_path / "escape").exists()


@responses.activate
def test_a_member_that_is_not_a_regular_file_is_rejected(tmp_path, monkeypatch):
    """A symlink where the executable belongs is a rejection, never something to follow,
    even when the link points at a real member of the same archive."""
    monkeypatch.setattr(settings, "root", tmp_path)
    payload = b"a payload living elsewhere in the archive"
    blob = _link_archive("kubeconform", payload)
    _pin(monkeypatch, blob, hashlib.sha256(payload).hexdigest())
    with pytest.raises(tools.Rejected):
        tools.acquire("kubeconform")
    assert not (tmp_path / "tools" / "kubeconform").exists()


@responses.activate
def test_a_download_larger_than_the_bound_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "root", tmp_path)
    monkeypatch.setattr(tools, "MAX_ARCHIVE", 16)
    blob = _archive("kubeconform", b"x" * 4096)
    _pin(monkeypatch, blob, "11" * 32)
    with pytest.raises(tools.Rejected):
        tools.acquire("kubeconform")
    assert not (tmp_path / "tools" / "kubeconform").exists()


@responses.activate
def test_a_download_that_fails_leaves_nothing_behind(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "root", tmp_path)
    responses.add(responses.GET, "https://example.invalid/k.tar.gz", status=404)
    monkeypatch.setitem(
        tools.PINS["kubeconform"],
        tools.host(),
        tools.Pin(
            "0.8.0",
            "https://example.invalid/k.tar.gz",
            "00" * 32,
            "kubeconform",
            "11" * 32,
        ),
    )
    with pytest.raises(tools.Rejected):
        tools.acquire("kubeconform")
    assert list((tmp_path / "tools").iterdir()) == []


def test_report_names_the_command_that_fixes_a_missing_tool(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "root", tmp_path)
    monkeypatch.setitem(
        tools.PINS["kubeconform"],
        tools.host(),
        tools.Pin(
            "0.8.0",
            "https://example.invalid/k.tar.gz",
            "00" * 32,
            "kubeconform",
            "11" * 32,
        ),
    )
    assert tools.report() == [
        ("kubeconform", "missing or altered: run `drillion doctor --fetch`")
    ]
