def solve(name: str, level: int, messages: list[tuple[str, str]]):
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import logging

from _lib import rng

_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def _gen(r):
    """(level_int, messages)."""
    level = getattr(logging, r.choice(_LEVELS))
    verbs = ["starting", "draining", "retrying", "evicting", "reloading",
             "leaking", "timing out"]
    nouns = ["pod", "node", "queue", "socket", "cache", "volume"]
    messages = [(r.choice(_LEVELS),
                 f"{r.choice(verbs)} {r.choice(nouns)}-{r.randint(1, 99)}")
                for _ in range(r.randint(4, 9))]
    return level, messages


def _reference(name, level, messages):
    captured = []

    class ListHandler(logging.Handler):
        def emit(self, record):
            captured.append(self.format(record))

    handler = ListHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    logger.addHandler(handler)
    for levelname, text in messages:
        logger.log(getattr(logging, levelname), text)
    return captured


def test_solve():
    r = rng()
    for i in range(4):
        level, messages = _gen(r)
        mine, ref = f"drill38.{i}.solve", f"drill38.{i}.ref"   # fresh loggers, no shared state
        try:
            assert solve(mine, level, list(messages)) == _reference(ref, level, messages)
            assert logging.getLogger(mine).propagate is False, "set propagate = False"
        finally:
            for name in (mine, ref):
                logging.getLogger(name).handlers.clear()
