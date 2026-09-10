import configparser


def solve(text, section):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_ENVS = ["dev", "staging", "prod"]


def _gen(r):
    lines = [
        "[DEFAULT]",
        "host = localhost",
        f"port = {r.randint(5000, 5999)}",
        "url = postgres://%(host)s:%(port)s/%(database)s",
        f"database = {r.choice(['orders', 'billing', 'inventory'])}",
        f"timeout = {r.randint(5, 60)}",
        "",
    ]
    for env in _ENVS:
        lines.append(f"[{env}]")
        # each section overrides a different subset, so inheritance has to do real work
        if r.random() < 0.7:
            lines.append(f"host = db.{env}.internal")
        if r.random() < 0.5:
            lines.append(f"port = {r.randint(6000, 6999)}")
        if r.random() < 0.4:
            lines.append(f"database = {env}_scratch")
        lines.append("")
    return "\n".join(lines), r.choice(_ENVS)


def _reference(text, section):
    parser = configparser.ConfigParser()
    parser.read_string(text)
    return dict(parser[section]), parser.getint(section, "port")


def test_solve():
    r = rng()
    text, section = _gen(r)

    values, port = solve(text, section)
    want_values, want_port = _reference(text, section)

    assert type(values) is dict, "return a plain dict, not the parser's section view"
    assert values == want_values, f"[{section}] values"
    assert port == want_port and type(port) is int, f"[{section}] port must be the int {want_port}"

    assert set(values) >= {"timeout", "url", "database"}, (
        f"[{section}] must inherit the keys it never wrote itself: got {sorted(values)}"
    )
    assert "%(" not in values["url"], f"[{section}] url is not interpolated: {values['url']!r}"
    assert values["url"] == f"postgres://{values['host']}:{values['port']}/{values['database']}", (
        f"[{section}] url must interpolate this section's own host, port and database"
    )
    assert all(isinstance(v, str) for v in values.values()), "every value stays a str"

    canonical, canonical_port = solve(
        "[DEFAULT]\nhost = localhost\nport = 5432\nurl = %(host)s:%(port)s\n\n[prod]\nhost = db.prod\n",
        "prod",
    )
    assert canonical == {"host": "db.prod", "port": "5432", "url": "db.prod:5432"}, canonical
    assert canonical_port == 5432
