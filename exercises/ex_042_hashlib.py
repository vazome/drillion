"""A checksum is how you prove the artifact you deployed is the artifact you built."""

import hashlib
import os
import shutil
import tempfile

from _lib import rng

META = {"topic": 42, "title": "hashlib — checksum files against a known digest",
        "tier": 3, "minutes": 10, "prereqs": []}


def solve(paths, known_good):
    """WHY: The release pipeline publishes a checksum (a short fingerprint
    string computed from a file's bytes) next to every build artifact.
    Before deploying, you must prove the files that arrived on the server
    are the exact ones that were built: a single changed byte, from a
    corrupted download or tampering, must be caught. You compute each file's
    fingerprint and compare it with the published one.

    YOU GET: `paths` — a list of file path strings, like
    ["/tmp/x/build-0.bin", "/tmp/x/build-1.bin"]. The test writes the files
    and hands you the paths; you never build them yourself.

    YOU GET: `known_good` — a string, the correct fingerprint in lowercase
    hex, like "9f86d0...".

    YOU RETURN: a dict with "digests" (filename to fingerprint), "match" and
    "bad" (sorted lists of filenames), as in the rules below.

    ─── exact rules ───
    `paths` is a list of file paths (strings). `known_good` is the sha256
    hex digest of the artifact you were supposed to receive.

    Return exactly:

        {"digests": {"build-0.bin": "9f86d0...", "build-1.bin": "3a7bd3..."},
         "match":   ["build-0.bin"],     # digest equals known_good, sorted
         "bad":     ["build-1.bin"]}     # everything else, sorted

    Keys in "digests" are basenames, not full paths. Digests are lowercase hex
    strings, which is what .hexdigest() already gives you.

    Read each file as BYTES — open in "rb", not text mode. A hash function eats
    bytes; handing it a decoded string is the usual first error, and on a real
    binary artifact decoding would fail outright.

    These files are small, so read each one whole. For a multi-gigabyte image
    you would loop over chunks and call .update() on the hash object instead of
    holding the file in memory.

    Some of these files differ from the good one by a single byte. A digest
    turns that one byte into a completely different string, with no way to tell
    a typo from sabotage — that property is why release pipelines publish
    checksums at all.
    """
    raise NotImplementedError


HINTS = [
    ("A hash reads bytes and returns a short fixed-length fingerprint. Same "
    "bytes in, same fingerprint out, every time and on every machine; one bit "
    "different and the fingerprint is unrecognisable. So you never compare "
    "files by size or by name — you compare their digests, as strings."),
    ("hashlib.sha256(data) where data is bytes, then .hexdigest() on the result "
    "for the lowercase hex string. Open with open(path, 'rb') and .read(), or "
    "use pathlib's read_bytes. os.path.basename turns the path into the key. "
    "Then it is one pass over the digests dict to split matching from "
    "non-matching, sorted at the end."),
    ("Different data, same idea:\n"
    "    import hashlib\n"
    "    print(hashlib.sha256(b'ok').hexdigest()[:16])    # 2689367b205c16ce\n"
    "    print(hashlib.sha256(b'Ok').hexdigest()[:16])    # 843ac01149cced78\n"
    "\n"
    "    with open('/etc/hostname', 'rb') as f:\n"
    "        print(hashlib.sha256(f.read()).hexdigest())\n"
    "One flipped bit in the input, nothing in common in the output."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    """(paths, known_good_hex). Some files are byte-identical to the good
    artifact, some differ by one byte, some are truncated."""
    root = tempfile.mkdtemp(prefix="ex042_")
    payload = bytes(r.randrange(256) for _ in range(r.randint(64, 400)))
    known_good = hashlib.sha256(payload).hexdigest()

    kinds = ["same", "flip"]
    kinds += [r.choice(["same", "flip", "flip", "short"])
              for _ in range(r.randint(2, 5))]
    r.shuffle(kinds)

    paths = []
    for i, kind in enumerate(kinds):
        data = bytearray(payload)
        if kind == "flip":
            at = r.randrange(len(data))
            data[at] = (data[at] + r.randint(1, 255)) % 256
        elif kind == "short":
            del data[-r.randint(1, 20):]
        name = f"{r.choice(['build', 'image', 'chart', 'bundle'])}-{i}.bin"
        path = os.path.join(root, name)
        with open(path, "wb") as f:
            f.write(bytes(data))
        paths.append(path)
    return paths, known_good


def _reference(paths, known_good):
    digests = {}
    for path in paths:
        with open(path, "rb") as f:
            digests[os.path.basename(path)] = hashlib.sha256(f.read()).hexdigest()
    return {"digests": digests,
            "match": sorted(n for n, d in digests.items() if d == known_good),
            "bad": sorted(n for n, d in digests.items() if d != known_good)}


def test_solve():
    r = rng()
    for _ in range(3):
        paths, known_good = _gen(r)
        try:
            assert solve(list(paths), known_good) == _reference(paths, known_good)
        finally:
            shutil.rmtree(os.path.dirname(paths[0]), ignore_errors=True)
