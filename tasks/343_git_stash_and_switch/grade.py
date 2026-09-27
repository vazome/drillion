"""What one sitting of 343 asks for: unfinished work set aside, a fix made elsewhere, then
the unfinished work returned exactly as it was.

The answer is the repository's end state: one new commit on `main`, the feature branch's
tracked edit and untracked file back and still unstaged, and the stash left empty."""

FEATURES = ["search", "export", "invoices"]


def brief(r):
    return {"feature": r.choice(FEATURES), "retries": r.randint(3, 6)}


def setup(repo, b):
    f = b["feature"]
    repo.commit("add config", {"config.py": "RETRIES = 1\nTIMEOUT = 30\n"})
    repo.git("switch", "-q", "-c", f"feature/{f}")
    repo.commit(f"start {f}", {f"{f}.py": "def run():\n    pass\n"})
    repo.write(f"{f}.py", "def run():\n    return 'half done'\n")
    repo.write(f"{f}_notes.md", "- remember the edge case\n")
