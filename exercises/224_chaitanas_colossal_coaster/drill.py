def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

_NAMES = ["Natasha", "Steve", "T'challa", "Wanda", "Rocket", "Tony", "Bruce", "Okoye",
          "Gamora", "Loki", "Peggy", "Drax", "Nebula", "Agatha", "Pepper", "Valkyrie",
          "RobotGuy", "WW", "HawkEye", "Bucky"]


def _gen(r):
    express = r.sample(_NAMES, r.randint(1, 4))
    normal = r.sample(_NAMES, r.randint(1, 4))
    queue = r.sample(_NAMES, r.randint(2, 6))
    return (express, normal, r.choice([0, 1]), r.choice(_NAMES),
            queue, r.choice(queue), r.randint(0, len(queue)))


def _reference():
    def add_me_to_the_queue(express_queue, normal_queue, ticket_type, person_name):
        queue = express_queue if ticket_type == 1 else normal_queue
        queue.append(person_name)
        return queue

    def find_my_friend(queue, friend_name):
        return queue.index(friend_name)

    def add_me_with_my_friends(queue, index, person_name):
        queue.insert(index, person_name)
        return queue

    return {"add_me_to_the_queue": add_me_to_the_queue, "find_my_friend": find_my_friend,
            "add_me_with_my_friends": add_me_with_my_friends}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        express, normal, ticket_type, person_name, queue, friend_name, index = _gen(r)
        mine, theirs = list(express), list(normal)
        joined = got["add_me_to_the_queue"](mine, theirs, ticket_type, person_name)
        assert joined == want["add_me_to_the_queue"](list(express), list(normal),
                                                     ticket_type, person_name), \
            f"add_me_to_the_queue({express}, {normal}, {ticket_type}, {person_name!r})"
        assert joined is (mine if ticket_type == 1 else theirs), \
            "add_me_to_the_queue must return the queue it was given, not a new list"

        assert (got["find_my_friend"](list(queue), friend_name)
                == want["find_my_friend"](list(queue), friend_name)), \
            f"find_my_friend({queue}, {friend_name!r})"

        line = list(queue)
        placed = got["add_me_with_my_friends"](line, index, person_name)
        assert placed == want["add_me_with_my_friends"](list(queue), index, person_name), \
            f"add_me_with_my_friends({queue}, {index}, {person_name!r})"
        assert placed is line, \
            "add_me_with_my_friends must return the queue it was given, not a new list"

    # canonical cases from exercism's list_methods_test.py
    assert (got["add_me_to_the_queue"](["Tony", "Bruce"], ["RobotGuy", "WW"], 0, "HawkEye")
            == ["RobotGuy", "WW", "HawkEye"])
    assert (got["add_me_to_the_queue"](["Tony", "Bruce"], ["RobotGuy", "WW"], 1, "RichieRich")
            == ["Tony", "Bruce", "RichieRich"])
    assert (got["add_me_to_the_queue"](["Agatha", "Pepper", "Valkyrie"], ["Drax", "Nebula"],
                                       0, "Gamora") == ["Drax", "Nebula", "Gamora"])
    guests = ["Natasha", "Steve", "Tchalla", "Wanda", "Rocket"]
    for name, expected in [("Natasha", 0), ("Steve", 1), ("Rocket", 4)]:
        assert got["find_my_friend"](list(guests), name) == expected, f"find_my_friend({name!r})"
    for index, expected in [(0, ["Bucky", "Natasha", "Steve", "Tchalla", "Wanda", "Rocket"]),
                            (1, ["Natasha", "Bucky", "Steve", "Tchalla", "Wanda", "Rocket"]),
                            (5, ["Natasha", "Steve", "Tchalla", "Wanda", "Rocket", "Bucky"])]:
        assert got["add_me_with_my_friends"](list(guests), index, "Bucky") == expected, \
            f"add_me_with_my_friends(queue, {index}, 'Bucky')"
