"""rna-transcription — a one-to-one character swap, and why four .replace() calls fail."""
# SOURCE: exercism/python practice/rna-transcription (MIT, adapted)
# READ FIRST:
#   https://docs.python.org/3/library/stdtypes.html#str.translate  — str.maketrans and
#       translate: build the mapping once, apply it in one pass
#   https://docs.python.org/3/library/stdtypes.html#str.join  — "".join over a generator, the
#       readable way to build a string character by character
#   https://docs.python.org/3/library/stdtypes.html#str.replace  — read this one to see the
#       trap: each replace() runs over the result of the previous one

from _lib import rng

META = {"topic": 309, "title": "rna-transcription — turn a DNA strand into its RNA partner",
        "minutes": 10, "prereqs": [200, 203, 209, 215, 218, 227],
        "tags": ["exercism", "string-methods", "core"]}


def solve(dna_strand):
    """WHY: A bioengineering team designs a molecule that switches off one
    misbehaving protein. To build it they need the RNA strand that pairs
    with a given piece of DNA, which means swapping every letter for its
    partner. One wrong letter and the molecule binds to something else
    entirely. Underneath the biology it is the most common string job
    there is — a fixed, one-to-one character mapping — and it hides the
    classic bug where you translate a letter and then translate your own
    output by mistake.

    YOU GET: `dna_strand` — a string of the DNA letters A, C, G and T,
    e.g. "ACGTGGTCTTAA". It may be empty.

    YOU RETURN: a string of the same length, holding the RNA complement.

    ─── exact rules ───
    Replace each letter with its partner, leaving the order untouched:

        G -> C      C -> G      T -> A      A -> U

    An empty strand transcribes to an empty string. Note that A becomes U
    while T becomes A: two letters map onto A's neighbourhood, which is
    where careless solutions come apart.

        solve("C")             ->  "G"
        solve("ACGTGGTCTTAA")  ->  "UGCACCAGAAUU"
        solve("")              ->  ""
    """
    raise NotImplementedError


HINTS = [
    ("Every character turns into exactly one other character and nothing else "
    "moves — the output is always as long as the input. So this is a per-"
    "character lookup, not a series of search-and-replace passes over the whole "
    "string. (Try four chained .replace() calls on paper with 'AT' and watch the "
    "T become A and then that A become U.)"),
    ("Two routes, both fine. The readable one: a dict {'G': 'C', 'C': 'G', ...} "
    "and \"\".join of the looked-up value for each character. The idiomatic one: "
    "str.maketrans(<the four DNA letters>, <their partners, in the same order>) "
    "builds the table once and str.translate applies it in a single pass — worth "
    "knowing because interviewers notice it."),
    ("Different data, same swap:\n"
    "    table = str.maketrans('abc', 'xyz')\n"
    "    'cab'.translate(table)   ->  'zxy'\n"
    "Each character is looked at exactly once against the original table, so a "
    "letter you have just written can never be translated a second time — that "
    "is precisely what chained replaces get wrong."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

def _gen(r):
    n = r.randint(0, 24)
    return "".join(r.choice("ACGT") for _ in range(n))


def _reference(dna_strand):
    return dna_strand.translate(str.maketrans("AGCT", "UCGA"))


def test_solve():
    r = rng()
    for _ in range(6):
        dna_strand = _gen(r)
        assert solve(dna_strand) == _reference(dna_strand), f"strand {dna_strand!r}"

    # canonical cases (exercism/python practice/rna-transcription)
    assert solve("") == ""
    assert solve("C") == "G"
    assert solve("G") == "C"
    assert solve("T") == "A"
    assert solve("A") == "U"
    assert solve("ACGTGGTCTTAA") == "UGCACCAGAAUU"
