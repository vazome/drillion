def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect
import typing

from _lib import rng


def _reference():
    def index_rows(headers: list[str], rows: list[list[str]]) -> list[tuple[int, dict[str, str]]]:
        return [(number, dict(zip(headers, row)))
                for number, row in enumerate(rows, start=1)]

    return index_rows


def test_solve():
    index_rows = solve()
    assert callable(index_rows) and not inspect.isclass(index_rows)
    assert typing.get_type_hints(index_rows) == {
        "headers": list[str],
        "rows": list[list[str]],
        "return": list[tuple[int, dict[str, str]]],
    }
    assert index_rows(["host", "zone"], [["api", "eu"], ["db", "us"]]) == [
        (1, {"host": "api", "zone": "eu"}),
        (2, {"host": "db", "zone": "us"}),
    ]
    r = rng()
    for _ in range(5):
        headers = r.sample(["host", "zone", "team", "image", "status"], r.randint(2, 5))
        rows = [[f"value-{r.randint(1, 99)}" for _ in headers] for _ in range(r.randint(0, 5))]
        assert index_rows(list(headers), [list(row) for row in rows]) == _reference()(headers, rows)
