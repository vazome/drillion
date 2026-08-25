"""print in a daemon has no level, no timestamp and nowhere to go but stdout."""

import logging

from _lib import rng

META = {"topic": 38, "title": "logging — levels, a formatter, a custom handler",
        "tier": 3, "minutes": 18, "prereqs": [], "tags": ["stdlib-ops"]}


def solve(name, level, messages):
    """WHY: A background service writes hundreds of messages a minute. In
    production the operators want only warnings and errors; while debugging
    they want everything — and they want to switch between the two with one
    setting, not a code change. The messages must also go somewhere you
    control (a file, a log system, or here a plain list the test can
    inspect) in one consistent format. You wire up one such logger.

    YOU GET: `name` — a string naming the logger, like "drill38.0.solve".
    The test creates it and hands it to you; you never build it yourself.

    YOU GET: `level` — a whole number meaning "keep messages at this
    severity or higher", like logging.WARNING.

    YOU GET: `messages` — a list of (severity name, text) pairs, like
    [("INFO", "starting"), ("ERROR", "disk full")].

    YOU RETURN: a list of strings — the formatted messages that got past the
    level filter, in order, like ["ERROR:disk full"].

    ─── exact rules ───
    Set up one logger and capture what it emits, printing nothing.

        name      a unique logger name, e.g. "drill38.0.solve"
        level     a level as an int, e.g. logging.WARNING
        messages  list of (levelname, text) pairs, e.g.
                  [("INFO", "starting"), ("ERROR", "disk full")]

    Build it in this order:

      1. A handler class of your own: subclass logging.Handler, and in its
         emit(self, record) append self.format(record) to a list.
      2. Give the handler logging.Formatter("%(levelname)s:%(message)s").
      3. Get the logger by name, set its level, attach the handler, and set
         .propagate = False so records stop here instead of climbing to the
         root logger and being printed twice by whatever else is running.
      4. Log every message at its own level, in order.
      5. Return the list of formatted strings.

        level=logging.WARNING, [("INFO", "hi"), ("ERROR", "boom")]
          ->  ["ERROR:boom"]

    Only records at or above the logger's level survive; the rest never reach
    the handler. That is the point of levels — the same daemon runs quiet in
    production and chatty at DEBUG without touching a line of code.
    """
    raise NotImplementedError


HINTS = [
    ("Three separate objects, and mixing them up is the usual beginner failure. "
    "The logger is a named thing you fetch, and it decides which records pass "
    "its level. The handler decides where a surviving record goes — a file, "
    "syslog, or in this case a list. The formatter decides what it looks like "
    "as text. Loggers are also a tree: by default a record travels up to the "
    "root and gets emitted again there, which is why one flag exists to stop "
    "it."),
    ("Subclass logging.Handler and override emit(self, record); inside, "
    "self.format(record) gives you the formatted string. Then: "
    "logging.getLogger(name), .setLevel(level), handler.setFormatter(...), "
    ".addHandler(handler), .propagate = False. To log at a level you only know "
    "as a string, getattr(logging, 'INFO') gives you the int and "
    "logger.log(int, text) takes it."),
    ("Different data, same wiring:\n"
    "    import logging\n"
    "    seen = []\n"
    "\n"
    "    class ListHandler(logging.Handler):\n"
    "        def emit(self, record):\n"
    "            seen.append(self.format(record))\n"
    "\n"
    "    h = ListHandler()\n"
    "    h.setFormatter(logging.Formatter('%(levelname)s|%(message)s'))\n"
    "    log = logging.getLogger('demo.backup')\n"
    "    log.setLevel(logging.INFO)\n"
    "    log.propagate = False\n"
    "    log.addHandler(h)\n"
    "    log.debug('opening socket')\n"
    "    log.log(getattr(logging, 'WARNING'), 'slow disk')\n"
    "    print(seen)          # ['WARNING|slow disk']\n"
    "The debug line was dropped by the logger's level, not by the handler."),
]


# ─────────────────────────────  below here is the machinery  ──────────────

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
