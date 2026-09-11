---
title: textwrap — lay a report out for a terminal that is exactly 72 columns wide
difficulty: medium
tier: core
minutes: 15
prereqs: [9]
tags: [strings, string-formatting]
---
# textwrap — lay a report out for a terminal that is exactly 72 columns wide

*`dedent` takes the source-code indentation off a triple-quoted string, `fill` breaks it at a width, and the indent you want on the output has to be part of that width rather than added afterwards.*

## Read first
- [`textwrap`](https://devdocs.io/python~3.14/library/textwrap) — the module and its four common functions
- [`textwrap.fill`](https://devdocs.io/python~3.14/library/textwrap#textwrap.fill) — `initial_indent` and `subsequent_indent`
- [`textwrap.dedent`](https://devdocs.io/python~3.14/library/textwrap#textwrap.dedent) — removing the leading whitespace every line shares

## Why
The audit tool prints its findings to a terminal, and the descriptions come from triple-quoted strings inside the checks themselves — which means every line after the first carries whatever indentation the surrounding function had. Printed raw, the report is a staircase. Wrapped naively, it is a staircase with a ragged right edge, because the two-space indent the layout calls for was added after the wrapping and pushed every line two columns past the limit. Nobody notices on a wide window; everyone notices in the CI log, where the wrap point is fixed and every second line is a two-character orphan.

## You get
- `sections`, a list of `(heading, body)` pairs. Each `body` is a single paragraph, arriving with the indentation it had in its source file and with newlines wherever the author happened to break the line.
- `width`, the terminal width in columns.

## You return
one string: the whole report.

## Rules
- Each section is its heading on a line of its own, unindented, then the body.
- The body is re-flowed from scratch: the author's line breaks and the source indentation carry no meaning, and neither survives. Words are separated by single spaces.
- Every body line is indented two spaces, and **no line of the report may be longer than `width`** — the two spaces count towards it.
- Sections are separated by one blank line. There is no blank line before the first heading and no trailing newline after the last body line.

```python
solve([("Certs", "\n    certificate expires\n    tomorrow")], 20)
# -> 'Certs\n  certificate\n  expires tomorrow'
# and not 'Certs\n  certificate expires\n  tomorrow', whose first line is 21 columns
```

> [!WARNING]
> Wrapping to `width` and then indenting the result gives you lines of `width + 2`. The indent has to be handed to the wrapper so it can budget for it, not stapled on afterwards.

## Hints
### Hint 1
`textwrap.dedent` removes the longest whitespace prefix that *every* non-blank line shares. A body that starts with a newline and then indented lines dedents cleanly; `.strip()` afterwards clears the leading and trailing whitespace it leaves behind.
### Hint 2
`textwrap.fill` collapses runs of whitespace, including newlines, into single spaces before it wraps — so the author's line breaks disappear without you doing anything about them.
### Hint 3
`fill` budgets for the indent when you pass it in:

```python
import textwrap

body = "\n        a long enough sentence to need two lines\n        of output"
textwrap.fill(textwrap.dedent(body).strip(), width=24, initial_indent="  ", subsequent_indent="  ")
# -> '  a long enough sentence\n  to need two lines of\n  output'
```

Every line, first one included, comes out at 24 columns or fewer. `initial_indent` and `subsequent_indent` are separate because a bullet list wants a different marker on the first line; here they are the same two spaces.
