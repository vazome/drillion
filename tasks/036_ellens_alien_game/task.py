# given — do not edit: the finished Alien class from task 035_ellens_alien_game
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


def solve(positions: list[object] | list[tuple[int, int]]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng


def _gen(r):
    positions = [(r.randint(-9, 9), r.randint(-9, 9)) for _ in range(r.randint(0, 6))]
    if positions and r.random() < 0.4:
        positions.append(positions[0])
    return positions


def _reference(positions):
    return [Alien(position[0], position[1]) for position in positions]


def _shape(aliens):
    return [(alien.x_coordinate, alien.y_coordinate, alien.health) for alien in aliens]


def test_solve():
    r = rng()
    for _ in range(6):
        positions = _gen(r)
        got = solve(list(positions))
        assert isinstance(got, list), f"solve({positions!r}) must return a list, got {type(got)}"
        for alien in got:
            assert isinstance(alien, Alien), (
                f"solve({positions!r}) must return Alien objects, got a {type(alien)}")
        assert _shape(got) == _shape(_reference(positions)), (
            f"solve({positions!r}) -> {_shape(got)}")
        assert len({id(alien) for alien in got}) == len(positions), (
            f"solve({positions!r}) reused the same object for more than one position")

    # a fresh object per position means the class counter moves by exactly that much
    before = Alien.total_aliens_created
    solve([(1, 1), (2, 2), (3, 3)])
    assert Alien.total_aliens_created == before + 3, (
        "three positions must build three new aliens")

    # canonical cases from exercism's classes_test.py and instructions
    canonical = [(-2, 6), (1, 5), (-4, -3)]
    aliens = solve(canonical)
    assert len(aliens) == len(canonical)
    for position, alien in zip(canonical, aliens):
        assert isinstance(alien, Alien), "solve() must return a list of Alien objects"
        assert (alien.x_coordinate, alien.y_coordinate) == position
    wave = solve([(4, 7), (-1, 0)])
    assert [(alien.x_coordinate, alien.y_coordinate) for alien in wave] == [(4, 7), (-1, 0)]
    assert wave[0].health == 3
    assert solve([]) == []
