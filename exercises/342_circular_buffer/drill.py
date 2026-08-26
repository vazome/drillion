# given — do not edit
class BufferFullException(BufferError):
    """Raised when a write is attempted and every slot already holds an unread item."""


class BufferEmptyException(BufferError):
    """Raised when a read is attempted and no slot holds an unread item."""


def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import inspect

import pytest
from _lib import rng


def _gen(r):
    capacity = r.randint(1, 5)
    operations = r.choices(["write", "read", "overwrite", "clear"],
                           weights=[5, 4, 3, 1], k=r.randint(8, 16))
    return capacity, [(name, r.choice("123456789abcdef")) for name in operations]


def _apply(buffer, operation, data):
    if operation == "read":
        return buffer.read()
    if operation == "clear":
        buffer.clear()
    elif operation == "write":
        buffer.write(data)
    else:
        buffer.overwrite(data)
    return None


def _outcome(buffer, operation, data):
    try:
        return ("ok", _apply(buffer, operation, data))
    except BufferError as err:
        return ("error", type(err), err.args[0] if err.args else None)


def _reference():
    class CircularBuffer:
        def __init__(self, capacity):
            self.capacity = capacity
            self.slots = [None] * capacity
            self.oldest = 0
            self.unread = 0

        def clear(self):
            self.slots = [None] * self.capacity
            self.oldest = 0
            self.unread = 0

        def read(self):
            if self.unread == 0:
                raise BufferEmptyException("Circular buffer is empty")
            data = self.slots[self.oldest]
            self.oldest = (self.oldest + 1) % self.capacity
            self.unread -= 1
            return data

        def write(self, data):
            if self.unread == self.capacity:
                raise BufferFullException("Circular buffer is full")
            self.slots[(self.oldest + self.unread) % self.capacity] = data
            self.unread += 1

        def overwrite(self, data):
            if self.unread == self.capacity:
                self.slots[self.oldest] = data
                self.oldest = (self.oldest + 1) % self.capacity
            else:
                self.write(data)

    return CircularBuffer


def test_solve():
    r = rng()
    CircularBuffer = solve()
    assert inspect.isclass(CircularBuffer), "solve() must return a class"
    Reference = _reference()
    for _ in range(5):
        capacity, script = _gen(r)
        mine, theirs = CircularBuffer(capacity), Reference(capacity)
        for step, (operation, data) in enumerate(script, start=1):
            assert _outcome(mine, operation, data) == _outcome(theirs, operation, data), \
                f"CircularBuffer({capacity}): {operation}({data!r}) after {script[:step - 1]!r}"

    # canonical cases (exercism/python practice/circular-buffer)
    buffer = CircularBuffer(1)
    with pytest.raises(BufferEmptyException, match=r"^Circular buffer is empty$"):
        buffer.read()
    buffer.write("1")
    with pytest.raises(BufferFullException, match=r"^Circular buffer is full$"):
        buffer.write("2")
    assert buffer.read() == "1"

    buffer = CircularBuffer(3)
    buffer.write("1")
    buffer.write("2")
    assert buffer.read() == "1"
    buffer.write("3")
    assert buffer.read() == "2"
    assert buffer.read() == "3"

    buffer = CircularBuffer(3)
    for item in "123":
        buffer.write(item)
    assert buffer.read() == "1"
    buffer.write("4")
    buffer.overwrite("5")
    assert buffer.read() == "3"
    assert buffer.read() == "4"
    assert buffer.read() == "5"

    buffer = CircularBuffer(1)
    buffer.write("1")
    buffer.clear()
    with pytest.raises(BufferEmptyException, match=r"^Circular buffer is empty$"):
        buffer.read()
    buffer.write("2")
    assert buffer.read() == "2"

    buffer = CircularBuffer(2)
    buffer.clear()
    buffer.write("1")
    buffer.write("2")
    buffer.overwrite("3")
    buffer.overwrite("4")
    assert buffer.read() == "3"
    assert buffer.read() == "4"
    with pytest.raises(BufferEmptyException, match=r"^Circular buffer is empty$"):
        buffer.read()

    buffer = CircularBuffer(2)
    buffer.write("1")
    buffer.overwrite("2")
    assert buffer.read() == "1"
    assert buffer.read() == "2"
