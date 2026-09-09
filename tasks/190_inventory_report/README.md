---
title: argparse + CSV — filter an inventory report
difficulty: medium
tier: core
minutes: 18
prereqs: [9, 106, 108]
tags: [argparse, csv, f-strings]
---
# argparse + CSV — filter an inventory report

*Parse the command line, read structured input, and render unambiguous diagnostics.*

## Read first
- [argparse](https://devdocs.io/python~3.14/library/argparse) — typed options and boolean flags
- [csv.DictReader](https://devdocs.io/python~3.14/library/csv#csv.DictReader) — rows addressed by header name
- [Formatted string literals](https://devdocs.io/python~3.14/reference/lexical_analysis#f-strings) — conversion flags such as `!r`

## Why
An inventory command gets its data as CSV, but operators need a small view for one region or a minimum replica count. Shell flags choose the view; the CSV parser preserves quoted fields; an f-string's `!r` conversion keeps commas, whitespace, and escapes unambiguous in diagnostic output.

## You get
`text`, a CSV string with `service`, `region`, and `replicas` columns, and `argv`, the arguments after the command name.

## You return
A list of diagnostic lines such as `"service='api' region=eu replicas=3"`.

## Rules
Build an `ArgumentParser` with:

- `--region REGION`, optional;
- `--minimum N`, an integer whose default is `0`;
- `--descending`, a boolean flag.

Read `text` with `csv.DictReader`. Keep rows in the chosen region, when supplied, whose replica count is at least the minimum. Normally sort by service name. With `--descending`, sort by replica count descending and service name ascending for ties. Format each row as `service=<repr> region=<region> replicas=<replicas>`, using `!r` for the service value.

```python
solve('service,region,replicas\n"api,edge",eu,3\nweb,us,5', ["--region", "eu"])
# -> ["service='api,edge' region=eu replicas=3"]
```

## Hints
### Hint 1
Let each tool own one boundary: `argparse` for strings in `argv`, `DictReader` for strings in the CSV, and the f-string for the final diagnostic representation.
### Hint 2
Use `type=int` on `--minimum` and `action="store_true"` on `--descending`. Convert each row's `replicas` cell to `int` only when comparing or sorting it.
### Hint 3
Parse first, then filter the `DictReader`, sort the surviving row dictionaries, and finish with a list comprehension containing `f"service={row['service']!r} ..."`.
