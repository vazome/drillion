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

## Introduction
The Python `str` built-in can be initialized using two robust string formatting methods : `f-strings` and `str.format()`. String interpolation with `f'{variable}'` is preferred because it is an easily read, complete, and very fast module. When an internationalization-friendly or more flexible approach is needed, `str.format()` allows creating almost all the other `str` variations you might need.

### literal string interpolation. f-string

Literal string interpolation is a way of quickly and efficiently formatting and evaluating expressions to `str` using the `f` prefix and the curly brace `{object}`. It can be used with all enclosing string types as: single quote `'`, double quote `"` and for multi-lines and escaping triple quotes `'''` or `"""`.

In this basic example of **f-string**, the variable `name` is rendered at the beginning of the string, and the variable `age` of type `int` is converted to `str` and rendered after `' is '`.

```python
>>> name, age = 'Artemis', 21
>>> f'{name} is {age} years old.'
'Artemis is 21 years old.'
```

The expressions evaluated by an `f-string` can be almost anything -- so the usual cautions about sanitizing input apply. Some of the many values that can be evaluated: `str`, numbers, variables, arithmetic expressions, conditional expressions, built-in types, slices, functions or any objects with either `__str__` or `__repr__` methods defined. Some examples:

```python
>>> waves = {'water': 1, 'light': 3, 'sound': 5}

>>> f'"A dict can be represented with f-string: {waves}."'
'"A dict can be represented with f-string: {\'water\': 1, \'light\': 3, \'sound\': 5}."'

>>> f'Tenfold the value of "light" is {waves["light"]*10}.'
'Tenfold the value of "light" is 30.'
```

f-string output supports the same control mechanisms such as _width_, _alignment_, and _precision_ that are described for `.format()`. String interpolation cannot be used together with the GNU gettext API for internationalization (I18N) and localization (L10N), `str.format()` needs to be used instead.

### str.format() method

`str.format()` allows for the replacement of in-text placeholders. Placeholders are identified with named indexes `{price}` or numbered indexes `{0}` or empty placeholders `{}`. Their values are specified as parameters in the `str.format()` method. Example:

```python
>>> 'My text: {placeholder1} and {}.'.format(12, placeholder1='value1')
'My text: value1 and 12.'
```

Python `.format()` supports a whole range of [mini language specifier][format-mini-language] that can be used to align text, convert, etc.

The complex formatting specifier is `{[<name>][!<conversion>][:<format_specifier>]}`:

- `<name>` can be a named placeholder or a number or empty.
- `!<conversion>` is optional and should be one of the three: `!s` for [`str()`][str-conversion], `!r` for [`repr()`][repr-conversion] or `!a` for [`ascii()`][ascii-conversion]. By default, `str()` is used.
- `:<format_specifier>` is optional and has a lot of options, which we are [listed here][format-specifiers].

Example of conversions for a diacritical ascii letter:

```python
>>> '{0!s}'.format('ë')
'ë'
>>> '{0!r}'.format('ë')
"'ë'"
>>> '{0!a}'.format('ë')
"'\\xeb'"

>>> 'She said her name is not {} but {!r}.'.format('Anna', 'Zoë')
"She said her name is not Anna but 'Zoë'."
```

Example of format specifiers, [more examples at the end of this page][summary-string-format]:

```python
>>> "The number {0:d} has a representation in binary: '{0: >8b}'.".format(42)
"The number 42 has a representation in binary: '  101010'."
```

`str.format()` should be used together with the [GNU gettext API][gnu-gettext-api] for internationalization (I18N) and localization (L10N).

[all-about-formatting]: https://realpython.com/python-formatted-output
[difference-formatting]: https://realpython.com/python-string-formatting/#2-new-style-string-formatting-strformat
[printf-style-docs]: https://devdocs.io/python~3.14/library/stdtypes#printf-style-string-formatting
[tuples]: https://www.w3schools.com/python/python_tuples.asp
[format-mini-language]: https://devdocs.io/python~3.14/library/string#format-specification-mini-language
[str-conversion]: https://www.w3resource.com/python/built-in-function/str.php
[repr-conversion]: https://www.w3resource.com/python/built-in-function/repr.php
[ascii-conversion]: https://www.w3resource.com/python/built-in-function/ascii.php
[format-specifiers]: https://www.python.org/dev/peps/pep-3101/#standard-format-specifiers
[summary-string-format]: https://www.w3schools.com/python/ref_string_format.asp
[template-string]: https://devdocs.io/python~3.14/library/string#template-strings-strings
[gnu-gettext-api]: https://devdocs.io/python~3.14/library/gettext

