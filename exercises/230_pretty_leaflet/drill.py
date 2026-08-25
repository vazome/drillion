def solve():
    raise NotImplementedError


# ══ machinery — everything below is the grader's, not yours ══

import calendar

from _lib import rng

_EVENTS = ["concert", "webinar", "macbeth", "fan meetup", "poetry SLAM",
           "jazz NIGHT", "book fair", "gala", "OPEN mic"]
_NAMES = ["John", "Benjamin", "Max", "Vince", "Chris", "Leo", "Fleance",
          "Seyton", "Ada", "Grace", "Ravi", "Yuki", "Nina", "Omar", "Tess"]
_ICONS = ["\U0001f3b8", "\U0001f3a4", "\U0001f3b9", "\U0001f4da", "\U0001f4bb",
          "\U0001f3af", "\U0001f318", "\U0001f98a", "\U0001f340", "\U0001f420"]


def _gen(r):
    event_name = r.choice(_EVENTS)
    authors = r.sample(_NAMES, r.randint(1, 4))
    icons = r.sample(_ICONS, r.randint(0, len(authors)))
    event_date = None
    if r.random() < 0.75:
        event_date = [r.randint(1, 28), r.randint(1, 12), r.randint(1990, 2030)]
    return event_name, icons, authors, event_date


def _reference():
    def capitalize_header(event_name):
        return event_name.capitalize()

    def format_date(event_date):
        day, month, year = event_date
        return f"{calendar.month_name[month]} {day}, {year}"

    def display_icons(icons):
        return [f"{icon}" for icon in icons]

    def print_leaflet(event_name, icons, authors, event_date=None):
        full_row = "*" * 20
        empty_row = f'*{"":^18}*'
        header = capitalize_header(event_name)
        rendered = display_icons(icons)
        date_string = format_date(event_date) if event_date is not None else ""

        poster = [full_row, empty_row, f"*{header!r:^18}*", empty_row,
                  f"*{date_string!s:^18}*", empty_row]
        for position, author in enumerate(authors):
            icon = rendered[position] if position < len(rendered) else "    "
            poster.append(f'*{"":>1}{author:<11}{icon:>3}{"":>2}*')
        poster.append(empty_row)
        poster.append(full_row)
        return "\n".join(poster)

    return {"capitalize_header": capitalize_header,
            "format_date": format_date,
            "display_icons": display_icons,
            "print_leaflet": print_leaflet}


def test_solve():
    r = rng()
    got, want = solve(), _reference()
    for _ in range(6):
        event_name, icons, authors, event_date = _gen(r)
        assert (got["capitalize_header"](event_name)
                == want["capitalize_header"](event_name)), \
            f"capitalize_header({event_name!r})"
        assert (got["display_icons"](icons)
                == want["display_icons"](icons)), f"display_icons({icons!r})"
        if event_date is not None:
            assert (got["format_date"](event_date)
                    == want["format_date"](event_date)), \
                f"format_date({event_date!r})"
        assert (got["print_leaflet"](event_name, icons, authors, event_date)
                == want["print_leaflet"](event_name, icons, authors, event_date)), \
            f"print_leaflet({event_name!r}, {icons!r}, {authors!r}, {event_date!r})"

    # canonical cases from exercism's string_formatting_test.py
    assert got["capitalize_header"]("") == ""
    assert got["capitalize_header"]("Event") == "Event"
    assert got["capitalize_header"]("evENt") == "Event"
    assert got["format_date"]([21, 2, 2021]) == "February 21, 2021"
    assert got["display_icons"](
        ["\U0001f98a", "\U0001f340", "\U0001f420"]) == ["🦊", "🍀", "🐠"]

    concert = ("""********************
*                  *
*    'Concert'     *
*                  *
*  April 30, 2021  *
*                  *
* John         🎸  *
* Benjamin     🎤  *
* Max          🎹  *
*                  *
********************""")
    assert got["print_leaflet"](
        "Concert", ["\U0001f3b8", "\U0001f3a4", "\U0001f3b9"],
        ["John", "Benjamin", "Max"], [30, 4, 2021]) == concert

    macbeth = ("""********************
*                  *
*    'Macbeth'     *
*                  *
*                  *
*                  *
* Fleance      🌘  *
* Seyton           *
*                  *
********************""")
    assert got["print_leaflet"](
        "macbeth", ["\U0001f318"], ["Fleance", "Seyton"]) == macbeth

    webinar = ("""********************
*                  *
*    'Webinar'     *
*                  *
* January 29, 2020 *
*                  *
* Vince        📚  *
* Chris        💻  *
* Leo          🎯  *
*                  *
********************""")
    assert got["print_leaflet"](
        "webinar", ["\U0001f4da", "\U0001f4bb", "\U0001f3af"],
        ["Vince", "Chris", "Leo"], [29, 1, 2020]) == webinar
