def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from enum import Enum

from _lib import rng

_CODES = ["TRC", "DBG", "INF", "WRN", "ERR", "FTL", "UKN"]
_BOGUS = ["XYZ", "CRT", "NTC", "ALT", "EMG", "VRB", "FYI"]
_TEXTS = ["File deleted", "Stack overflow", "File is being overwritten",
          "Some Random Log", "Overly specific, out of context message",
          "Disk 91% full", "Connection reset by peer", "This is a warning",
          "Cache warmed in 12ms", "Retrying in 5s"]
_ORDER = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "FATAL", "UNKNOWN"]


def _gen(r):
    code = r.choice(_CODES) if r.random() < 0.75 else r.choice(_BOGUS)
    text = r.choice(_TEXTS)
    return f"[{code}]: {text}", r.choice(_ORDER), text


def _reference():
    class LogLevel(Enum):
        TRACE = "TRC"
        DEBUG = "DBG"
        INFO = "INF"
        WARNING = "WRN"
        WARN = "WRN"  # noqa: PIE796 — the alias is the point of task 4
        ERROR = "ERR"
        FATAL = "FTL"
        UNKNOWN = "UKN"

    codes = {"TRACE": 0, "DEBUG": 1, "INFO": 4, "WARNING": 5,
             "ERROR": 6, "FATAL": 7, "UNKNOWN": 42}

    def parse_log_level(message):
        code = message.split(":")[0][1:-1]
        if code in [level.value for level in LogLevel]:
            return LogLevel(code)
        return LogLevel("UKN")

    def convert_to_short_log(log_level, message):
        return f"{codes[log_level.name]}:{message}"

    def get_warn_alias():
        return LogLevel("WRN")

    def get_members():
        return [(member.name, member.value) for member in LogLevel]

    return {"LogLevel": LogLevel, "parse_log_level": parse_log_level,
            "convert_to_short_log": convert_to_short_log,
            "get_warn_alias": get_warn_alias, "get_members": get_members}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    LogLevel, WantLevel = got["LogLevel"], want["LogLevel"]
    assert isinstance(LogLevel, type) and issubclass(LogLevel, Enum), (
        "solve()['LogLevel'] must be an Enum subclass, not a member or an instance")

    for _ in range(6):
        line, member_name, text = _gen(r)
        parsed = got["parse_log_level"](line)
        expected = want["parse_log_level"](line)
        assert parsed is LogLevel[expected.name], f"parse_log_level({line!r}) -> {parsed!r}"
        assert (parsed.name, parsed.value) == (expected.name, expected.value), (
            f"parse_log_level({line!r}) -> {parsed!r}")
        assert (got["convert_to_short_log"](LogLevel[member_name], text)
                == want["convert_to_short_log"](WantLevel[member_name], text)), (
            f"convert_to_short_log(LogLevel.{member_name}, {text!r})")

    assert got["get_members"]() == want["get_members"](), "get_members()"
    assert got["get_warn_alias"]() is LogLevel["WARNING"], (
        "get_warn_alias() must return the alias of WARNING, which IS WARNING")

    # canonical cases from exercism's enums_test.py
    assert got["parse_log_level"]("[INF]: File deleted") is LogLevel.INFO
    assert got["parse_log_level"]("[WRN]: File is being overwritten") is LogLevel.WARNING
    assert got["parse_log_level"]("[ERR]: Some Random Log") is LogLevel.ERROR
    assert got["parse_log_level"]("[XYZ]: Some Random Log") is LogLevel.UNKNOWN
    assert got["convert_to_short_log"](LogLevel.ERROR, "Stack overflow") == "6:Stack overflow"
    assert (got["convert_to_short_log"](LogLevel.WARNING, "This is a warning")
            == "5:This is a warning")
    assert got["get_warn_alias"]() is LogLevel.WARN
    assert got["get_members"]() == [("TRACE", "TRC"), ("DEBUG", "DBG"), ("INFO", "INF"),
                                    ("WARNING", "WRN"), ("ERROR", "ERR"), ("FATAL", "FTL"),
                                    ("UNKNOWN", "UKN")]
