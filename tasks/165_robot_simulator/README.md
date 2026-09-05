---
title: class-customization — a robot that turns and advances on an infinite grid
difficulty: medium
tier: advanced
minutes: 20
prereqs: [115]
tags: [class-customization, decorators, dict-methods]
source: exercism/python practice/robot-simulator (MIT, adapted)
---
# class-customization — a robot that turns and advances on an infinite grid

*robot-simulator — keep the facing as a number, and both turns become one line of arithmetic.*

## Read first
- [A first look at classes](https://devdocs.io/python~3.14/tutorial/classes#a-first-look-at-classes) — `__init__`, `self`, and methods that change the instance rather than return a new one
- [`property`](https://devdocs.io/python~3.14/library/functions#property) — how `.coordinates` can be computed on access instead of stored and kept in sync
- [`%` on integers](https://devdocs.io/python~3.14/reference/expressions#binary-arithmetic-operations) — `% 4` keeps a facing inside `0..3`, and Python's `%` gives a non-negative answer even for `-1`
- [Dictionaries](https://devdocs.io/python~3.14/tutorial/datastructures#dictionaries) — a mapping is a neat stand-in for a chain of `if`s, both for "which letter is this" and for "which way does this facing move"

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Before a warehouse robot is allowed anywhere near a warehouse, the firmware that reads its command stream is replayed against a model of the robot in software: feed in `"RAALAL"`, check it ends up where the plan said. That model has to be cheap enough to run thousands of times in a test suite, so it is not a robot at all — it is a position, a facing, and a rule for what each letter does. Plotters, turtle graphics, CNC paths, the movement code in a game, a cursor walking a document: same object every time. The part worth getting right is the facing, because the obvious representation — four names, or four strings — turns "turn left" into a table of special cases, and the right one turns it into a remainder.

## Instructions
Write a robot simulator.

A robot factory's test facility needs a program to verify robot movements.

The robots have three possible movements:

- turn right
- turn left
- advance

Robots are placed on a hypothetical infinite grid, facing a particular direction (north, east, south, or west) at a set of {x,y} coordinates,
e.g., {3,8}, with coordinates increasing to the north and east.

The robot then receives a number of instructions, at which point the testing facility verifies the robot's new position, and in which direction it is pointing.

- The letter-string "RAALAL" means:
  - Turn right
  - Advance twice
  - Turn left
  - Advance once
  - Turn left yet again
- Say a robot starts at {7, 3} facing north.
  Then running this stream of instructions should leave it at {9, 4} facing west.

## You get
Nothing to start — you return a **class**. The four compass names are **already written for you** at the top of `task.py`, marked `# given — do not edit`:

```python
NORTH, EAST, SOUTH, WEST = range(4)    # 0, 1, 2, 3 — clockwise
```

The grader builds robots as `Robot(direction, x_pos, y_pos)`, e.g. `Robot(NORTH, 7, 3)` or `Robot(SOUTH, -1, -1)`, and then calls `.move(commands)` with a string like `"RAALAL"`.

> [!NOTE]
> Exercism's stub is a `class Robot` in `robot_simulator.py`, and there you choose the four constants' values yourself. Here the entry point is `solve()`, which takes **no arguments** and returns the class itself — not an instance — and the four constants are given so that you and the grader agree on what `.direction` means.

## You return
The class. The grader uses it like this:

```python
Robot = solve()
robot = Robot(NORTH, 7, 3)
robot.move("RAALAL")
robot.coordinates     # -> (9, 4)
robot.direction       # -> WEST
```

| member | is | behaviour |
| --- | --- | --- |
| `Robot(direction=NORTH, x_pos=0, y_pos=0)` | constructor | a robot placed at `(x_pos, y_pos)` facing `direction` |
| `.direction` | attribute or property | the facing right now — one of `NORTH`, `EAST`, `SOUTH`, `WEST` |
| `.coordinates` | attribute or property | a `tuple` `(x, y)` of where the robot is right now |
| `.move(commands)` | method | run every letter of `commands`, left to right; returns nothing |

## Rules
- keep the three parameter names and the three defaults: the grader calls `Robot()` with no arguments and expects the origin, facing north
- the grid is infinite in both directions, so both coordinates may be negative and there is nothing to clamp
- north increases `y`, south decreases `y`, east increases `x`, west decreases `x`
- `commands` contains only the letters `A` (advance one square in the current facing), `L` (turn a quarter turn left) and `R` (turn a quarter turn right) — nothing else is ever passed in, and an empty string is allowed and does nothing
- turning never changes the coordinates and advancing never changes the facing
- `.coordinates` is a `tuple`, not a list — the grader compares it with `==` against `(9, 4)`
- `.direction` is one of the four given names, i.e. one of `0, 1, 2, 3`, never the string `"north"`
- a robot keeps its state between calls: two `move("A")` calls and one `move("AA")` leave it in the same place

```python
Robot = solve()
robot = Robot(NORTH, 0, 0)
robot.move("LAAARALA")
robot.coordinates     # -> (-4, 1)
robot.direction       # -> WEST

robot = Robot(EAST, 2, -7)
robot.move("RRAAAAALA")
robot.coordinates     # -> (-3, -8)
robot.direction       # -> SOUTH
```

> [!WARNING]
> The given constants run **clockwise**: `NORTH, EAST, SOUTH, WEST` is `0, 1, 2, 3`. Turning right is therefore the step that increases the number and turning left the one that decreases it — note that Exercism's stub declares them `EAST, NORTH, WEST, SOUTH`, which runs anticlockwise; the order here is not that.

## Hints
### Hint 1
There are only two pieces of state — where the robot is and which way it faces — and three commands that each touch exactly one of them. Before writing anything, decide how you will represent the facing, because that single choice decides whether the two turns are one line each or twelve lines of `if`. The constants are given to you as `0, 1, 2, 3` in clockwise order for a reason.

### Hint 2
With the facing held as a number `0..3` clockwise, a right turn adds one and a left turn subtracts one, each followed by `% 4` so the value stays in range — and Python's `%` already returns a non-negative result, so no `if` is needed for the left turn off `NORTH`. Advancing is the only command that needs to know *which* facing it has: rather than four branches, pair each facing with the pair of numbers to add to `x` and `y`, look that pair up, and add. `move` then reads each character in turn and dispatches — a mapping from letter to the method that handles it works nicely and keeps `move` to two lines.

### Hint 3
Different data, same shape — a thermostat with a mode button that cycles through four settings:

```python
MODES = ("off", "heat", "cool", "fan")

class Thermostat:
    def __init__(self, mode=0, degrees=20):
        self.mode = mode
        self.degrees = degrees

    @property
    def display(self):
        return (MODES[self.mode], self.degrees)

    def next_mode(self):
        self.mode = (self.mode + 1) % 4

    def warmer(self):
        self.degrees += 1

    def cooler(self):
        self.degrees -= 1

    def press(self, buttons):
        actions = {"M": self.next_mode, "+": self.warmer, "-": self.cooler}
        for button in buttons:
            actions[button]()

panel = Thermostat()
panel.press("MM++")
panel.display        # -> ("cool", 22)
```

Three things to lift from this. The cycling setting is a number with a `% 4` on it, and the readable names sit in a tuple beside it rather than in the state. `display` is a `@property`, so it can never fall out of step with the two values it is built from. And `press` does not know what any button does — it looks the letter up and calls whatever it finds, which is why adding a fourth button would not touch it at all.
