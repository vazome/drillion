"""What one sitting of 339 asks for: a first commit that leaves a secret behind.

The answer is the repository's end state: one new commit holding the app, its test and a
`.gitignore`, with the secret file staged, tracked or committed nowhere."""

APPS = ["parser", "ledger", "mailer", "billing"]
SECRETS = [".env", "secrets.env", "local.env"]


def brief(r):
    return {"app": r.choice(APPS), "secret": r.choice(SECRETS)}


def setup(repo, b):
    app = b["app"]
    repo.commit("start the project", {"README.md": "# Project\n"})
    repo.write(f"{app}.py", f"def run():\n    return '{app}'\n")
    repo.write(
        f"test_{app}.py",
        f"from {app} import run\n\n\ndef test_run():\n    assert run() == '{app}'\n",
    )
    repo.write(b["secret"], "API_TOKEN=do-not-commit\n")
