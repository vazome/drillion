"""What one sitting of 348 asks for: a branch's working history folded, reworded and
trimmed into the history it should have shipped with.

The answer is the repository's end state: two commits, a finished module and a reworded
validation commit, the debug print gone."""


def brief(r):
    return {"form": r.choice(["signup", "contact", "checkout"])}


def setup(repo, b):
    f = b["form"]
    repo.commit("start", {"README.md": "# Forms\n"})
    repo.git("switch", "-q", "-c", f"feature/{f}")
    repo.commit(f"add {f} form", {f"{f}.py": "FIELDS = ['name']\n"})
    repo.commit("wip", {f"{f}.py": "FIELDS = ['name', 'emial']\n"})
    repo.commit(f"fix typo in {f} form", {f"{f}.py": "FIELDS = ['name', 'email']\n"})
    repo.commit(f"add {f} validation", {"validate.py": "def valid(form):\n    return all(form.values())\n"})
    repo.commit("debug print", {"debug.py": "print('here')\n"})
