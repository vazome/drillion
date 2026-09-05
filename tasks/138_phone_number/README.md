---
title: raising-and-handling-errors — clean a NANP number or say exactly why you cannot
difficulty: hard
tier: core
minutes: 15
prereqs: [11, 35]
tags: [raising-and-handling-errors, string-formatting, errors]
source: exercism/python practice/phone-number (MIT, adapted)
---
# raising-and-handling-errors — clean a NANP number or say exactly why you cannot

*phone-number — normalise the input, and fail with a message that names the problem.*

## Read first
- [Raising exceptions](https://devdocs.io/python~3.14/tutorial/errors#raising-exceptions) — `raise ValueError("message")`, and why the message is the useful part
- [Built-in exceptions](https://devdocs.io/python~3.14/library/exceptions#ValueError) — when `ValueError` is the right class to pick
- [Classes tutorial](https://devdocs.io/python~3.14/tutorial/classes) — `__init__` runs during construction, so raising there means the object never exists
- [f-strings](https://devdocs.io/python~3.14/reference/lexical_analysis#f-strings) — assembling `pretty()` from three slices
- [str.isdigit()](https://devdocs.io/python~3.14/library/stdtypes#str.isdigit) and [str.isalpha()](https://devdocs.io/python~3.14/library/stdtypes#str.isalpha) — the two questions that separate "letters" from "punctuation"

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Any system that accepts a phone number gets it in fifteen shapes: with dots, with brackets, with a country code, with a letter someone fat-fingered. Downstream — the SMS gateway, the CRM, the deduplication job — wants one shape and nothing else. So the boundary of your system does two things: it normalises what it can, and it rejects what it cannot with a message precise enough for the caller to fix the input without opening a ticket. "Invalid phone number" is a bad error. "area code cannot start with zero" is a good one.

## Introduction
You've joined LinkLine, a leading communications company working to ensure reliable connections for everyone.
The team faces a big challenge: users submit phone numbers in all sorts of formats — dashes, spaces, dots, parentheses, and even prefixes.
Some numbers are valid, while others are impossible to use.

Your mission is to turn this chaos into order.
You'll clean up valid numbers, formatting them appropriately for use in the system.
At the same time, you'll identify and filter out any invalid entries.

The success of LinkLine's operations depends on your ability to separate the useful from the unusable.
Are you ready to take on the challenge and keep the connections running smoothly?

## Instructions
Clean up phone numbers so that they can be sent SMS messages.

The **North American Numbering Plan (NANP)** is a telephone numbering system used by many countries in North America like the United States, Canada or Bermuda.
All NANP-countries share the same international country code: `1`.

NANP numbers are ten-digit numbers consisting of a three-digit Numbering Plan Area code, commonly known as _area code_, followed by a seven-digit local number.
The first three digits of the local number represent the _exchange code_, followed by the unique four-digit number which is the _subscriber number_.

The format is usually represented as

```text
NXX NXX-XXXX
```

where `N` is any digit from 2 through 9 and `X` is any digit from 0 through 9.

Sometimes they also have the country code (represented as `1` or `+1`) prefixed.

Your task is to clean up differently formatted telephone numbers by removing punctuation and the country code if present.

For example, the inputs

- `+1 (613)-995-0253`
- `613-995-0253`
- `1 613 995 0253`
- `613.995.0253`

should all produce the output

`6139950253`

**Note:** As this exercise only deals with telephone numbers used in NANP-countries, only 1 is considered a valid country code.

### Exception messages

Sometimes it is necessary to [raise an exception](https://devdocs.io/python~3.14/tutorial/errors#raising-exceptions). When you do this, you should always include a **meaningful error message** to indicate what the source of the error is. This makes your code more readable and helps significantly with debugging. For situations where you know that the error source will be a certain type, you can choose to raise one of the [built in error types](https://devdocs.io/python~3.14/library/exceptions#base-classes), but should still include a meaningful message.

This particular exercise requires that you use the [raise statement](https://devdocs.io/python~3.14/reference/simple_stmts#the-raise-statement) to "throw" multiple `ValueErrors` if the `PhoneNumber()` class constructor is passed a number that is not a _valid phone number_.  This includes errors for when area code or exchange codes are invalid, when the number has too many (or too few) digits, and for when punctuation or letters are given as input. The tests will only pass if you both `raise` the `exception` and include a message with it.

To raise a `ValueError` with a message, write the message as an argument to the `exception` type:

```python
# if a phone number has less than 10 digits.
raise ValueError("must not be fewer than 10 digits")

# if a phone number has more than 11 digits.
raise ValueError("must not be greater than 11 digits")

# if a phone number has 11 digits, but starts with a number other than 1.
raise ValueError("11 digits must start with 1")

# if a phone number has an exchange code that starts with 0.
raise ValueError("exchange code cannot start with zero")

# if a phone number has an exchange code that starts with 1.
raise ValueError("exchange code cannot start with one")

# if a phone number has an area code that starts with 0.
raise ValueError("area code cannot start with zero")

# if a phone number has an area code that starts with 1.
raise ValueError("area code cannot start with one")

# if a phone number has punctuation in place of some digits.
raise ValueError("punctuations not permitted")

# if a phone number has letters in place of some digits.
raise ValueError("letters not permitted")
```

## You get
Nothing to start — you return a **class**. The grader builds it as `PhoneNumber(number)`, where `number` is the raw string a user typed, e.g. `"+1 (613)-995-0253"`.

> [!NOTE]
> Exercism's stub is a `class PhoneNumber` in `phone_number.py`. Here the entry point is `solve()`, which takes **no arguments** and returns the class itself — not an instance.

## You return
The class. The grader uses it like this:

```python
PhoneNumber = solve()
phone = PhoneNumber("+1 (223) 456-7890")
phone.number     # -> "2234567890"
phone.area_code  # -> "223"
phone.pretty()   # -> "(223)-456-7890"
```

| member | is | value |
| --- | --- | --- |
| `.number` | attribute | the ten digits, no separators, no country code |
| `.area_code` | attribute | the first three of those digits |
| `.pretty()` | method | `"(223)-456-7890"` — brackets around the area code, then hyphens |

Validation happens in `__init__`: an invalid number must raise while it is being constructed, not later.

## Rules
Only these characters are formatting and are simply removed: `(`, `)`, `+`, `-`, `.` and whitespace. Everything left after that must be a digit.

The checks run **in this order**, and each one raises `ValueError` with exactly this message:

| when | message |
| --- | --- |
| a letter is present | `letters not permitted` |
| any other non-digit is present | `punctuations not permitted` |
| fewer than 10 digits | `must not be fewer than 10 digits` |
| more than 11 digits | `must not be greater than 11 digits` |
| 11 digits not starting with `1` | `11 digits must start with 1` |
| area code starts with `0` | `area code cannot start with zero` |
| area code starts with `1` | `area code cannot start with one` |
| exchange code starts with `0` | `exchange code cannot start with zero` |
| exchange code starts with `1` | `exchange code cannot start with one` |

- an 11-digit number starting with `1` is valid; drop that leading `1` and keep the ten digits
- the area code is digits 1–3 of the ten, the exchange code digits 4–6, the subscriber number digits 7–10

```python
PhoneNumber = solve()
PhoneNumber("223.456.7890").number       # -> "2234567890"
PhoneNumber("223 456   7890   ").number  # -> "2234567890"
PhoneNumber("12234567890").pretty()      # -> "(223)-456-7890"
PhoneNumber("523-abc-7890")              # raises ValueError("letters not permitted")
```

> [!WARNING]
> The messages are compared character for character — lower case, no full stop, and `punctuations` is plural. The order matters too: `"523-abc-7890"` has only seven digits, and the expected message is still `letters not permitted`, so the character checks must come before the length checks.

## Hints
### Hint 1
Sketch the checks as a straight list before you write them, because the order is part of the specification and not a detail. Notice that `"523-abc-7890"` is both too short *and* contains letters, yet only one message is correct — so read the table top to bottom and let the first matching check win.
### Hint 2
Strip the formatting characters into a `digits` string first; every later check works on that string, never on the raw input. Then: any `isalpha()` character means letters; any remaining non-digit means punctuation; `len(digits)` handles the two length messages; an 11-digit string is only allowed when it starts with `1`, and once you have checked that, slice it off so you are always holding exactly ten digits. From there `digits[0]` is the area code's first character and `digits[3]` is the exchange code's. Store the slices on `self` at the end and let `pretty()` just format them.
### Hint 3
Different data, same "validate at the boundary, in a fixed order, with a specific message" shape — parsing a port from configuration:

```python
def port(raw):
    text = raw.strip()
    if not text.isdigit():
        raise ValueError('port must be digits only')
    value = int(text)
    if value == 0:
        raise ValueError('port cannot be zero')
    if value > 65535:
        raise ValueError('port must not be greater than 65535')
    return value

port(' 8080 ')   # -> 8080
```

Normalise, then a run of guards from most specific to least, then return the clean value. Anything that gets past the guards is safe for the rest of the program to trust.
