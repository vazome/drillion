def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from typing import ClassVar

import pytest
from _lib import rng

_EVENTS = ["image.uploaded", "user.created", "order.paid", "file.scanned", "mail.bounced"]


def _gen(r):
    names = r.sample(_EVENTS, r.randint(1, 4))
    return [(e, f"{r.choice(['cat', 'ada', 'batch'])}-{r.randint(10, 99)}") for e in names]


def _reference():
    class Handler:
        registry: ClassVar[dict] = {}

        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)
            event = cls.__dict__.get("event")
            if not isinstance(event, str) or not event:
                raise TypeError(f"{cls.__name__} must set its own event")
            if not callable(getattr(cls, "handle", None)):
                raise TypeError(f"{cls.__name__} must define handle()")
            if event in cls.registry:
                raise TypeError(f"{event!r} is already handled by {cls.registry[event].__name__}")
            cls.registry[event] = cls

        @classmethod
        def dispatch(cls, event, payload):
            if event not in cls.registry:
                raise KeyError(event)
            return cls.registry[event]().handle(payload)

    return Handler


def _populate(base, events):
    for event in events:
        # a class statement per event: the registration happens right here
        type(f"H{len(base.registry)}", (base,), {"event": event, "handle": lambda self, p, e=event: f"{e}:{p}"})


def test_solve():
    r = rng()

    for _ in range(6):
        pairs = _gen(r)
        events = [e for e, _ in pairs]
        mine, theirs = solve(), _reference()
        _populate(mine, events)
        _populate(theirs, events)
        assert sorted(mine.registry) == sorted(theirs.registry), f"registry for {events}"
        for event, payload in pairs:
            assert mine.dispatch(event, payload) == theirs.dispatch(event, payload), f"{event}"

    handler = solve()
    assert handler.registry == {}, "the base itself must not be registered"

    class Resize(handler):
        event = "image.uploaded"

        def handle(self, payload):
            return f"resizing {payload}"

    assert handler.registry == {"image.uploaded": Resize}, "writing the class is what registers it"
    assert handler.dispatch("image.uploaded", "cat.png") == "resizing cat.png"
    with pytest.raises(KeyError):
        handler.dispatch("nope", "x")

    # checking in __init__ would let every one of these classes finish being defined
    with pytest.raises(TypeError):

        class NoEvent(handler):
            def handle(self, payload):
                return payload

    with pytest.raises(TypeError):

        class EmptyEvent(handler):
            event = ""

            def handle(self, payload):
                return payload

    with pytest.raises(TypeError):

        class NoHandle(handler):
            event = "user.created"

    with pytest.raises(TypeError):

        class Duplicate(handler):
            event = "image.uploaded"

            def handle(self, payload):
                return payload

    assert handler.registry == {"image.uploaded": Resize}, "a rejected class must not be registered"

    # a grandchild inherits `event`, and inheriting is not naming
    with pytest.raises(TypeError):

        class Rescale(Resize):
            pass

    class Thumbnail(Resize):
        event = "image.thumbnailed"

    assert handler.registry["image.thumbnailed"] is Thumbnail, "a grandchild that names its own event"
    assert "__init_subclass__" in vars(handler), "the hook belongs on the base"
