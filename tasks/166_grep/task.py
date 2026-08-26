def solve(pattern, flags, files):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_FILE_NAMES = ["notes.txt", "runbook.md", "alerts.log", "inventory.csv", "diary.txt", "poem.txt"]

_LINES = [
    "the night shift found the leak",
    "Ada wrote the first report",
    "no answer from the north gate",
    "Grace filed a second report",
    "THE PUMP IS OFFLINE",
    "a quiet morning, nothing to add",
    "the north gate answered at last",
    "Alan signed off on the repair",
    "second pump running warm",
    "nothing to report",
    "Katherine closed the ticket",
    "the leak was never found",
]

_CANONICAL = {
    "iliad.txt": """Achilles sing, O Goddess! Peleus' son;
His wrath pernicious, who ten thousand woes
Caused to Achaia's host, sent many a soul
Illustrious into Ades premature,
And Heroes gave (so stood the will of Jove)
To dogs and to all ravening fowls a prey,
When fierce dispute had separated once
The noble Chief Achilles from the son
Of Atreus, Agamemnon, King of men.\n""",
    "midsummer-night.txt": """I do entreat your grace to pardon me.
I know not by what power I am made bold,
Nor how it may concern my modesty,
In such a presence here to plead my thoughts;
But I beseech your grace that I may know
The worst that may befall me in this case,
If I refuse to wed Demetrius.\n""",
    "paradise-lost.txt": """Of Mans First Disobedience, and the Fruit
Of that Forbidden Tree, whose mortal tast
Brought Death into the World, and all our woe,
With loss of Eden, till one greater Man
Restore us, and regain the blissful Seat,
Sing Heav'nly Muse, that on the secret top
Of Oreb, or of Sinai, didst inspire
That Shepherd, who first taught the chosen Seed\n""",
}


def _gen(r):
    files = {}
    for name in r.sample(_FILE_NAMES, r.randint(1, 3)):
        files[name] = "".join(r.choice(_LINES) + "\n" for _ in range(r.randint(3, 7)))
    if r.random() < 0.25:
        # a file may be empty; slot one in anywhere, the rest still hold the lines
        spare = r.choice([name for name in _FILE_NAMES if name not in files])
        entries = list(files.items())
        entries.insert(r.randrange(len(entries) + 1), (spare, ""))
        files = dict(entries)
    every_line = [line for text in files.values() for line in text.splitlines()]
    roll = r.random()
    if roll < 0.30:
        pattern = r.choice(r.choice(every_line).split())
    elif roll < 0.55:
        pattern = r.choice(every_line)
    elif roll < 0.80:
        pattern = r.choice(r.choice(every_line).split()).upper()
    else:
        pattern = r.choice(["Gandalf", "zebra", "quarterly", "north gate"])
    chosen = [flag for flag in ("-n", "-l", "-i", "-v", "-x") if r.random() < 0.4]
    r.shuffle(chosen)
    return pattern, " ".join(chosen), files


def _reference(pattern, flags, files):
    chosen = set(flags.split())
    matches = []
    for name, contents in files.items():
        for number, line in enumerate(contents.splitlines(keepends=True), start=1):
            text, needle = line.rstrip("\n"), pattern
            if "-i" in chosen:
                text, needle = text.lower(), needle.lower()
            hit = text == needle if "-x" in chosen else needle in text
            if hit != ("-v" in chosen):
                matches.append((name, number, line))

    if "-l" in chosen:
        names = dict.fromkeys(name for name, _, _ in matches)
        return "".join(name + "\n" for name in names)

    prefixed = len(files) > 1
    out = []
    for name, number, line in matches:
        head = f"{name}:" if prefixed else ""
        if "-n" in chosen:
            head += f"{number}:"
        out.append(head + line)
    return "".join(out)


