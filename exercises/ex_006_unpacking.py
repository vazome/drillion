"""Star-unpacking and tuple assignment — Python's way of naming the parts."""

from _lib import rng

META = {"topic": 6, "title": "unpacking — star, swap, loop", "tier": 3,
        "minutes": 12, "prereqs": []}


def solve(xs, pairs):
    """xs is a list of numbers (at least 3 long). pairs is a list of
    (key, value) tuples of strings. Return a dict:

        "first":   first item of xs
        "rest":    everything after the first, as a list
        "body":    everything before the last, as a list
        "last":    last item
        "swapped": a copy of xs with first and last items exchanged
        "lines":   one "key=value" string per pair

        xs=[5, 6, 7], pairs=[("env", "prod"), ("region", "eu")]
        ->  {"first": 5, "rest": [6, 7], "body": [5, 6], "last": 7,
             "swapped": [7, 6, 5], "lines": ["env=prod", "region=eu"]}

    Slicing would pass the test — do it with star-unpacking anyway
    (a, *rest = ...), one tuple swap with no temp variable, and unpack
    each pair right in the for line. That is what is being drilled.
    """
    raise NotImplementedError


HINTS = [
    "One starred name on the LEFT of an assignment soaks up 'whatever is "
    "left over' as a list, and it can sit at either end. Swapping needs no "
    "temp variable because Python builds the whole right-hand side before "
    "assigning anything.",
    "Four moves: star-assign with the star last to split off the first item; "
    "star first to split off the last; on a copy of xs, assign a pair to a "
    "pair to swap the ends; and in the loop header give each pair's two "
    "slots their own names.",
    "Different data, same moves:\n"
    "    q = ['mon', 'tue', 'wed', 'thu']\n"
    "    head, *tail = q            # 'mon', ['tue', 'wed', 'thu']\n"
    "    *early, final = q          # ['mon', 'tue', 'wed'], 'thu'\n"
    "    a, b = 1, 2\n"
    "    a, b = b, a                # a=2, b=1\n"
    "    for k, v in [('cpu', '90'), ('mem', '40')]:\n"
    "        print(k + '=' + v)     # cpu=90  mem=40\n"
    "Same shapes, collected into your dict.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    xs = [r.randint(0, 99) for _ in range(r.randint(3, 8))]
    keys = r.sample(["env", "region", "tier", "owner", "app"], r.randint(2, 4))
    vals = ["prod", "dev", "eu", "us", "web", "ops"]
    pairs = [(k, r.choice(vals)) for k in keys]
    return xs, pairs


def _reference(xs, pairs):
    first, *rest = xs
    *body, last = xs
    swapped = list(xs)
    swapped[0], swapped[-1] = swapped[-1], swapped[0]
    lines = [f"{k}={v}" for k, v in pairs]
    return {"first": first, "rest": rest, "body": body, "last": last,
            "swapped": swapped, "lines": lines}


def test_solve():
    r = rng()
    for _ in range(4):
        xs, pairs = _gen(r)
        assert solve(list(xs), [tuple(p) for p in pairs]) == _reference(xs, pairs)
