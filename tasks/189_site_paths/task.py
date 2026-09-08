def solve(root: str) -> list[str]:
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    import tempfile
    from pathlib import Path

    root = Path(tempfile.mkdtemp(prefix="ex189_"))
    sections = r.sample(["guides", "reference", "blog", "about"], r.randint(2, 4))
    for section in sections:
        (root / section).mkdir()
        for page in r.sample(["index", "setup", "faq", "api", "changelog"], r.randint(1, 3)):
            (root / section / f"{page}.md").write_text("# page\n", encoding="utf-8")
        (root / section / "notes.txt").write_text("scratch\n", encoding="utf-8")
        if r.random() < 0.6:
            drafts = root / section / "drafts"
            drafts.mkdir()
            (drafts / "wip.md").write_text("# wip\n", encoding="utf-8")
    deep = root / sections[0] / "v2"
    deep.mkdir()
    (deep / "upgrade.md").write_text("# upgrade\n", encoding="utf-8")
    (root / "index.md").write_text("# home\n", encoding="utf-8")
    return str(root)


def _reference(root):
    from pathlib import Path

    root = Path(root)
    return sorted(
        p.relative_to(root).with_suffix(".html").as_posix()
        for p in root.rglob("*.md")
        if "drafts" not in p.relative_to(root).parts
    )


def test_solve():
    import shutil

    r = rng()
    for _ in range(4):
        root = _gen(r)
        try:
            assert solve(root) == _reference(root), root
        finally:
            shutil.rmtree(root, ignore_errors=True)
