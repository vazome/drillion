"""Pinned external graders: verified on every use, never trusted because they exist."""

import hashlib
import io
import json
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
    monkeypatch.setattr(tools, "host", lambda: ("win32", "amd64"))
    pin = tools.pin_for("kubeconform")
    binary = tmp_path / "tools" / pin.member
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"pretend")
    monkeypatch.setitem(
        tools.PINS["kubeconform"],
        tools.host(),
        pin._replace(binary_sha256=hashlib.sha256(b"pretend").hexdigest()),
    )
    assert tools.installed("kubeconform") == binary


def test_an_image_can_keep_its_validator_outside_the_mounted_data_root(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "root", tmp_path / "data")
    baked = tmp_path / "app" / "tools"
    monkeypatch.setenv("DRILLION_TOOLS_DIR", str(baked))

    assert tools.tools_dir() == baked


def test_an_unsupported_platform_says_so(monkeypatch):
    monkeypatch.setattr(tools, "host", lambda: ("plan9", "vax"))
    with pytest.raises(tools.Unsupported):
        tools.pin_for("kubeconform")


def test_every_pin_is_filled_in():
    """A placeholder pin is a release blocker, not a TODO."""
    for name, by_host in tools.PINS.items():
        for host, pin in by_host.items():
            assert pin.version and pin.url.startswith("https://"), (name, host)
            assert len(pin.archive_sha256) == 64 and len(pin.binary_sha256) == 64, (
                name,
                host,
            )


def test_kubeconform_pins_use_the_patched_fork_release():
    expected = {
        ("linux", "amd64"): (
            "ab8eef9c7846a63f01f9df30e53ed01c1aaa9afe1fec30a918bbd44ffea103ab",
            "4b3e14698051fcebf6a04c0438fc40a044e5a0989a3e92f5ff3c52c9d40feba9",
        ),
        ("linux", "arm64"): (
            "b98a72aa072620d80370e526a8442aec128d498dd630ca9c043d9ea8b8612482",
            "5db1ce5c7e712468ddd2f8dac883671156586a09cb71fe1cbde6b7225d0ac3ab",
        ),
        ("darwin", "amd64"): (
            "3487e750c96b0b6b40a5700d744780653d62b31f3b26562401c5cd45f8f371b0",
            "217d797587fa6527acb1d22caace116651b90d74d661d998ab69bf594ae2cb07",
        ),
        ("darwin", "arm64"): (
            "12d12f56ccba69f75b0f42085ebbebaa6a25c0c2936ff39aa2fa552ba4a5dea3",
            "19bd3a2e82bfd717e7a6a9cc54df9bdb9639e01953878d872f92fa602e1fde3e",
        ),
        ("win32", "amd64"): (
            "f3870f91f4f60e3f0ff508b62f45f48b43f6d5511b7025a984dac58e9198969a",
            "8025d1fd64783a578961b6d7092a40a083beeb5ae9fb9510f3ee2c9d6f49704e",
        ),
    }
    for host, (archive, binary) in expected.items():
        pin = tools.PINS[tools.KUBECONFORM][host]
        assert pin.version == "v0.8.0-drillion.3"
        assert pin.url.startswith(
            "https://github.com/vazome/kubeconform/releases/download/v0.8.0-drillion.3/"
        )
        assert (pin.archive_sha256, pin.binary_sha256) == (archive, binary)


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
    # the message, or the binary checksum satisfies this and the size guard can be deleted
    with pytest.raises(tools.Rejected, match="larger than"):
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


def test_packaged_schemas_are_present_and_pinned():
    assert tools.SCHEMAS.is_dir(), (
        "schemas must ship with the package, not be downloaded"
    )
    assert tools.KUBERNETES_VERSION.count(".") == 2, "pin a concrete X.Y.Z"
    assert (tools.SCHEMAS / "deployment-apps-v1.json").is_file()
    assert len(tools.schema_digest()) == 64


def test_schema_location_is_a_local_template_with_no_remote_fallback():
    location = tools.schema_location()
    assert location.startswith(str(tools.SCHEMAS))
    assert "{{.ResourceKind}}" in location and "http" not in location


def test_schema_digest_ignores_checkout_line_endings(tmp_path, monkeypatch):
    schemas = tmp_path / "schemas"
    schemas.mkdir()
    path = schemas / "pod-v1.json"
    path.write_bytes(b'{"kind": "Pod"}\n')
    monkeypatch.setattr(tools, "SCHEMAS", schemas)
    expected = tools.schema_digest()

    path.write_bytes(b'{"kind": "Pod"}\r\n')

    assert tools.schema_digest() == expected


def test_manifest_digest_matches_the_live_computation():
    manifest = json.loads((tools.SCHEMAS.parent / "manifest.json").read_text())
    assert manifest["digest"] == tools.schema_digest()
