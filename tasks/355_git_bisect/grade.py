"""What one sitting of 355 asks for: the first commit that broke a check, found by binary
search instead of by reading fifteen commits one at a time.

The answer is the repository's end state: a tag on the first commit where the check fails,
and the bisect itself finished."""


def brief(r):
    return {"bad": r.randint(4, 13), "rate": r.choice([15, 20, 25])}


def setup(repo, b):
    rate = b["rate"]
    repo.commit(
        "start", {"calc.py": f"RATE = {rate}\n", "check.sh": f"grep -qx 'RATE = {rate}' calc.py\n"}
    )
    for i in range(1, 16):
        files = {f"notes/{i}.md": f"# Note {i}\n"}
        if i == b["bad"]:
            files["calc.py"] = f"RATE = {rate // 5}\n"
        repo.commit(f"change {i}", files)
