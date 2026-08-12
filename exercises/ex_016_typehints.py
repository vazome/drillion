"""Most of the type hints you meet are ones you read, not ones you wrote."""

from _lib import rng

META = {"topic": 16, "title": "type hints — read a signature with get_type_hints", "tier": 3,
        "minutes": 22, "prereqs": []}


def solve(fn):
    """Report three facts about an annotated function's signature.

    fn is a function you must not call. Its annotations are stored as plain
    strings, because the file it came from starts with
    `from __future__ import annotations` — check fn.__annotations__ and you get
    {"replicas": "int", ...}, the source text, not types. Turning those strings
    into real type objects is a one-call job in the typing module.

    Return the tuple (params, nullable, ret):

        params    dict of parameter name -> resolved annotation, in declaration
                  order, with no "return" key
        nullable  sorted list of the PARAMETER names whose annotation admits
                  None
        ret       the resolved annotation of the return value

    For a function declared

        def scale(replicas: int, zone: str | None, tags: list[str]) -> dict[str, int]

    you return

        ({"replicas": int, "zone": str | None, "tags": list[str]},
         ["zone"],
         dict[str, int])

    The return annotation can itself be nullable. It never belongs in the
    nullable list — that list is parameters only.

    `str | None` is the modern spelling of Optional[str]: this value is a str
    or it is missing. Spotting those is the practical payoff of reading hints,
    since they are the ones that will hand you a None at 3am.
    """
    raise NotImplementedError


HINTS = [
    "Two separate problems. One: annotations arrive as strings and you need "
    "objects, so something has to evaluate them in the namespace of the module "
    "that defined the function. Two: once you have the objects, you need to ask "
    "of each one 'could this be None' — and a compound type like `str | None` "
    "has parts you can pull apart, while a plain `int` has none.",
    "typing.get_type_hints(fn) does the resolving and returns one dict holding "
    "the parameters AND the return, keyed 'return'. Pop that key off first: it "
    "gives you ret and leaves params clean, in declaration order. Then "
    "typing.get_args(t) returns the pieces of a union — (str, NoneType) for "
    "`str | None` — and an empty tuple for anything that is not compound. So a "
    "parameter is nullable when type(None) is in get_args of its annotation. "
    "sorted() the names at the end.",
    "Different data — a two-parameter function:\n"
    "    import typing\n"
    "\n"
    "    def f(host: str, port: int | None) -> bool: ...\n"
    "\n"
    "    print(f.__annotations__)          # under `from __future__ import\n"
    "                                      # annotations`: {'host': 'str', ...}\n"
    "    hints = typing.get_type_hints(f)  # {'host': <class 'str'>,\n"
    "                                      #  'port': int | None,\n"
    "                                      #  'return': <class 'bool'>}\n"
    "    print(hints.pop('return'))        # <class 'bool'>, and hints is now\n"
    "                                      # parameters only\n"
    "    print(typing.get_args(hints['port']))   # (<class 'int'>, <class 'NoneType'>)\n"
    "    print(typing.get_args(hints['host']))   # ()\n"
    "Yours does the same over however many parameters it is handed.",
]


# ─────────────────────────────  below here is the machinery  ──────────────

_PARAM_TYPES = ["int", "str", "bool", "float", "list[str]", "list[int]",
                "dict[str, int]", "dict[str, str]", "set[str]",
                "str | None", "int | None", "float | None"]
_RETURN_TYPES = ["bool", "int", "str", "list[str]", "dict[str, int]", "set[str]"]
_NULLABLE_RETURNS = ["str | None", "int | None", "list[str] | None"]
_PARAM_NAMES = ["replicas", "zone", "image", "tags", "labels", "timeout",
                "retries", "port", "region", "healthy", "cluster"]
_FN_NAMES = ["scale", "drain", "resolve", "reconcile", "annotate", "probe"]

_TEMPLATE = """from __future__ import annotations


def %s(%s) -> %s:
    ...
"""


def _gen(r, nullable_return=False):
    """Compile a fresh annotated function. Signature varies with the seed.

    nullable_return forces a `... | None` return type, so the test always
    includes a case where mixing the return in with the parameters shows up."""
    count = r.randint(2, 5)
    names = r.sample(_PARAM_NAMES, count)
    types = [r.choice(_PARAM_TYPES) for _ in range(count)]
    if not any("None" in t for t in types):          # always at least one nullable param
        types[r.randrange(count)] = r.choice(["str | None", "int | None"])

    fn_name = r.choice(_FN_NAMES)
    params = ", ".join(f"{n}: {t}" for n, t in zip(names, types))
    returns = r.choice(_NULLABLE_RETURNS if nullable_return else _RETURN_TYPES)
    source = _TEMPLATE % (fn_name, params, returns)

    namespace = {}
    exec(compile(source, "<generated>", "exec"), namespace)
    return namespace[fn_name]


def _reference(fn):
    import typing

    hints = typing.get_type_hints(fn)
    ret = hints.pop("return")
    nullable = sorted(name for name, t in hints.items()
                      if type(None) in typing.get_args(t))
    return hints, nullable, ret


def test_solve():
    r = rng()
    for i in range(4):
        fn = _gen(r, nullable_return=(i == 0))
        got, exp = solve(fn), _reference(fn)
        assert got == exp
        assert list(got[0]) == list(exp[0]), "params must keep declaration order"
