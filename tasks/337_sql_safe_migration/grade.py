"""What one sitting of 337 asks for: a new required column on a table that already has rows,
filled from other data.

The probes read every account's plan back and try the writes the new rules forbid, after
the learner's migration and after the answer key's, on both datasets."""

import datetime as dt

PLANS = ["pro", "team", "plus"]


def brief(r):
    return {"paid": r.choice(PLANS)}


def rows(r, b):
    """30 accounts, a random third of them with payments."""
    accounts = [{"id": i, "email": f"user{i}@example.com"} for i in range(1, 31)]
    payers = r.sample(range(1, 31), 10)
    payments = [
        {"id": n, "account_id": a, "paid_on": dt.date(2026, r.randint(1, 6), 1)}
        for n, a in enumerate(payers + r.sample(payers, 5), 1)
    ]
    return {"accounts": accounts, "payments": payments}


def probes(b):
    return {
        "every account's plan after your migration": (
            "SELECT id, plan FROM accounts ORDER BY id"
        ),
        "the plan column": (
            "SELECT data_type, is_nullable FROM information_schema.columns "
            "WHERE table_name = 'accounts' AND column_name = 'plan'"
        ),
        "a new account gets free": (
            "INSERT INTO accounts (id, email) VALUES (100000, 'n@example.com'); "
            "SELECT plan FROM accounts WHERE id = 100000"
        ),
        "a plan cannot be left empty": "UPDATE accounts SET plan = NULL WHERE id = 1",
        "an unknown plan is refused": "UPDATE accounts SET plan = 'gold' WHERE id = 1",
    }
