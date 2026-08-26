# given — do not edit
NORTH, EAST, SOUTH, WEST = range(4)


def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

from _lib import rng

_NAMES = {NORTH: "NORTH", EAST: "EAST", SOUTH: "SOUTH", WEST: "WEST"}


def _gen(r):
    direction = r.choice([NORTH, EAST, SOUTH, WEST])
    x_pos, y_pos = r.randint(-25, 25), r.randint(-25, 25)
    commands = "".join(r.choices("AALR", k=r.randint(4, 14)))
    return direction, x_pos, y_pos, commands


def _reference():
    steps = {NORTH: (0, 1), EAST: (1, 0), SOUTH: (0, -1), WEST: (-1, 0)}

    class Robot:
        def __init__(self, direction=NORTH, x_pos=0, y_pos=0):
            self.direction = direction
            self.x_pos = x_pos
            self.y_pos = y_pos

        @property
        def coordinates(self):
            return (self.x_pos, self.y_pos)

        def advance(self):
            east, north = steps[self.direction]
            self.x_pos += east
            self.y_pos += north

        def turn_left(self):
            self.direction = (self.direction - 1) % 4

        def turn_right(self):
            self.direction = (self.direction + 1) % 4

        def move(self, commands):
            actions = {"A": self.advance, "L": self.turn_left, "R": self.turn_right}
            for command in commands:
                actions[command]()

    return Robot


def test_solve():
    r = rng()
    Robot = solve()
    assert inspect.isclass(Robot), "solve() must return a class"
    Reference = _reference()
    assert Robot().coordinates == (0, 0), "Robot() with no arguments starts at the origin"
    assert Robot().direction == NORTH, "Robot() with no arguments starts facing NORTH"
    for _ in range(5):
        direction, x_pos, y_pos, commands = _gen(r)
        start = f"Robot({_NAMES[direction]}, {x_pos}, {y_pos})"
        mine, theirs = Robot(direction, x_pos, y_pos), Reference(direction, x_pos, y_pos)
        assert mine.coordinates == theirs.coordinates, f"{start}.coordinates before moving"
        assert isinstance(mine.coordinates, tuple), f"{start}.coordinates must be a tuple"
        assert mine.direction == theirs.direction, f"{start}.direction before moving"
        for step, command in enumerate(commands, start=1):
            mine.move(command)
            theirs.move(command)
            done = commands[:step]
            assert mine.coordinates == theirs.coordinates, f"{start} after move({done!r})"
            assert mine.direction == theirs.direction, f"{start}.direction after move({done!r})"
        whole, expected = Robot(direction, x_pos, y_pos), Reference(direction, x_pos, y_pos)
        whole.move(commands)
        expected.move(commands)
        assert whole.coordinates == expected.coordinates, f"{start}.move({commands!r}) in one call"
        assert whole.direction == expected.direction, \
            f"{start}.move({commands!r}) in one call, direction"

    # canonical cases (exercism/python practice/robot-simulator)
    robot = Robot(SOUTH, -1, -1)
    assert robot.coordinates == (-1, -1)
    assert robot.direction == SOUTH

    robot = Robot(WEST, 0, 0)
    robot.move("L")
    assert robot.coordinates == (0, 0)
    assert robot.direction == SOUTH

    robot = Robot(NORTH, 7, 3)
    robot.move("RAALAL")
    assert robot.coordinates == (9, 4)
    assert robot.direction == WEST

    robot = Robot(NORTH, 0, 0)
    robot.move("LAAARALA")
    assert robot.coordinates == (-4, 1)
    assert robot.direction == WEST

    robot = Robot(EAST, 2, -7)
    robot.move("RRAAAAALA")
    assert robot.coordinates == (-3, -8)
    assert robot.direction == SOUTH

    robot = Robot(SOUTH, 8, 4)
    robot.move("LAAARRRALLLL")
    assert robot.coordinates == (11, 5)
    assert robot.direction == NORTH
