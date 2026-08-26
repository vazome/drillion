def solve(limit):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    roll = r.random()
    if roll < 0.20:
        return r.randint(0, 15)
    if roll < 0.60:
        return r.randint(15, 300)
    return r.randint(300, 3000)


def _reference(limit):
    if limit < 2:
        return []
    unmarked = [True] * (limit + 1)
    unmarked[0] = unmarked[1] = False
    number = 2
    while number * number <= limit:
        if unmarked[number]:
            for multiple in range(number * number, limit + 1, number):
                unmarked[multiple] = False
        number += 1
    return [value for value, is_prime in enumerate(unmarked) if is_prime]


def test_solve():
    r = rng()
    for _ in range(6):
        limit = _gen(r)
        assert solve(limit) == _reference(limit), f"limit {limit!r}"

    # canonical cases (exercism/python practice/sieve)
    assert solve(1) == []
    assert solve(2) == [2]
    assert solve(10) == [2, 3, 5, 7]
    assert solve(13) == [2, 3, 5, 7, 11, 13]
    assert solve(1000) == [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61,
        67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137,
        139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
        211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277,
        281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359,
        367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439,
        443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521,
        523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607,
        613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683,
        691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773,
        787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863,
        877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967,
        971, 977, 983, 991, 997]
