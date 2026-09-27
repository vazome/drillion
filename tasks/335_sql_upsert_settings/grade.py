"""What one sitting of 335 asks for: apply a batch of settings changes, inserting new users and
merging into existing ones.

There is no result to compare: the probe reads `settings` back after the learner's SQL and
after the answer key's, on the data shown and on a hidden second dataset."""

import datetime as dt

VALUES = {
    "theme": ["light", "dark", "sepia"],
    "lang": ["en", "pt", "no", "et"],
    "digest": ["daily", "weekly", "never"],
}


def _prefs(r, n):
    return {key: r.choice(VALUES[key]) for key in r.sample(sorted(VALUES), n)}


def brief(r):
    return {"today": f"2026-07-{r.randint(1, 28):02d}"}


def rows(r, b):
    """Users 1 to 20 have settings; the batch changes six of them and adds 21 to 26."""
    settings = [
        {
            "user_id": i,
            "prefs": _prefs(r, r.randint(2, 3)),
            "updated_on": dt.date(2026, 6, r.randint(1, 30)),
        }
        for i in range(1, 21)
    ]
    changed = r.sample(range(1, 21), 6) + list(range(21, 27))
    incoming = [{"user_id": i, "prefs": _prefs(r, r.randint(1, 2))} for i in changed]
    return {"settings": settings, "incoming": incoming}


def probes(b):
    return {
        "settings after your SQL": (
            "SELECT user_id, prefs, updated_on FROM settings ORDER BY user_id"
        )
    }
