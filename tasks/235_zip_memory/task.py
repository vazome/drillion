import io
import zipfile


def solve(files, wanted):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_NAMES = ["report.txt", "notes.md", "hosts.csv", "summary/index.txt", "résumé.txt"]
_BODIES = ["all clear", "# résumé\nrien à signaler", "host,status\nweb1,up", "x" * 400, ""]


def _gen(r):
    names = r.sample(_NAMES, r.randint(2, 5))
    files = {name: r.choice(_BODIES) for name in names}
    return files, r.choice(names)


def _reference(files, wanted):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, text in files.items():
            archive.writestr(name, text)
    blob = buffer.getvalue()
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        return blob, archive.read(wanted).decode("utf-8")


def _check(files, wanted, got):
    blob, text = got
    assert isinstance(blob, bytes), f"the archive must be bytes, got {type(blob).__name__}"
    try:
        archive = zipfile.ZipFile(io.BytesIO(blob))
    except zipfile.BadZipFile as error:
        # closing the ZipFile is what writes the central directory
        raise AssertionError(f"{blob[:4]!r}... is not a readable archive: {error}") from None
    with archive:
        assert archive.namelist() == list(files), f"members: {archive.namelist()}"
        for name, body in files.items():
            assert archive.read(name).decode("utf-8") == body, f"content of {name!r}"
            assert archive.getinfo(name).compress_type == zipfile.ZIP_DEFLATED, f"{name!r} is stored, not deflated"
    assert text == files[wanted], f"{wanted!r} read back as {text!r}"


def test_solve():
    r = rng()
    for _ in range(5):
        files, wanted = _gen(r)
        _check(files, wanted, solve(dict(files), wanted))

    canonical = {"report.txt": "all clear", "notes.md": "# résumé"}
    _check(canonical, "notes.md", solve(dict(canonical), "notes.md"))
