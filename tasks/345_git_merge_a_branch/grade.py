"""What one sitting of 345 asks for: two finished branches landed on main the way each one
calls for, a fast-forward for one, a merge commit for the other, both gone afterward.

The answer is the repository's end state: main holding both branches' commits, one folded
in without a merge commit and one with git's default message, neither branch left behind."""


def brief(r):
    return {"a": r.choice(["search", "login"]), "b": r.choice(["export", "audit"])}


def setup(repo, b):
    a, bb = b["a"], b["b"]
    repo.commit("start", {"README.md": "# Shop\n"})
    repo.git("branch", f"feature/{bb}")
    repo.git("switch", "-q", "-c", f"feature/{a}")
    repo.commit(f"add {a}", {f"{a}.py": "def run():\n    pass\n"})
    repo.commit(f"test {a}", {f"test_{a}.py": "def test_run():\n    pass\n"})
    repo.git("switch", "-q", f"feature/{bb}")
    repo.commit(f"add {bb}", {f"{bb}.py": "def run():\n    pass\n"})
    repo.git("switch", "-q", "main")
