def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_TITLES = ["my hobbies", "canopy", "fish are cold blooded", "the life of a mayfly",
           "why snails sleep", "a very short paper about moss", "elephants and jumping",
           "how fittonia drink"]

_SENTENCES = ["I like to hike, bake, and read.", "Fittonia are nice",
              "Snails can sleep for 3 years.", "Animals are cool.",
              "A rolling stone gathers no moss", "Elephants can't jump.",
              "The canopy is full of small birds", "I bake good cakes.",
              "Moss is nice and soft"]

_PADS = ["", " ", "   ", "\t", "  \t ", "\n  "]

_SWAPS = [("good", "amazing"), ("cool", "awesome"), ("nice", "delightful"),
          ("small", "tiny"), ("sleep", "rest"), ("bake", "make"), ("moss", "lichen")]


def _gen(r):
    spaced = r.choice(_PADS) + r.choice(_SENTENCES) + r.choice(_PADS)
    old_word, new_word = r.choice(_SWAPS)
    return (r.choice(_TITLES), r.choice(_SENTENCES), spaced,
            r.choice(_SENTENCES), old_word, new_word)


def _reference():
    def capitalize_title(title):
        return title.title()

    def check_sentence_ending(sentence):
        return sentence.endswith(".")

    def clean_up_spacing(sentence):
        return sentence.strip()

    def replace_word_choice(sentence, old_word, new_word):
        return sentence.replace(old_word, new_word)

    return {"capitalize_title": capitalize_title,
            "check_sentence_ending": check_sentence_ending,
            "clean_up_spacing": clean_up_spacing,
            "replace_word_choice": replace_word_choice}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        title, ending, spaced, sentence, old_word, new_word = _gen(r)
        assert (got["capitalize_title"](title)
                == want["capitalize_title"](title)), f"capitalize_title({title!r})"
        assert (got["check_sentence_ending"](ending)
                == want["check_sentence_ending"](ending)), f"check_sentence_ending({ending!r})"
        assert (got["clean_up_spacing"](spaced)
                == want["clean_up_spacing"](spaced)), f"clean_up_spacing({spaced!r})"
        assert (got["replace_word_choice"](sentence, old_word, new_word)
                == want["replace_word_choice"](sentence, old_word, new_word)), \
            f"replace_word_choice({sentence!r}, {old_word!r}, {new_word!r})"

    # canonical cases from exercism's string_methods_test.py
    assert got["capitalize_title"]("canopy") == "Canopy"
    assert got["capitalize_title"]("fish are cold blooded") == "Fish Are Cold Blooded"
    assert got["check_sentence_ending"]("Snails can sleep for 3 years.") is True
    assert got["check_sentence_ending"]("Fittonia are nice") is False
    assert (got["clean_up_spacing"]("  A rolling stone gathers no moss")
            == "A rolling stone gathers no moss")
    assert got["clean_up_spacing"]("  Elephants can't jump.  ") == "Elephants can't jump."
    assert (got["replace_word_choice"]("Animals are cool.", "cool", "awesome")
            == "Animals are awesome.")
    assert (got["replace_word_choice"]("Animals are cool.", "small", "tiny")
            == "Animals are cool.")
