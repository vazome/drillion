"""What one sitting of 341 asks for: the last commit fixed in place, not piled on top of.

The answer is the repository's end state: still two commits, the second holding both the
module and its test, under a message that describes what it actually holds."""

APPS = ["csv", "json", "toml"]


def brief(r):
    return {"app": r.choice(APPS)}


def setup(repo, b):
    app = b["app"]
    repo.commit("start the project", {"README.md": "# Project\n"})
    repo.commit("wip", {f"{app}.py": f"def parse(text):\n    return text  # {app}\n"})
    repo.write(
        f"test_{app}.py",
        f"from {app} import parse\n\n\ndef test_parse():\n    assert parse('x') == 'x'\n",
    )
