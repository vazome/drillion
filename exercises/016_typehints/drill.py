def solve(fn):
    from typing import get_type_hints
    modifications = get_type_hints(fn)
    zone = modifications["zone"]
    returnal = modifications["return"]

    print(get_type_hints(fn))

    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

from _lib import rng

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
    exec(compile(source, "<generated>", "exec"), namespace)  # noqa: S102 — builds fixture fns
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
