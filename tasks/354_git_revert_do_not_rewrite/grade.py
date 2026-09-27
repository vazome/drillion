"""What one sitting of 354 asks for: a commit already on origin undone without touching any
other commit, since rewriting it would just be rejected on the next push.

The answer is the repository's end state: a new commit reverting the flag commit, everything
else untouched, pushed to origin."""


def brief(r):
    return {"flag": r.choice(["dark mode", "beta search", "new checkout"])}


def setup(repo, b):
    repo.origin()
    repo.commit("start", {"README.md": "# App\n", "flags.py": "ENABLED = []\n"})
    repo.commit(f"enable {b['flag']} by default", {"flags.py": f"ENABLED = [{b['flag']!r}]\n"})
    repo.commit("add metrics", {"metrics.py": "COUNT = 0\n"})
    repo.git("push", "-q", "-u", "origin", "main")
