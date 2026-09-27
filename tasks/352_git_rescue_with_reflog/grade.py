"""What one sitting of 352 asks for: a deleted branch and a hard-reset commit, both brought
back from the reflog, not from memory of the hashes.

The answer is the repository's end state: the feature branch recreated at its last commit,
and main back at the commit it lost, with nothing left uncommitted."""


def brief(r):
    return {"feature": r.choice(["search", "audit"]), "lost": r.choice(["metrics", "cache"])}


def setup(repo, b):
    f, g = b["feature"], b["lost"]
    repo.commit("start", {"README.md": "# App\n"})
    repo.git("switch", "-q", "-c", f"feature/{f}")
    repo.commit(f"add {f}", {f"{f}.py": "def run():\n    pass\n"})
    repo.commit(f"add {f} tests", {f"test_{f}.py": "def test_run():\n    pass\n"})
    repo.git("switch", "-q", "main")
    repo.git("branch", "-q", "-D", f"feature/{f}")
    repo.commit(f"add {g}", {f"{g}.py": "ON = True\n"})
    repo.git("reset", "-q", "--hard", "HEAD~1")
