"""What one sitting of 336 asks for: two tables, their keys and their constraints.

Nothing is compared by name. The probes read the columns back and try the inserts and
deletes each rule is about, after the learner's SQL and after the answer key's, and the
two must agree, errors by SQLSTATE."""

ROLES = ["member", "viewer", "editor"]
TEAM = "INSERT INTO teams (name) VALUES ('t'); "
ONE = (
    TEAM
    + "INSERT INTO members (team_id, email) SELECT id, 'a@example.com' FROM teams; "
)


def brief(r):
    return {"role": r.choice(ROLES)}


def rows(r, b):
    return {}


def probes(b):
    columns = (
        "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
        "WHERE table_name = '{}' ORDER BY column_name"
    )
    return {
        "the columns of teams": columns.format("teams"),
        "the columns of members": columns.format("members"),
        "the primary keys": (
            "SELECT k.table_name, k.column_name FROM information_schema.table_constraints c "
            "JOIN information_schema.key_column_usage k USING (constraint_schema, constraint_name) "
            "WHERE c.constraint_type = 'PRIMARY KEY' ORDER BY k.table_name"
        ),
        "every team and member gets its own id": (
            TEAM + "INSERT INTO teams (name) VALUES ('u'); "
            "INSERT INTO members (team_id, email) SELECT id, name || '@example.com' FROM teams; "
            "SELECT (SELECT count(DISTINCT id) FROM teams) AS teams, "
            "(SELECT count(DISTINCT id) FROM members) AS members"
        ),
        "a new team gets an id by itself": (
            "INSERT INTO teams (name) VALUES ('a') RETURNING id IS NOT NULL AS given"
        ),
        "two teams cannot share a name": (
            "INSERT INTO teams (name) VALUES ('a'); INSERT INTO teams (name) VALUES ('a')"
        ),
        "a member's team has to exist": (
            "INSERT INTO members (team_id, email) VALUES (999, 'x@example.com')"
        ),
        "an email is required": (
            TEAM + "INSERT INTO members (team_id, email) SELECT id, NULL FROM teams"
        ),
        "two members cannot share an email": (
            ONE + "INSERT INTO members (team_id, email) "
            "SELECT id, 'a@example.com' FROM teams"
        ),
        f"a role left out is {b['role']}": ONE + "SELECT role FROM members",
        "a role outside the two is refused": (
            TEAM + "INSERT INTO members (team_id, email, role) "
            "SELECT id, 'a@example.com', 'admin' FROM teams"
        ),
        "deleting a team deletes its members": (
            ONE + "DELETE FROM teams; SELECT count(*) AS left FROM members"
        ),
    }
