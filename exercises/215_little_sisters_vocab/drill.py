def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_ROOTS = ["happy", "manageable", "fold", "eaten", "avoidable", "usual", "clear",
          "certain", "kind", "even", "settled", "aware", "wanted", "spoken"]

_GROUPS = {
    "en": ["circle", "fold", "close", "joy", "lighten", "tangle", "able", "code"],
    "pre": ["serve", "dispose", "position", "requisite", "digest", "natal", "mature"],
    "auto": ["didactic", "graph", "mate", "chrome", "centric", "complete", "encoder"],
    "inter": ["twine", "connected", "dependent", "galactic", "action", "stellar"],
    "un": ["happy", "eaten", "usual", "fold", "certain", "aware", "settled"],
}

_NESS = ["heaviness", "sadness", "softness", "crabbiness", "lightness", "artiness",
         "edginess", "happiness", "silliness", "kindness", "emptiness", "dryness",
         "tidiness", "darkness", "fullness", "readiness"]

_SENTENCES = [("Look at the bright sky.", -2), ("His expression went dark.", -1),
              ("The bread got hard after sitting out.", 3),
              ("The butter got soft in the sun.", 3),
              ("Her eyes were light blue.", -2),
              ("The morning fog made everything damp with mist.", -3),
              ("He cut the fence pickets short by mistake.", 5),
              ("Charles made weak crying noises.", 2),
              ("The black oil got on the white dog.", 1),
              ("I need to make that bright.", -1),
              ("It got dark as the sun set.", 2)]


def _gen(r):
    prefix = r.choice(list(_GROUPS))
    vocab_words = [prefix, *r.sample(_GROUPS[prefix], r.randint(2, 5))]
    sentence, index = r.choice(_SENTENCES)
    return r.choice(_ROOTS), vocab_words, r.choice(_NESS), sentence, index


def _reference():
    def add_prefix_un(word):
        return "un" + word

    def make_word_groups(vocab_words):
        joiner = " :: " + vocab_words[0]
        return joiner.join(vocab_words)

    def remove_suffix_ness(word):
        root = word[:-4]
        return root[:-1] + "y" if root[-1] == "i" else root

    def adjective_to_verb(sentence, index):
        word = sentence.split()[index]
        return (word[:-1] if word[-1] == "." else word) + "en"

    return {"add_prefix_un": add_prefix_un, "make_word_groups": make_word_groups,
            "remove_suffix_ness": remove_suffix_ness, "adjective_to_verb": adjective_to_verb}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        word, vocab_words, ness_word, sentence, index = _gen(r)
        assert (got["add_prefix_un"](word)
                == want["add_prefix_un"](word)), f"add_prefix_un({word!r})"
        assert (got["make_word_groups"](list(vocab_words))
                == want["make_word_groups"](list(vocab_words))), f"make_word_groups({vocab_words!r})"
        assert (got["remove_suffix_ness"](ness_word)
                == want["remove_suffix_ness"](ness_word)), f"remove_suffix_ness({ness_word!r})"
        assert (got["adjective_to_verb"](sentence, index)
                == want["adjective_to_verb"](sentence, index)), \
            f"adjective_to_verb({sentence!r}, {index})"

    # canonical cases from exercism's strings_test.py
    assert got["add_prefix_un"]("happy") == "unhappy"
    assert got["add_prefix_un"]("manageable") == "unmanageable"
    assert got["make_word_groups"](["en", "circle", "fold", "close", "joy", "lighten",
                                    "tangle", "able", "code", "culture"]) == (
        "en :: encircle :: enfold :: enclose :: enjoy :: enlighten :: entangle :: "
        "enable :: encode :: enculture")
    assert got["make_word_groups"](["auto", "didactic", "graph", "mate"]) == (
        "auto :: autodidactic :: autograph :: automate")
    for word, root in [("heaviness", "heavy"), ("sadness", "sad"), ("softness", "soft"),
                       ("crabbiness", "crabby"), ("edginess", "edgy")]:
        assert got["remove_suffix_ness"](word) == root, f"remove_suffix_ness({word!r})"
    for sentence, index, verb in [("Look at the bright sky.", -2, "brighten"),
                                  ("His expression went dark.", -1, "darken"),
                                  ("He cut the fence pickets short by mistake.", 5, "shorten"),
                                  ("The black oil got on the white dog.", 1, "blacken")]:
        assert got["adjective_to_verb"](sentence, index) == verb, f"adjective_to_verb({sentence!r})"
