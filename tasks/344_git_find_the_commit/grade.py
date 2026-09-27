"""What one sitting of 344 asks for: two commits found by what they changed, not by
scrolling, and marked with a tag so they can be named again.

The answer is the repository's end state: `introduced` on the commit that first added a
line of config, and `last-docs` on one author's most recent commit under `docs/`."""

AUTHORS = [
    ("Grace Hopper", "grace@example.com"),
    ("Alan Turing", "alan@example.com"),
    ("Barbara Liskov", "barbara@example.com"),
]
# no author's last commit touches docs/, so a search that drops the path finds another
DOCS = (1, 2, 3, 4, 5, 6)


def brief(r):
    return {"limit": r.randint(10, 50), "author": r.choice(AUTHORS)[0]}


def setup(repo, b):
    repo.commit("start", {"README.md": "# Upload service\n", "docs/index.md": "# Docs\n"})
    for i in range(12):
        name, email = AUTHORS[i % 3]
        files = {f"src/step{i}.py": f"STEP = {i}\n"}
        if i == 4:
            files["src/limits.py"] = f"MAX_UPLOAD_MB = {b['limit']}\n"
        if i == 9:
            files["src/limits.py"] = f"MAX_UPLOAD_MB = {b['limit'] + 5}\n"
        if i in DOCS:
            files[f"docs/page{i}.md"] = f"# Page {i}\n"
        repo.commit(f"step {i}", files, author=f"{name} <{email}>")
