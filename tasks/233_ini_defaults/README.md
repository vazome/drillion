---
title: configparser — read an ini where DEFAULT fills the gaps and %(name)s fills itself
difficulty: medium
tier: core
minutes: 15
prereqs: [68]
tags: [files-text, stdlib-ops]
---
# configparser — read an ini where DEFAULT fills the gaps and %(name)s fills itself

*A `[DEFAULT]` section is inherited by every other section, and `%(key)s` inside a value is substituted from the section you are reading it out of.*

## Read first
- [`configparser`](https://devdocs.io/python~3.14/library/configparser) — the module, `[DEFAULT]`, and the mapping access
- [Interpolation](https://devdocs.io/python~3.14/library/configparser#interpolation-of-values) — `%(name)s` and `BasicInterpolation`
- [`ConfigParser.getint`](https://devdocs.io/python~3.14/library/configparser#configparser.ConfigParser.getint) — the typed getters

## Why
One ini file describes three environments, and almost every setting is the same in all three. Writing every key out three times is how a staging file ends up pointing at a production database — not because anyone decided to, but because a line got changed in two of the three places. An ini's `[DEFAULT]` section exists so the common value is written once and each environment states only what differs. Interpolation is the same argument one level down: the connection URL is built from the host and the port rather than repeated alongside them, so changing the port cannot leave a stale URL behind. Neither feature is something you rebuild by hand after parsing — reading the file the right way gives you both.

## You get
- `text`, the whole ini file as one string.
- `section`, the name of the section to read.

## You return
a tuple `(values, port)`.

- `values` is a plain `dict` of every key visible in that section, with every value fully interpolated.
- `port` is that section's `port`, as an `int`.

## Rules
- "Every key visible in that section" includes the keys it inherits from `[DEFAULT]` and never wrote itself. A dict built only from the lines physically under the section header is wrong.
- Values are interpolated, not raw: a value containing `%(host)s` comes back with the host substituted, using the host that this section sees — its own if it has one, `[DEFAULT]`'s otherwise.
- `values` is a real `dict`, not the parser's section proxy, and every value in it is a `str`.
- `port` is an `int`. `values["port"]` stays a string.
- Keys are lowercased by the parser. Leave them that way.

```python
text = """
[DEFAULT]
host = localhost
port = 5432
url = %(host)s:%(port)s

[prod]
host = db.prod
"""
values, port = solve(text, "prod")
values      # -> {'host': 'db.prod', 'port': '5432', 'url': 'db.prod:5432'}
port        # -> 5432
```

> [!WARNING]
> `parser.sections()` does not list `DEFAULT`, and `parser["prod"]` is a live view rather than a dict — comparing it to a dict works, but returning it hands the caller something that still points at the parser. `dict(...)` around it settles both.

## Hints
### Hint 1
`ConfigParser.read_string(text)` parses a string; `read()` is for filenames and would need a file that does not exist here.
### Hint 2
A `ConfigParser` behaves like a mapping. `parser[section]` gives you a section that already knows about `[DEFAULT]` and already interpolates, so iterating it — or wrapping it in `dict()` — gets you both features for free.
### Hint 3
Typed reads go through the parser, not the string:

```python
import configparser

parser = configparser.ConfigParser()
parser.read_string("[web]\nport = 8080\ndebug = yes\n")
parser.getint("web", "port")       # -> 8080
parser.getboolean("web", "debug")  # -> True
parser["web"]["port"]              # -> '8080', still a string
```
