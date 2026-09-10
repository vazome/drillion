import uuid

ASSET_NS = "https://drillion.example/asset/"


def solve(names):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_WORDS = ["hero", "banner", "thumb", "avatar", "cover", "sprite", "icon", "poster", "tile"]


def _gen(r):
    return [f"{r.choice(_WORDS)}-{r.choice(_WORDS)}-{r.randint(1, 99)}" for _ in range(6)]


def _reference(names):
    stable = {n: str(uuid.uuid5(uuid.NAMESPACE_URL, ASSET_NS + n)) for n in names}
    session = {n: str(uuid.uuid4()) for n in names}
    return stable, session


def test_solve():
    r = rng()
    names = _gen(r)

    stable, session = solve(names)
    want_stable, _ = _reference(names)
    assert stable == want_stable, f"derived ids for {names}"
    assert sorted(session) == sorted(names), "session must be keyed by the same names"

    for name in names:
        assert isinstance(stable[name], str) and isinstance(session[name], str), f"{name}: return strings"
        assert uuid.UUID(stable[name]).version == 5, f"{name}: the stable id must be a version 5 UUID"
        assert uuid.UUID(session[name]).version == 4, f"{name}: the session id must be a version 4 UUID"

    # the whole contract: one dict repeats across calls, the other never does
    again_stable, again_session = solve(names)
    assert again_stable == stable, "the derived id must be identical on a second call"
    assert len(set(session.values())) == len(names), "session ids must be distinct within one call"
    assert set(again_session.values()).isdisjoint(session.values()), (
        "session ids must be fresh on a second call"
    )

    # the URL prefix is part of the hashed name, not decoration
    solo = str(uuid.uuid5(uuid.NAMESPACE_URL, names[0]))
    assert stable[names[0]] != solo, f"{names[0]}: hash ASSET_NS + name, not the bare name"
