"""pathlib turns path string-surgery into readable code — and interviewers notice."""

from _lib import rng

META = {"topic": 27, "title": "pathlib.Path — walk and inspect a tree", "tier": 3,
        "minutes": 12, "prereqs": []}


def solve(root):
    """WHY: A company keeps one folder per service on a shared server, each
    with its own log and config subfolders. Before a migration the platform
    team asks for an inventory: the name of every log file anywhere under
    the root, the name (minus extension) of every config file, and whether
    someone already wrote a README at the top. Chopping path strings by hand
    is error-prone; you need to walk the whole tree and ask questions about
    each path.

    YOU GET: `root` — a string with the path to the top folder, like
    "/tmp/ex027_xyz". The test builds a small tree of folders and files
    under it and hands you the path; you never build it yourself.

    YOU RETURN: a dict with three keys: "logs" (sorted list of log file
    names), "conf_stems" (sorted list of config file names without the
    extension) and "has_readme" (True or False).

    ─── exact rules ───
    `root` is a directory path as a STRING. The tree under it looks like:

        root/
          api/
            logs/api-0.log
            conf/api.conf
            notes.txt
          web/
            logs/web-0.log
          README.md            <- sometimes absent

    Build a pathlib.Path from it and return:

        {"logs":       ["api-0.log", "web-0.log"],  # .name of every *.log anywhere under root, sorted
         "conf_stems": ["api"],                     # .stem of every *.conf anywhere under root, sorted
         "has_readme": True}                        # does root/README.md exist

    Join paths with the / operator, not string concatenation. The .log and
    .conf files sit at any depth — search the whole tree, not just the top.
    """
    raise NotImplementedError


HINTS = [
    ("pathlib treats a path as an object, not a string: joining, searching and "
    "asking questions about it are all methods. glob looks in one directory "
    "only; it has a sibling that walks the entire tree. A Path also knows its "
    "own final component, and that component with the extension removed."),
    ("Path(root) gets you into object-land. rglob('*.log') yields every match "
    "in the whole tree. .name is the final component, .stem is that minus the "
    "suffix. Join with the / operator and ask .exists() for the readme. Wrap "
    "both listings in sorted so the order is fixed."),
    ("Different data, same moves:\n"
    "    from pathlib import Path\n"
    "    etc = Path('/etc')\n"
    "    units = sorted(p.name for p in etc.rglob('*.timer'))\n"
    "    p = Path('/var/log/nginx/access.log')\n"
    "    print(p.name, p.stem, p.suffix)   # access.log access .log\n"
    "    print((etc / 'hosts').exists())   # True on most boxes\n"
    "One object, and the string-splitting you used to do disappears."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    import tempfile
    from pathlib import Path
    root = Path(tempfile.mkdtemp(prefix="ex027_"))
    services = r.sample(["api", "auth", "billing", "cron", "web", "worker"],
                        r.randint(2, 4))
    for svc in services:
        logs = root / svc / "logs"
        logs.mkdir(parents=True)
        for i in range(r.randint(1, 3)):
            (logs / f"{svc}-{i}.log").write_text(f"line {i}\n", encoding="utf-8")
        if r.random() < 0.7:
            conf = root / svc / "conf"
            conf.mkdir()
            (conf / f"{svc}.conf").write_text("k: v\n", encoding="utf-8")
    (root / services[0] / "notes.txt").write_text("scratch\n", encoding="utf-8")
    if r.random() < 0.5:
        (root / "README.md").write_text("readme\n", encoding="utf-8")
    return str(root)


def _reference(root):
    from pathlib import Path
    root = Path(root)
    return {"logs": sorted(p.name for p in root.rglob("*.log")),
            "conf_stems": sorted(p.stem for p in root.rglob("*.conf")),
            "has_readme": (root / "README.md").exists()}


def test_solve():
    import shutil
    r = rng()
    for _ in range(3):
        root = _gen(r)
        try:
            assert solve(root) == _reference(root)
        finally:
            shutil.rmtree(root, ignore_errors=True)
