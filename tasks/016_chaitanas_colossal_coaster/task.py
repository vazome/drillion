def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_NAMES = ["Natasha", "Steve", "Ultron", "Wanda", "Rocket", "Tony", "Bruce", "Okoye",
          "Gamora", "Loki", "Peggy", "Drax", "Nebula", "Agatha", "Pepper", "Valkyrie",
          "Eltran", "Bucky"]


def _gen(r):
    queue = [r.choice(_NAMES) for _ in range(r.randint(3, 8))]
    return queue, r.choice(queue), r.choice(_NAMES)


def _reference():
    def remove_the_mean_person(queue, person_name):
        queue.remove(person_name)
        return queue

    def how_many_namefellows(queue, person_name):
        return queue.count(person_name)

    def remove_the_last_person(queue):
        return queue.pop()

    def sorted_names(queue):
        roster = queue[:]
        roster.sort()
        return roster

    return {"remove_the_mean_person": remove_the_mean_person,
            "how_many_namefellows": how_many_namefellows,
            "remove_the_last_person": remove_the_last_person,
            "sorted_names": sorted_names}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        queue, mean_person, counted = _gen(r)

        line = list(queue)
        thinned = got["remove_the_mean_person"](line, mean_person)
        assert thinned == want["remove_the_mean_person"](list(queue), mean_person), \
            f"remove_the_mean_person({queue}, {mean_person!r})"
        assert thinned is line, \
            "remove_the_mean_person must return the queue it was given, not a new list"

        assert (got["how_many_namefellows"](list(queue), counted)
                == want["how_many_namefellows"](list(queue), counted)), \
            f"how_many_namefellows({queue}, {counted!r})"

        line = list(queue)
        assert (got["remove_the_last_person"](line)
                == want["remove_the_last_person"](list(queue))), f"remove_the_last_person({queue})"
        assert line == queue[:-1], f"remove_the_last_person must shorten the queue: {queue}"

        line = list(queue)
        roster = got["sorted_names"](line)
        assert roster == want["sorted_names"](list(queue)), f"sorted_names({queue})"
        assert roster is not line, "sorted_names must return a new list, not the queue itself"
        assert line == queue, f"sorted_names must leave the queue in its original order: {queue}"

    # canonical cases from exercism's list_methods_test.py
    for queue, mean_person, expected in [
            (["Natasha", "Steve", "Ultron", "Wanda", "Rocket"], "Ultron",
             ["Natasha", "Steve", "Wanda", "Rocket"]),
            (["Natasha", "Steve", "Wanda", "Rocket", "Ultron"], "Rocket",
             ["Natasha", "Steve", "Wanda", "Ultron"]),
            (["Ultron", "Natasha", "Steve", "Wanda", "Rocket"], "Steve",
             ["Ultron", "Natasha", "Wanda", "Rocket"])]:
        assert got["remove_the_mean_person"](list(queue), mean_person) == expected, \
            f"remove_the_mean_person({queue}, {mean_person!r})"
    for queue, name, expected in [
            (["Natasha", "Steve", "Ultron", "Natasha", "Rocket"], "Bucky", 0),
            (["Natasha", "Steve", "Ultron", "Rocket"], "Natasha", 1),
            (["Natasha", "Steve", "Ultron", "Natasha", "Rocket"], "Natasha", 2)]:
        assert got["how_many_namefellows"](list(queue), name) == expected, \
            f"how_many_namefellows({queue}, {name!r})"
    queue = ["Natasha", "Steve", "Ultron", "Natasha", "Rocket"]
    assert got["remove_the_last_person"](queue) == "Rocket"
    assert queue == ["Natasha", "Steve", "Ultron", "Natasha"]
    queue = ["Steve", "Ultron", "Natasha", "Rocket"]
    assert got["sorted_names"](queue) == ["Natasha", "Rocket", "Steve", "Ultron"]
    assert queue == ["Steve", "Ultron", "Natasha", "Rocket"]
    assert (got["sorted_names"](["Gamora", "Loki", "Tony", "Peggy", "Okoye"])
            == ["Gamora", "Loki", "Okoye", "Peggy", "Tony"])
