"""What one sitting of 351 asks for: two commits squashed into one on main, and a branch's
last commit thrown away entirely.

The answer is the repository's end state: main with the two export commits replaced by one,
and experiment with its last commit and the file it added both gone."""


def brief(r):
    return {"format": r.choice(["csv", "json", "xml"])}


def setup(repo, b):
    fmt = b["format"]
    repo.commit("start", {"README.md": "# Reports\n"})
    repo.commit("export part 1", {"export.py": f"def export(rows):\n    return '{fmt}'\n"})
    repo.commit(
        "export part 2",
        {
            "export.py": f"def export(rows):\n    return '{fmt}', rows\n",
            "test_export.py": "def test_export():\n    pass\n",
        },
    )
    repo.git("switch", "-q", "-c", "experiment")
    repo.commit("try a faster writer", {"fast.py": "FAST = True\n"})
    repo.git("switch", "-q", "main")
