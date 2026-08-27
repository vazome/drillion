def solve(text: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    ints = [("replicas", r.randint(1, 12)), ("port", r.randint(1024, 9999)),
            ("timeout", r.randint(5, 120))]
    bools = [("debug", r.choice(["true", "false"])),
             ("tls", r.choice(["true", "false"]))]
    strs = [("name", r.choice(["api", "worker", "gateway"])),
            ("env", r.choice(["prod", "staging"])),
            ("image", f"nginx:1.{r.randint(18, 27)}"),
            ("listen", f"0.0.0.0:{r.randint(1024, 9999)}")]
    pairs = (r.sample(ints, r.randint(1, 3)) + r.sample(bools, r.randint(1, 2))
             + r.sample(strs, r.randint(2, 4)))
    r.shuffle(pairs)
    lines = [f"# {r.choice(['deploy config', 'generated', 'do not edit'])}"]
    for k, v in pairs:
        if r.random() < 0.2:
            lines.append("")
        if r.random() < 0.15:
            lines.append(f"# {k} below")
        lines.append(f"{k}{r.choice([': ', ': ', ' : ', ':  '])}{v}")
    return "\n".join(lines)


def _reference(text):
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if value == "true":
            out[key] = True
        elif value == "false":
            out[key] = False
        elif value.isdigit():
            out[key] = int(value)
        else:
            out[key] = value
    return out


def test_solve():
    r = rng()
    for _ in range(4):
        text = _gen(r)
        assert solve(text) == _reference(text)
