"""What one sitting of 347 asks for: one fix replayed onto a release branch, nothing else
main did since that branch split off.

The answer is the repository's end state: the release branch one commit ahead, holding
only that fix, main untouched."""


def brief(r):
    return {"bug": r.choice(["rounding", "timezone", "encoding"]), "minor": r.randint(2, 9)}


def setup(repo, b):
    repo.commit("start", {"app.py": "VERSION = '1.0'\n"})
    repo.commit("add reports", {"reports.py": "def report():\n    pass\n"})
    repo.git("branch", f"release/1.{b['minor']}")
    repo.commit("add dashboards", {"dash.py": "def dash():\n    pass\n"})
    repo.commit(f"fix {b['bug']}", {f"{b['bug']}.py": f"# fixed {b['bug']}\n"})
    repo.commit("add exports", {"exports.py": "def export():\n    pass\n"})
