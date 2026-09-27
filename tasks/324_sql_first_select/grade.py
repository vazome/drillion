"""What one sitting of 324 asks for: the newest customers of one city, newest first.

The answer is compared row for row, in order, with the answer key's on the same data, and
again on a second dataset the learner never sees."""

import datetime as dt

CITIES = ["Lisbon", "Oslo", "Porto", "Tallinn", "Riga", "Ghent"]
FIRST = ["Ada", "Grace", "Alan", "Edsger", "Barbara", "Ken", "Linus", "Margaret"]
LAST = ["Lovelace", "Hopper", "Turing", "Dijkstra", "Liskov", "Thompson", "Hamilton"]
START = dt.date(2026, 1, 1)


def brief(r):
    return {"city": r.choice(CITIES), "n": r.randint(3, 5)}


def rows(r, b):
    """40 customers, enough of them in the brief's city that the limit always bites."""
    return {
        "customers": [
            {
                "id": i,
                "name": f"{r.choice(FIRST)} {r.choice(LAST)}",
                "city": b["city"] if i <= b["n"] + 2 else r.choice(CITIES),
                "joined": START + dt.timedelta(days=r.randrange(365)),
            }
            for i in range(1, 41)
        ]
    }
