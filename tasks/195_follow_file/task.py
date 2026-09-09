def solve(path):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _reference(path):
    from contextlib import contextmanager

    @contextmanager
    def follow():
        stream = path.open(encoding="utf-8")
        stream.seek(0, 2)

        def read_new():
            return stream.read().splitlines()

        try:
            yield read_new
        finally:
            stream.close()

    return follow()


def test_solve(tmp_path):
    r = rng()
    path = tmp_path / "service.log"
    path.write_text("old line\n", encoding="utf-8")
    with solve(path) as read_new:
        first = [f"event {r.randint(1, 99)}" for _ in range(2)]
        with path.open("a", encoding="utf-8") as stream:
            stream.write("\n".join(first) + "\n")
        assert read_new() == first
        with path.open("a", encoding="utf-8") as stream:
            stream.write("last event\n")
        assert read_new() == ["last event"]
    try:
        read_new()
    except ValueError:
        pass
    else:
        raise AssertionError("the context manager must close its reader on exit")

    try:
        with solve(path) as read_after_error:
            raise RuntimeError("body failed")
    except RuntimeError:
        pass
    try:
        read_after_error()
    except ValueError:
        pass
    else:
        raise AssertionError("the context manager must close its reader after an error")

    other = tmp_path / "reference.log"
    other.write_text("ignored\n", encoding="utf-8")
    with _reference(other) as read_reference:
        with other.open("a", encoding="utf-8") as stream:
            stream.write("new\n")
        assert read_reference() == ["new"]
