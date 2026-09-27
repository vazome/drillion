"""What one sitting of 349 asks for: a fix to an earlier commit folded into it without
hand-editing a rebase todo list.

The answer is the repository's end state: still two commits, the first now holding the
fixed version, no fixup commit left over."""


def brief(r):
    return {"sep": r.choice([",", ";", "|"])}


def setup(repo, b):
    sep = b["sep"]
    repo.commit("start", {"README.md": "# Parser\n"})
    repo.git("switch", "-q", "-c", "feature/parser")
    repo.commit("add parser", {"parser.py": f"def parse(text):\n    return text.split('{sep}')\n"})
    repo.commit("add parser tests", {"test_parser.py": "def test_parse():\n    pass\n"})
    repo.write("parser.py", f"def parse(text):\n    return [part.strip() for part in text.split('{sep}')]\n")
