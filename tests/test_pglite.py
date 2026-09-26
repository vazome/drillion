"""PGlite is pinned like the other graders, but as a directory: the tarball on download,
the unpacked tree and its snapshot on every use."""

import io
import shutil
import tarfile

import pytest

from drillion import pglite, tools


def _tar(path, members):
    """A gzipped tarball of {name: bytes | ("link", target)}."""
    with tarfile.open(path, "w:gz") as tf:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            if isinstance(data, tuple):
                info.type, info.linkname = tarfile.SYMTYPE, data[1]
                tf.addfile(info)
            else:
                info.size = len(data)
                tf.addfile(info, io.BytesIO(data))
    return path


def test_unpack_keeps_what_runs_under_dist_and_nothing_else(tmp_path):
    archive = _tar(
        tmp_path / "p.tgz",
        {
            "package/dist/index.js": b"js",
            "package/dist/pglite.wasm": b"wasm",
            "package/dist/fs/nodefs.js": b"fs",
            "package/dist/index.js.map": b"map",
            "package/dist/index.d.ts": b"types",
            "package/dist/hstore.tar.gz": b"ext",
            "package/README.md": b"readme",
            "package/dist/../../escape.js": b"no",
            "package/dist/link.js": ("link", "/etc/passwd"),
        },
    )
    out = pglite.unpack(archive, tmp_path / "out")
    found = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    assert found == ["fs/nodefs.js", "index.js", "pglite.wasm"]
    assert not (tmp_path / "escape.js").exists()


def test_the_tree_digest_moves_with_a_path_or_a_byte(tmp_path):
    (tmp_path / "a.js").write_bytes(b"1")
    before = pglite.tree_digest(tmp_path)
    (tmp_path / "a.js").write_bytes(b"2")
    assert pglite.tree_digest(tmp_path) != before
    (tmp_path / "a.js").write_bytes(b"1")
    (tmp_path / "a.js").rename(tmp_path / "b.js")
    assert pglite.tree_digest(tmp_path) != before


def test_the_snapshot_is_not_part_of_the_tree(tmp_path):
    (tmp_path / "a.js").write_bytes(b"1")
    before = pglite.tree_digest(tmp_path)
    (tmp_path / pglite.SNAPSHOT).write_bytes(b"x")
    (tmp_path / (pglite.SNAPSHOT + ".sha256")).write_text("y")
    assert pglite.tree_digest(tmp_path) == before


def test_a_tarball_off_its_pin_installs_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("DRILLION_TOOLS_DIR", str(tmp_path))
    monkeypatch.setattr(
        tools, "_download", lambda url, into: (into.write_bytes(b"x"), into)[1]
    )
    with pytest.raises(tools.Rejected, match="checksum"):
        pglite.acquire()
    assert not pglite.home().exists()


needs_pglite = pytest.mark.skipif(
    pglite.installed() is None,
    reason="PGlite is not installed: run `drillion doctor --fetch`",
)


@needs_pglite
def test_a_changed_file_is_no_longer_installed(tmp_path, monkeypatch):
    shutil.copytree(pglite.home(), tmp_path / pglite.NAME)
    monkeypatch.setenv("DRILLION_TOOLS_DIR", str(tmp_path))
    assert pglite.installed() == tmp_path / pglite.NAME
    (tmp_path / pglite.NAME / "index.js").write_bytes(b"// altered")
    assert pglite.installed() is None
