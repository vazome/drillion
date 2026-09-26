"""What one sitting of 333 asks for: each customer's latest order of one status.

Compared row for row, in order, with the answer key's, on the data shown and on a second
dataset the learner never sees."""

import datetime as dt

CITIES = ["Lisbon", "Oslo", "Porto", "Tallinn", "Riga", "Ghent"]
FIRST = ["Ada", "Grace", "Alan", "Edsger", "Barbara", "Ken", "Linus", "Margaret"]
LAST = ["Lovelace", "Hopper", "Turing", "Dijkstra", "Liskov", "Thompson", "Hamilton"]
START = dt.date(2026, 1, 1)


def customers(r, n, city=None, at_least=0):
    """`n` customers, the first `at_least` of them in `city`."""
    return [
        {
            "id": i,
            "name": f"{r.choice(FIRST)} {r.choice(LAST)}",
            "city": city if i <= at_least else r.choice(CITIES),
            "joined": START + dt.timedelta(days=r.randrange(365)),
        }
        for i in range(1, n + 1)
    ]


def orders(r, ids, n, months=(3, 4, 5, 6)):
    """`n` orders by the customers in `ids`, placed in 2026 during `months`."""
    return [
        {
            "id": i,
            "customer_id": r.choice(ids),
            "placed_at": dt.datetime(  # noqa: DTZ001 - a timestamp without time zone
                2026,
                r.choice(months),
                r.randint(1, 28),
                r.randrange(24),
                r.randrange(60),
            ),
            "status": r.choices(["paid", "shipped", "refunded"], [5, 3, 1])[0],
            "total": f"{r.randrange(500, 50000) / 100:.2f}",
        }
        for i in range(1, n + 1)
    ]


def brief(r):
    return {"status": r.choice(["paid", "shipped"])}


def rows(r, b):
    people = customers(r, 20)
    return {"customers": people, "orders": orders(r, [c["id"] for c in people], 150)}
