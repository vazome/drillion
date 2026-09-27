"""What one sitting of 330 asks for: the largest orders in each city, ranked.

Totals are drawn from thirty values, so equal totals inside a city happen on every seed and
the tie rule is visible."""

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
    return {"n": r.randint(2, 3)}


def rows(r, b):
    people = customers(r, 30)
    placed = orders(r, [c["id"] for c in people], 120)
    prices = [f"{r.randrange(1000, 20000) / 100:.2f}" for _ in range(30)]
    for order in placed:
        order["total"] = r.choice(prices)
    return {"customers": people, "orders": placed}
