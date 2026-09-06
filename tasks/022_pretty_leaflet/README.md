---
title: string-formatting — Erin's event leaflet
difficulty: hard
tier: core
minutes: 15
prereqs: [18]
tags: [string-formatting]
source: exercism/python concept/pretty-leaflet (MIT, adapted)
---
# string-formatting — Erin's event leaflet

*f-strings and format specs — centring, padding and a 20-column box.*

## Read first
- [f-strings](https://devdocs.io/python~3.14/reference/lexical_analysis#f-strings) — the `f'...'` prefix and what is allowed between the braces
- [str.format()](https://devdocs.io/python~3.14/library/stdtypes#str.format) — the same formatting as a method call, for when the template itself is data
- [Format specification mini-language](https://devdocs.io/python~3.14/library/string#format-specification-mini-language) — everything after the `:`: fill character, alignment (`<` `^` `>`), width, precision
- [PEP 3101: standard format specifiers](https://www.python.org/dev/peps/pep-3101/#standard-format-specifiers) — the specifier table from the PEP that introduced `.format()`
- [Real Python: formatted output](https://realpython.com/python-formatted-output/) — a complete tour with the output printed for every example
- [str.capitalize()](https://devdocs.io/python~3.14/library/stdtypes#str.capitalize) — first letter up, the rest down, which is exactly task 1
- [calendar.month_name](https://devdocs.io/python~3.14/library/calendar#calendar.month_name) — English month names indexed 1–12, so you need not type them out

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Erin is printing thousands of handbills for a season of events, and the layout has to come out of code rather than out of a designer's hands: the same narrow box every time, the event name centred, the date under it, then one line per performer with their instrument icon lined up on the right. Every piece of that is a formatting decision — capitalise this, spell out that month number, centre inside 18 columns, keep the name in 11. This is the same skill that produces a readable `--help` screen, a status table in a CLI, or an aligned log line: get the format specs right once and the template prints a thousand leaflets.

## You get
Nothing. The event details arrive as arguments to your functions.

> [!NOTE]
> Exercism's Instructions above talk about a class, a `convert_date` function and a `leaflet.set_date(...)` method — none of those exist in Exercism's own tests or exemplar (the task is marked `wip` upstream). What is graded is four plain functions, listed below. Exercism asks for four module-level functions in one `string_formatting.py`. Here there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your four functions to the grader, keyed by name. Define them wherever you like — module level or inside `solve` — as long as the dict points at them.

## You return
A dict with these four functions.

| key | parameters | returns |
| --- | --- | --- |
| `"capitalize_header"` | `event_name` — the raw event name, e.g. `'fan meetup'` | the same name with the first letter upper-cased and the rest lower-cased |
| `"format_date"` | `event_date` — a three-item list `[day, month, year]`, e.g. `[9, 4, 2020]` | the date as `'<month name> <day>, <year>'`, the month spelled out in English |
| `"display_icons"` | `icons` — a list of unicode code points, e.g. `['\U0001F3B8', '\U0001F3A4']` | a list of the rendered icons, one per code point, in the same order |
| `"print_leaflet"` | `event_name`, `icons`, `authors`, and `event_date=None` | the whole leaflet as **one string**, rows joined with `\n` |

```python
leaflet = solve()
leaflet["capitalize_header"]("fan meetup")            # -> 'Fan meetup'
leaflet["format_date"]([9, 4, 2020])                  # -> 'April 9, 2020'
leaflet["display_icons"](["\U00000040", "\U0001D70B"])  # -> ['@', '𝜋']
leaflet["print_leaflet"]("macbeth", ["\U0001F318"], ["Fleance", "Seyton"])
```

That last call returns this string — note the missing date section and the artist with no icon:

```text
********************
*                  *
*    'Macbeth'     *
*                  *
*                  *
*                  *
* Fleance      🌘  *
* Seyton           *
*                  *
********************
```

## Rules
- `format_date`'s list is `[day, month, year]` — the **day comes first**, then the month *number*, then the year
- `print_leaflet` **returns** the leaflet as a single string and prints nothing; the rows are joined with `\n` and there is no trailing newline
- the header row shows the capitalized name **in single quotes** — `'Concert'`, not `Concert`
- `event_date` defaults to `None`; with no date, that section is one more empty row
- there may be fewer icons than artists: the artists past the end of the icon list get blank space where the icon would be, and the row still has to close with its `*`
- `capitalize_header("")` is `""` — an empty header is allowed

> [!WARNING]
> The tests compare the whole leaflet string character for character, so a row that is one space wide or one space narrow fails. Every row is 20 columns wide *on screen*; an emoji is a single Python character but a double-width glyph in a terminal, which is why the artist rows are one character shorter than the border rows when you measure them with `len()`.

## Hints
### Hint 1
Four functions, and only the last one is really a layout problem. `str.capitalize()` finishes task 1 in one call — check what it does to the letters *after* the first. For the date, the month arrives as a number and has to come out as an English word; [`calendar.month_name[2]`](https://devdocs.io/python~3.14/library/calendar#calendar.month_name) is `'February'` if you would rather not type the twelve names yourself. Everything else is one f-string per row.
### Hint 2
Build the leaflet as a **list of row strings** and `"\n".join(...)` them at the very end. Each row then becomes its own small formatting problem, and you can print the list while you work to see the box taking shape. Two of those rows never change — the row of asterisks and the empty row — so make each once and reuse it.

The rows in between all have the same skeleton: a `*`, then a fixed number of columns that a format spec fills, then a `*`. The [format spec](https://devdocs.io/python~3.14/library/string#formatspec) after the `:` is where alignment lives — `^` centres, `<` pushes left, `>` pushes right, and the number is the width. Conversions go **before** the colon: `!r` asks for the quoted `repr` of a value, `!s` for its plain `str`.

For the artist rows, loop with `enumerate` over the authors so you have the name and its position together, and compare that position with `len(icons)` before you index into the icons — some leaflets have more artists than icons.
### Hint 3
Different data, same shape. A café receipt, 22 columns wide between the pipes:

```python
WIDTH = 22
items = [("Espresso", 2.5), ("Cinnamon bun", 3.0)]
rows = ["+" + "-" * WIDTH + "+", f'|{"RECEIPT":^{WIDTH}}|']
for name, price in items:
    rows.append(f"|{name:<16}{price:>6.2f}|")
rows.append("+" + "-" * WIDTH + "+")
print("\n".join(rows))
```

prints

```text
+----------------------+
|       RECEIPT        |
|Espresso          2.50|
|Cinnamon bun      3.00|
+----------------------+
```

Note `{WIDTH}` nested *inside* the spec, and that `<16` plus `>6` add up to the 22 columns the border promises.
