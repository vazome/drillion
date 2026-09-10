import textwrap


def solve(sections, width):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_HEADINGS = ["Disk", "Certificates", "Backups", "Open ports", "Package drift", "Clock skew"]
_WORDS = [
    "volume", "mounted", "crossed", "ninety", "percent", "rotation", "job", "since",
    "tuesday", "which", "means", "the", "next", "large", "write", "will", "fail",
    "before", "anyone", "is", "paged", "about", "space", "itself", "and", "has", "not",
]


def _gen(r):
    sections = []
    for heading in r.sample(_HEADINGS, 3):
        words = [r.choice(_WORDS) for _ in range(r.randint(14, 30))]
        pad = " " * r.choice([4, 8])
        # rebuilt with the source indentation and line breaks a triple-quoted string would carry
        lines = [words[i : i + 5] for i in range(0, len(words), 5)]
        body = "\n" + "".join(pad + " ".join(chunk) + "\n" for chunk in lines) + pad
        sections.append((heading, body))
    return sections, r.choice([40, 52, 72])


def _reference(sections, width):
    blocks = []
    for heading, body in sections:
        filled = textwrap.fill(
            textwrap.dedent(body).strip(),
            width=width,
            initial_indent="  ",
            subsequent_indent="  ",
        )
        blocks.append(f"{heading}\n{filled}")
    return "\n\n".join(blocks)


def test_solve():
    r = rng()
    sections, width = _gen(r)

    got = solve(sections, width)
    assert got == _reference(sections, width), f"report at width {width}"

    for line in got.splitlines():
        assert len(line) <= width, f"{line!r} is {len(line)} columns, over the {width} limit"
    assert not got.endswith("\n"), "no trailing newline"
    for heading, _ in sections:
        assert f"\n{heading}\n" in f"\n{got}", f"{heading} must sit unindented on its own line"

    # at width 20 the two-space indent is exactly what moves the first break point
    canonical = solve([("Certs", "\n    certificate expires\n    tomorrow")], 20)
    assert canonical == "Certs\n  certificate\n  expires tomorrow", canonical