## Instructions
Your acquaintance Erin needs to print thousands of handbills for multiple events and they need your help! They've asked you to create the layout for a leaflet containing a header, an optional date, and a list of artists -- each associated with a _unicode icon_. The goal is to `print` and distribute your cool new leaflet design - and you'll need all your Python string formatting skills to succeed.

### 1. Create the class with a capitalized header

The `capitalize_header` function should take in an event name and return the capitalized version of the event name.

```python
>>> capitalize_header("fan meetup")
"Fan meetup"
```

### 2. Format the date

Create a new method `format_date` which takes in a list which contains a date, month, and a year. It displays the formatted date with the format `<month_name> <date>, <year>`

```python
>>> convert_date([9, 4, 2020])
>>> leaflet.date
"April 9, 2020"
>>> leaflet.set_date([13, 5, 2030])
>>> leaflet.date
"May 13, 2030"
```

### 3. Render the unicode code points as icons

When the method `display_icons` is called, the list of unicode code points passed should be rendered and returned as a `list` of _icons_.

```python
>>> leaflet.display_icons(['\U00000040', '\U0001D70B'])
['@', '𝜋']
```

### 4. Display the finished leaflet

Now you will use all the functions above, and combine them in the `print_leaflet` function.
It should take an `event_name`, a list of `icons`, a list of `authors`, and an `event_date` list.

The poster should abide by the layout below.

The leaflet follows a specific layout in the shape of a rectangle:

- The first and last rows contain 20 asterisks. `"*"`
- Each section is separated by an empty row above and below it.
- An empty row contains only one asterisk at the beginning and one at the end.
- The first section is the header of the leaflet, this title is capitalized.
- The second section is the option date, if the date is not passed, this section should be an empty row.
- The third and last section is the list of the artists, each artist associated with the corresponding icon.

```python
********************
*                  *
*    'Concert'     *
*                  *
*  June 22, 2020   *
*                  *
* John         🎸  *
* Benjamin     🎤  *
* Max          🎹  *
*                  *
********************
```

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

## Exercism hints
### General

Use only f-strings or the `format()` method to build a leaflet containing basic information about an event.

- [Introduction to string formatting in Python][str-f-strings-docs]
- [Article on realpython.com][realpython-article]

### 1. Capitalize the header

- Capitalize the title using the str method `capitalize`.

### 2. Format the date

- The `date` should be formatted manually using `f''` or `''.format()`.
- The `date` should use this format: 'Month day, year'.

### 3. Render the unicode characters as icons

- One way of rendering with `format` would be to use the unicode prefix `u'{}'`.

### 4. Display the finished leaflet

- Find the right [format_spec field][formatspec-docs] to align the asterisks and characters.
- Section 1 is the `header` as a capitalized string.
- Section 2 is the `date`.
- Section 3 is the list of artists, each artist is associated with the unicode character having the same index.
- Each line should contain 20 characters.
- Write concise code to add the necessary empty lines between each section.
- If the date is not given, replace it with a blank line.

```python
******************** # 20 asterisks
*                  *
*     'Header'     * # capitalized header
*                  *
* Month day, year  * # Optional date
*                  *
* Artist1       ⑴ * # Artist list from 1 to 4
* Artist2       ⑵ *
* Artist3       ⑶ *
* Artist4       ⑷ *
*                  *
********************
```

[str-f-strings-docs]: https://devdocs.io/python~3.14/reference/lexical_analysis#f-strings
[realpython-article]: https://realpython.com/python-formatted-output/
[formatspec-docs]: https://devdocs.io/python~3.14/library/string#formatspec

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
