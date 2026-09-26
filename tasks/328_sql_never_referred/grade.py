"""What one sitting of 328 asks for: the customers of one city who never referred anyone.

Most customers have no referrer, so `referred_by` always holds NULLs, and `NOT IN` over it
returns nothing on every seed. That is the trap the task is about."""

CITIES = ["Lisbon", "Oslo", "Porto", "Tallinn", "Riga", "Ghent"]
FIRST = ["Ada", "Grace", "Alan", "Edsger", "Barbara", "Ken", "Linus", "Margaret"]
LAST = ["Lovelace", "Hopper", "Turing", "Dijkstra", "Liskov", "Thompson", "Hamilton"]


def brief(r):
    return {"city": r.choice(CITIES)}


def rows(r, b):
    """40 customers, the first 10 in the brief's city. A referrer is always an earlier
    customer, so the rows insert in order; the first customer never has one."""
    return {
        "customers": [
            {
                "id": i,
                "name": f"{r.choice(FIRST)} {r.choice(LAST)}",
                "city": b["city"] if i <= 10 else r.choice(CITIES),
                "referred_by": r.randrange(1, i)
                if i > 1 and r.random() < 0.4
                else None,
            }
            for i in range(1, 41)
        ]
    }