def test_solve():
    r = rng()
    for _ in range(6):
        pattern, flags, files = _gen(r)
        kept = dict(files)
        assert solve(pattern, flags, dict(files)) == _reference(pattern, flags, files), \
            f"pattern {pattern!r}, flags {flags!r}, files {files!r}"
        assert files == kept, f"solve must not change the files it is given: {pattern!r}, {flags!r}"

    # canonical cases (exercism/python practice/grep)
    one = {"iliad.txt": _CANONICAL["iliad.txt"]}
    assert solve("Agamemnon", "", one) == "Of Atreus, Agamemnon, King of men.\n"
    assert solve("ten", "-n -l", one) == "iliad.txt\n"
    assert solve("Gandalf", "-n -l -x -i", one) == ""
    assert solve("OF ATREUS, Agamemnon, KIng of MEN.", "-n -i -x", one) == \
        "9:Of Atreus, Agamemnon, King of men.\n"
    assert solve("Illustrious into Ades premature,", "-x -v", one) == (
        "Achilles sing, O Goddess! Peleus' son;\n"
        "His wrath pernicious, who ten thousand woes\n"
        "Caused to Achaia's host, sent many a soul\n"
        "And Heroes gave (so stood the will of Jove)\n"
        "To dogs and to all ravening fowls a prey,\n"
        "When fierce dispute had separated once\n"
        "The noble Chief Achilles from the son\n"
        "Of Atreus, Agamemnon, King of men.\n"
    )

    lost = {"paradise-lost.txt": _CANONICAL["paradise-lost.txt"]}
    assert solve("Of", "-v", lost) == (
        "Brought Death into the World, and all our woe,\n"
        "With loss of Eden, till one greater Man\n"
        "Restore us, and regain the blissful Seat,\n"
        "Sing Heav'nly Muse, that on the secret top\n"
        "That Shepherd, who first taught the chosen Seed\n"
    )

    every = dict(_CANONICAL)
    assert solve("Agamemnon", "", every) == "iliad.txt:Of Atreus, Agamemnon, King of men.\n"
    assert solve("that", "-n", every) == (
        "midsummer-night.txt:5:But I beseech your grace that I may know\n"
        "midsummer-night.txt:6:The worst that may befall me in this case,\n"
        "paradise-lost.txt:2:Of that Forbidden Tree, whose mortal tast\n"
        "paradise-lost.txt:6:Sing Heav'nly Muse, that on the secret top\n"
    )
    assert solve("who", "-n -l", every) == "iliad.txt\nparadise-lost.txt\n"
    assert solve("a", "-v", every) == (
        "iliad.txt:Achilles sing, O Goddess! Peleus' son;\n"
        "iliad.txt:The noble Chief Achilles from the son\n"
        "midsummer-night.txt:If I refuse to wed Demetrius.\n"
    )
    assert solve("WITH LOSS OF EDEN, TILL ONE GREATER MAN", "-n -i -x", every) == \
        "paradise-lost.txt:4:With loss of Eden, till one greater Man\n"
    assert solve("Illustrious into Ades premature,", "-x -v", every) == (
        "iliad.txt:Achilles sing, O Goddess! Peleus' son;\n"
        "iliad.txt:His wrath pernicious, who ten thousand woes\n"
        "iliad.txt:Caused to Achaia's host, sent many a soul\n"
        "iliad.txt:And Heroes gave (so stood the will of Jove)\n"
        "iliad.txt:To dogs and to all ravening fowls a prey,\n"
        "iliad.txt:When fierce dispute had separated once\n"
        "iliad.txt:The noble Chief Achilles from the son\n"
        "iliad.txt:Of Atreus, Agamemnon, King of men.\n"
        "midsummer-night.txt:I do entreat your grace to pardon me.\n"
        "midsummer-night.txt:I know not by what power I am made bold,\n"
        "midsummer-night.txt:Nor how it may concern my modesty,\n"
        "midsummer-night.txt:In such a presence here to plead my thoughts;\n"
        "midsummer-night.txt:But I beseech your grace that I may know\n"
        "midsummer-night.txt:The worst that may befall me in this case,\n"
        "midsummer-night.txt:If I refuse to wed Demetrius.\n"
        "paradise-lost.txt:Of Mans First Disobedience, and the Fruit\n"
        "paradise-lost.txt:Of that Forbidden Tree, whose mortal tast\n"
        "paradise-lost.txt:Brought Death into the World, and all our woe,\n"
        "paradise-lost.txt:With loss of Eden, till one greater Man\n"
        "paradise-lost.txt:Restore us, and regain the blissful Seat,\n"
        "paradise-lost.txt:Sing Heav'nly Muse, that on the secret top\n"
        "paradise-lost.txt:Of Oreb, or of Sinai, didst inspire\n"
        "paradise-lost.txt:That Shepherd, who first taught the chosen Seed\n"
    )
