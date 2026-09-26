"""What one sitting of 338 asks for: a trigger that keeps updated_at current when one column
changes, and leaves it alone otherwise.

The probes compare whether updated_at moved, never its value, since now() differs between
the learner's run and the answer key's."""

WORDS = ["draft", "notes", "plan", "minutes", "brief", "memo"]


def brief(r):
    watched = r.choice(["title", "body"])
    return {"watched": watched, "other": "body" if watched == "title" else "title"}


def rows(r, b):
    return {
        "documents": [
            {"id": i, "title": f"{r.choice(WORDS)} {i}", "body": r.choice(WORDS) * 3}
            for i in range(1, 11)
        ]
    }


def probes(b):
    w, o = b["watched"], b["other"]
    moved = "SELECT updated_at > TIMESTAMP '2000-01-01' AS moved FROM documents WHERE id = {}"
    return {
        f"changing {w} moves updated_at": (
            f"UPDATE documents SET {w} = {w} || '!' WHERE id = 1; " + moved.format(1)
        ),
        f"changing only {o} leaves it": (
            f"UPDATE documents SET {o} = {o} || '!' WHERE id = 1; " + moved.format(1)
        ),
        "an update that changes nothing leaves it": (
            f"UPDATE documents SET {w} = {w} WHERE id = 1; " + moved.format(1)
        ),
        "an insert keeps the default": (
            "INSERT INTO documents (id, title, body) VALUES (1000, 't', 'b'); "
            + moved.format(1000)
        ),
    }
