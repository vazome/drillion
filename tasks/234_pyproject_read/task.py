import tomllib


def solve(text):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_LIBS = ["requests", "httpx", "pydantic", "click", "rich", "anyio", "attrs", "boto3"]
_DEV = ["pytest", "ruff", "mypy", "coverage", "hypothesis"]


def _gen(r):
    lines = ["[project]", f'name = "{r.choice(["drillion", "audit-bot", "wavefront", "pinch"])}"']
    if r.random() < 0.6:
        lines.append(f'requires-python = ">=3.{r.choice([10, 11, 12, 13])}"')
    if r.random() < 0.6:
        lines.append("dependencies = [" + ", ".join(f'"{d}"' for d in r.sample(_LIBS, 3)) + "]")
    if r.random() < 0.6:
        lines.append("[project.optional-dependencies]")
        # the table can exist with only a group that is not 'dev'
        group = "dev" if r.random() < 0.7 else "docs"
        lines.append(f"{group} = [" + ", ".join(f'"{d}"' for d in r.sample(_DEV, 2)) + "]")
    if r.random() < 0.5:
        lines.append("[tool.ruff]")
        lines.append(f"line-length = {r.choice([79, 100, 120])}")
    return "\n".join(lines) + "\n"


def _reference(text):
    data = tomllib.loads(text)
    project = data["project"]
    return {
        "name": project["name"],
        "requires_python": project.get("requires-python"),
        "dependencies": sorted(project.get("dependencies", [])),
        "dev_dependencies": sorted(project.get("optional-dependencies", {}).get("dev", [])),
        "line_length": data.get("tool", {}).get("ruff", {}).get("line-length", 88),
    }


def test_solve():
    r = rng()
    seen = set()
    for _ in range(24):
        text = _gen(r)
        got = solve(text)
        want = _reference(text)
        assert got == want, f"for pyproject:\n{text}\ngot {got}"
        assert set(got) == set(want), f"exactly the five keys, got {sorted(got)}"
        assert type(got["line_length"]) is int, "line_length must be an int"
        seen.add((want["requires_python"] is None, not want["dependencies"], want["line_length"] == 88))

    # the point of the task: the absent tables have to be exercised, not just the full file
    assert len(seen) >= 4, "generator should cover several combinations of missing tables"

    canonical = solve('[project]\nname = "drillion"\n[tool.ruff]\nline-length = 100\n')
    assert canonical == {
        "name": "drillion",
        "requires_python": None,
        "dependencies": [],
        "dev_dependencies": [],
        "line_length": 100,
    }, canonical
