---
title: 'YAML, the concept — flat key: value block by hand'
difficulty: medium
tier: core
minutes: 12
prereqs: [16]
tags: [files-text]
---
# YAML, the concept — flat key: value block by hand

Half of DevOps config is YAML. PyYAML is not installed here, so this drills the concept by hand on the flat subset — in real code it is one `yaml.safe_load` call.

## Read first
- [PyYAML documentation](https://pyyaml.org/wiki/PyYAMLDocumentation) — `safe_load` — never plain `load` on input you did not write

## Why
Deployment settings live in a small text file: one setting per line as "key: value", with comments and blank lines in between. The deploy tool needs those settings as real typed values (3 as a number, false as a yes/no flag), not as text. The usual library for this format is not installed here, so you parse the simple flat form by hand. The trap: a value like an image tag `nginx:1.25` contains a colon of its own.

## You get
`text` — a multi-line string of settings, like the block shown in the rules below. The test creates it and hands it to you; you never build it yourself.

## You return
a dict mapping each key to its typed value, like

```python
{"replicas": 3, "debug": False, "name": "api"}
```

## Rules
`text` is a flat YAML-style mapping — the honest subset you can parse without a library:

```yaml
# deploy config
replicas: 3
image: nginx:1.25

debug: false
name : api
```

Return it as a dict with typed values:

```python
solve(text)
# -> {"replicas": 3, "image": "nginx:1.25", "debug": False, "name": "api"}
```

Rules:

- skip blank lines and lines whose stripped form starts with `"#"`
- split each remaining line at the FIRST colon only; strip both halves
- convert values:

| value text | becomes |
| --- | --- |
| `"true"` | `True` |
| `"false"` | `False` |
| all digits | `int` |
| anything else | stays a string |

Real YAML adds nesting, lists, anchors and sharper typing edges — which is exactly why real scripts call `yaml.safe_load` instead of doing this.

## Hints
### Hint 1
This is the YAML idea without the library: a mapping is lines of key, colon, value, with comments and blanks to ignore. The trap is that a value can contain a colon too — an image tag like `nginx:1.25` — so cutting at every colon destroys data. And YAML is typed: `3` and `true` are not strings.
### Hint 2
`splitlines` walks the block. `strip` plus `startswith('#')` filters the noise. `partition(':')` splits at the first colon only — that is why it beats `split` here. For typing: compare the value against `'true'` and `'false'`, then try `isdigit` for ints, otherwise keep the string.
### Hint 3
Different data, same moves:

```python
line = 'listen: 0.0.0.0:8080'
key, _, value = line.partition(':')
print(key.strip(), '|', value.strip())   # listen | 0.0.0.0:8080
print('42'.isdigit(), 'id42'.isdigit())  # True False
```

In real code this whole task is `yaml.safe_load(text)` — and never plain `yaml.load`, which can construct arbitrary Python objects from untrusted input.
