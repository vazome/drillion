"""What one sitting of 340 asks for: two unrelated edits in one file, split into two commits.

The answer is the repository's end state: two new commits, the first touching only the
`open(...)` line, the second the rest of the diff."""

NAMES = {"timeout": "30", "retries": "3", "region": "'eu-west-1'"}
BEFORE = '''def load(path):
    with open(path) as stream:
        return stream.read()


# the defaults below are read once, at start-up
LOG_LEVEL = "info"
LOG_FORMAT = "plain"
WORKERS = 4
QUEUE = "default"
CACHE = "memory"
TRACING = False


def default_{name}():
    return None
'''


def brief(r):
    name = r.choice(sorted(NAMES))
    return {"name": name, "value": NAMES[name]}


def setup(repo, b):
    before = BEFORE.format(name=b["name"])
    repo.commit("add settings", {"settings.py": before})
    after = before.replace("open(path)", 'open(path, encoding="utf-8")')
    repo.write("settings.py", after.replace("    return None", f"    return {b['value']}"))
