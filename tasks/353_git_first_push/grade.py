"""What one sitting of 353 asks for: a first push that leaves main tracking origin, and a
new branch that is pushed and tracked the same way from the moment it exists.

The answer is the repository's end state: main on origin and tracking it, and a new
docs/{topic} branch with one commit, pushed and tracking origin/docs/{topic}."""

TOPICS = {"setup": "Setting up", "deploys": "Deploying", "alerts": "Alerts"}


def brief(r):
    topic = r.choice(sorted(TOPICS))
    return {"topic": topic, "title": TOPICS[topic]}


def setup(repo, b):
    repo.origin()
    repo.commit("start", {"README.md": "# Service\n"})
    repo.commit("add the api", {"api.py": "def health():\n    return 'ok'\n"})


def probes(b):
    return {
        "the branch main tracks": ["rev-parse", "--abbrev-ref", "main@{upstream}"],
        f"the branch docs/{b['topic']} tracks": [
            "rev-parse",
            "--abbrev-ref",
            f"docs/{b['topic']}@{{upstream}}",
        ],
    }
