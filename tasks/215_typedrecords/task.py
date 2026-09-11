def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from typing import NamedTuple, TypedDict

from _lib import rng


def _gen(r):
    return (
        r.choice(["Kew", "Heathrow", "Ben Nevis", "Scilly", "Whitby", "Lerwick"]),
        round(r.uniform(-89.0, 89.0), 2),
        round(r.uniform(-179.0, 179.0), 2),
    )


def _reference():
    class Station(NamedTuple):
        name: str
        lat: float
        lon: float
        reference: str = "WGS84"

    class Payload(TypedDict):
        station: str
        coords: list[float]

    def to_payload(station):
        return Payload(station=station.name, coords=[station.lat, station.lon])

    return Station, Payload, to_payload


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    assert len(got) == 3, "return them as (Station, Payload, to_payload)"
    station_cls, payload_cls, to_payload = got
    want_station, _, want_payload = want
    # a dataclass has named fields too, and fails here
    assert issubclass(station_cls, tuple), "Station must be a NamedTuple, so a tuple"

    for _ in range(6):
        fields = _gen(r)
        mine, theirs = station_cls(*fields), want_station(*fields)
        assert to_payload(mine) == want_payload(theirs), f"payload for {fields}"
        assert mine == theirs, f"the record itself for {fields}"
        assert mine.reference == "WGS84", f"default reference for {fields}"

    kew = station_cls("Kew", 51.48, -0.29)
    assert kew == ("Kew", 51.48, -0.29, "WGS84"), "a Station compares equal to a plain tuple"
    name, lat, lon, reference = kew
    assert (name, lat, lon, reference) == ("Kew", 51.48, -0.29, "WGS84"), "Station must unpack"
    assert station_cls._fields == ("name", "lat", "lon", "reference"), "fields, in order"

    payload = to_payload(station_cls("Lerwick", 60.15, -1.15, "ETRS89"))
    assert type(payload) is dict, "a Payload is a plain dict, not a second record class"
    assert payload == {"station": "Lerwick", "coords": [60.15, -1.15]}, "the reference stays home"
    assert type(payload["coords"]) is list, "coords is a list; JSON has no tuples"
    assert payload_cls.__required_keys__ == frozenset({"station", "coords"}), "Payload's keys"
