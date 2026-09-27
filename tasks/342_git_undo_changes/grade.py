"""What one sitting of 342 asks for: two different mistakes, undone two different ways.

The answer is the repository's end state: the worktree edit gone, the staged edit still
in the worktree but no longer staged, and no new commit."""

NOTES = ["ship on Friday", "ask about the rate limit", "rename the queue"]
APP = "def total(items):\n    total = 0\n    for item in items:\n        total += item\n    return total\n"


def brief(r):
    return {"note": r.choice(NOTES)}


def setup(repo, b):
    repo.commit("add the app", {"app.py": APP, "notes.md": "# Notes\n"})
    repo.write("app.py", APP.replace("return total", "return 0  # quick hack"))
    repo.write("notes.md", f"# Notes\n\n- {b['note']}\n")
    repo.git("add", "notes.md")
