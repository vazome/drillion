"""What one sitting of 350 asks for: a branch replayed onto main's current tip, a conflict
along the way resolved and the branch landed without a merge commit.

The answer is the repository's end state: the branch's commits sitting on top of main,
the conflicting file resolved, main fast-forwarded, the branch gone."""


def brief(r):
    return {"feature": r.choice(["search", "billing"]), "size": r.randint(20, 90)}


def setup(repo, b):
    f = b["feature"]
    repo.commit("start", {"limits.py": "PAGE_SIZE = 10\n", "README.md": "# App\n"})
    repo.git("switch", "-q", "-c", f"feature/{f}")
    repo.commit(f"add {f}", {f"{f}.py": "def run():\n    pass\n"})
    repo.commit(f"page {f} results", {"limits.py": "PAGE_SIZE = 25\n"})
    repo.git("switch", "-q", "main")
    repo.commit("add health check", {"health.py": "def ok():\n    return True\n"})
    repo.commit("raise the page size", {"limits.py": "PAGE_SIZE = 50\n"})
