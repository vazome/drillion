def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

from _lib import rng


def _gen(r):
    return r.randint(-20, 20), r.randint(-20, 20), r.randint(1, 6)


def _reference():
    class Alien:
        total_aliens_created = 0

        def __init__(self, x_coordinate, y_coordinate):
            Alien.total_aliens_created += 1
            self.x_coordinate = x_coordinate
            self.y_coordinate = y_coordinate
            self.health = 3

        def hit(self):
            self.health -= 1

        def is_alive(self):
            return self.health > 0

        def teleport(self, new_x_coordinate, new_y_coordinate):
            self.x_coordinate = new_x_coordinate
            self.y_coordinate = new_y_coordinate

        def collision_detection(self, other):
            pass

    return Alien


def test_solve():
    r = rng()
    Alien = solve()
    assert inspect.isclass(Alien), "solve() must return the Alien class itself, not an instance"
    Reference = _reference()

    for _ in range(5):
        x_coordinate, y_coordinate, hits = _gen(r)
        alien = Alien(x_coordinate, y_coordinate)
        want = Reference(x_coordinate, y_coordinate)
        assert (alien.x_coordinate, alien.y_coordinate) == (x_coordinate, y_coordinate), (
            f"Alien({x_coordinate}, {y_coordinate}) sits at "
            f"{(alien.x_coordinate, alien.y_coordinate)}")
        assert alien.health == 3, f"a new Alien starts at health 3, got {alien.health}"

        for blow in range(1, hits + 1):
            alien.hit()
            want.hit()
            assert alien.is_alive() == (alien.health > 0), (
                f"after {blow} hit(s) health is {alien.health} but "
                f"is_alive() said {alien.is_alive()}")
        assert alien.health in (want.health, max(0, want.health)), (
            f"after {hits} hit(s) health is {alien.health}, expected "
            f"{want.health} (or {max(0, want.health)} if you stop at zero)")

        new_x, new_y = r.randint(-20, 20), r.randint(-20, 20)
        alien.teleport(new_x, new_y)
        assert (alien.x_coordinate, alien.y_coordinate) == (new_x, new_y), (
            f"teleport({new_x}, {new_y}) left the alien at "
            f"{(alien.x_coordinate, alien.y_coordinate)}")
        assert alien.collision_detection(Alien(new_x, new_y)) is None, (
            "collision_detection() must take one argument and return None")

    # health is per alien, the counter is per class
    one, two = Alien(-8, -1), Alien(2, 5)
    assert one.x_coordinate != two.x_coordinate, "each alien keeps its own x_coordinate"
    assert one.y_coordinate != two.y_coordinate, "each alien keeps its own y_coordinate"
    one.hit()
    assert one.health != two.health, (
        "hitting one alien changed the other's health — is health a class attribute?")

    Alien.total_aliens_created = 0
    aliens = [Alien(-2, 6)]
    assert aliens[0].total_aliens_created == 1, (
        f"one alien built, total_aliens_created is {aliens[0].total_aliens_created}")
    aliens.append(Alien(3, 5))
    aliens.append(Alien(-5, -5))
    assert [alien.total_aliens_created for alien in aliens] == [3, 3, 3], (
        "every alien must report the same total_aliens_created")
    assert Alien.total_aliens_created == 3, "the counter must be readable from the class too"

    # canonical cases from exercism's classes_test.py
    alien = Alien(2, -1)
    assert (alien.x_coordinate, alien.y_coordinate) == (2, -1)
    assert Alien(0, 0).health == 3
    for iterations, expected in [(1, (2,)), (2, (1,)), (3, (0,)), (4, (0, -1)),
                                 (5, (0, -2)), (6, (0, -3))]:
        target = Alien(2, 2)
        for _ in range(iterations):
            target.hit()
        assert target.health in expected, (
            f"hit() called {iterations} time(s) on a new Alien left health "
            f"{target.health}, expected one of {expected}")
    mover = Alien(0, 0)
    mover.teleport(-1, -4)
    assert (mover.x_coordinate, mover.y_coordinate) == (-1, -4)
    assert Alien(7, 3).collision_detection(Alien(7, 2)) is None
