def solve(paths: list[str], known_good: str):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import hashlib
import os
import shutil
import tempfile

from _lib import rng


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
