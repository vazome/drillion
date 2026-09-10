"""The failing case, as data rather than as pytest's prose.

The text of a failed run says a value was wrong. It does not say what `solve()` was called
with, and a fresh seed means the learner cannot work it out. All of it is on the frame pytest
is already holding, so this reads it there: the arguments from the failing frame's locals, and
the two sides of the comparison from the assertion hook.

The plugin is written into the run's scratch directory rather than imported from this package,
because the sandbox lets the graded child read the interpreter and `tasks/`, and an editable
install lives in neither."""

import reprlib

PLUGIN = '''
import json, os, reprlib

_short = reprlib.Repr()
_short.maxstring = _short.maxother = 400
_short.maxlist = _short.maxtuple = _short.maxset = _short.maxdict = 20
_pair = {}

# the grader's own names, and the rewriter's temporaries, are not what solve() was asked
_SKIP = ("_", "solve", "_reference", "_gen", "r", "rng", "got", "want", "mine", "theirs")


def pytest_assertrepr_compare(op, left, right):
    """The only place the two sides are still objects rather than a rendered diff."""
    if op == "==":
        _pair["actual"], _pair["expected"] = left, right


def pytest_runtest_makereport(item, call):
    if call.when != "call" or call.excinfo is None:
        return
    frame = call.excinfo.traceback[-1]
    args = {
        name: _short.repr(value)
        for name, value in frame.frame.f_locals.items()
        if name not in _SKIP and not name.startswith(("__", "@py_")) and not callable(value)
    }
    json.dump({
        "args": args,
        "expected": _short.repr(_pair["expected"]) if "expected" in _pair else None,
        "actual": _short.repr(_pair["actual"]) if "actual" in _pair else None,
        "source": str(frame.statement).strip(),
        "error": call.excinfo.exconly().split("\\n")[0],
    }, open(os.environ["DRILLION_CASE"], "w", encoding="utf-8"))
'''

NAME = "_drillion_case"
_short = (
    reprlib.Repr()
)  # only so the module states the cap it applies on the way back in
CASE_CHARS = 2000


def trim(case):
    """A case the panel can hold. A solution that builds a huge value is still a failing
    case worth reporting, and it is not worth reporting all of."""
    if not case:
        return None
    out = {}
    for key, value in case.items():
        if isinstance(value, dict):
            value = {k: v[:CASE_CHARS] for k, v in value.items()}
        elif isinstance(value, str):
            value = value[:CASE_CHARS]
        out[key] = value
    return out
