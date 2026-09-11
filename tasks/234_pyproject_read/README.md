---
title: tomllib — pull the facts out of a pyproject without assuming any of them are there
difficulty: medium
tier: core
minutes: 15
prereqs: [48]
tags: [files-text, dict-get]
---
# tomllib — pull the facts out of a pyproject without assuming any of them are there

*`tomllib` turns TOML into plain dicts and lists, which means every optional table in the file is an optional key you have to reach for carefully.*

## Read first
- [`tomllib`](https://devdocs.io/python~3.14/library/tomllib) — the module, `load` and `loads`
- [`dict.get`](https://devdocs.io/python~3.14/library/stdtypes#dict.get) — a default instead of a `KeyError`
- [pyproject.toml](https://packaging.python.org/en/latest/specifications/pyproject-toml/) — what `[project]` is allowed to contain

## Why
The audit script walks a hundred repositories and reports what each one declares: its name, the Python it needs, what it depends on, and how wide its lines are allowed to be. Every one of those except the name is optional, and about a third of the repositories leave out at least one. Written with square brackets, the script crashes on repository seventeen, and the person running it fixes that one key, reruns, and crashes on repository thirty-one — an afternoon spent discovering the schema one exception at a time. The information that a project declares no dependencies is not an error. It is a finding, and the report should say so.

## You get
`text`, the contents of a `pyproject.toml` as a string.

## You return
a dict with exactly these five keys:

| key | value |
|---|---|
| `name` | `project.name`, a string |
| `requires_python` | `project.requires-python`, or `None` when it is absent |
| `dependencies` | `project.dependencies`, sorted; `[]` when absent |
| `dev_dependencies` | `project.optional-dependencies.dev`, sorted; `[]` when absent |
| `line_length` | `tool.ruff.line-length`, or `88` when absent |

## Rules
- `name` is the one thing you may assume is there.
- Every other lookup has to survive its table being missing entirely — `[tool]` absent, `[tool.ruff]` absent, `[project.optional-dependencies]` present but with no `dev` key. All three happen.
- Both dependency lists come back sorted, and sorting must not disturb the parsed document.
- `line_length` is an `int`; the default is `88` and it is a real `int` too.
- The TOML key is `requires-python` with a hyphen; the key you return is `requires_python` with an underscore. Same for `line-length`.

```python
solve('[project]\nname = "drillion"\n[tool.ruff]\nline-length = 100\n')
# -> {'name': 'drillion', 'requires_python': None, 'dependencies': [],
#     'dev_dependencies': [], 'line_length': 100}
```

> [!NOTE]
> `tomllib.load` wants a file opened in **binary** mode, because TOML is defined to be UTF-8 and the module will not let a locale decide otherwise. You have a string here, so `tomllib.loads` is the one you want.

## Hints
### Hint 1
The result of `tomllib.loads` is ordinary dicts and lists all the way down — nothing clever, nothing lazy. Everything you know about dicts applies.
### Hint 2
`.get(key, {})` chains: an absent table becomes an empty dict, and asking that empty dict for the next level down gives another default rather than an exception. The chain only ends when you ask for the value itself.
### Hint 3
Reaching three levels down safely:

```python
import tomllib

data = tomllib.loads('[project]\nname = "app"\n')
data.get("tool", {}).get("ruff", {}).get("line-length", 88)      # -> 88
data["project"].get("optional-dependencies", {}).get("dev", [])  # -> []
sorted(["z", "a"])                                                # a new list; the original is untouched
```

Each `{}` is a stand-in for the table that is not there, and it is thrown away the moment the next `.get` misses too.
