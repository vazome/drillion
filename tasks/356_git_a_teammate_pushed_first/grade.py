"""What one sitting of 356 asks for: main brought up to date with a teammate's push and an
uncommitted edit in the way, then a rewritten branch landed on origin without clobbering
anyone else's view of it.

The answer is the repository's end state: main rebased on the teammate's commit with the
uncommitted edit restored, and the feature branch force-pushed with a lease."""


def brief(r):
    return {
        "feature": r.choice(["search", "reports"]),
        "note": r.choice(["call the vendor", "update the runbook"]),
    }


def setup(repo, b):
    f = b["feature"]
    repo.origin()
    repo.commit("start", {"README.md": "# Team app\n", "notes.md": "# Notes\n"})
    repo.git("push", "-q", "-u", "origin", "main")
    repo.git("switch", "-q", "-c", f"feature/{f}")
    repo.commit(f"add {f}", {f"{f}.py": "def run():\n    pass\n"})
    repo.git("push", "-q", "-u", "origin", f"feature/{f}")
    repo.write(f"{f}.md", f"# {f}\n")
    repo.git("add", f"{f}.md")
    repo.clock += 1
    repo.git("commit", "-q", "--amend", "-m", f"add {f} with docs")
    repo.git("switch", "-q", "main")
    mate = repo.teammate()
    mate.commit("teammate: add ci", {"ci.yml": "steps: []\n"})
    mate.git("push", "-q", "origin", "main")
    repo.commit("add changelog", {"CHANGELOG.md": "# Changes\n"})
    repo.write("notes.md", f"# Notes\n\n- {b['note']}\n")
