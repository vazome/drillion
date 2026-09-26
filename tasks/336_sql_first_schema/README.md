---
title: a first schema, with its rules in the database
kind: sql
edits: task.sql
difficulty: medium
minutes: 20
prereqs: [324]
tags: [ddl, constraints]
track: sql
---
# a first schema, with its rules in the database

*A constraint is a rule the database enforces on every write, whichever program makes it.*

## Read first
- [Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html): `NOT NULL`, `UNIQUE`, `CHECK`, keys, and `ON DELETE`
- [Identity columns](https://www.postgresql.org/docs/current/ddl-identity-columns.html): ids the database hands out

## Why
A new feature needs teams and their members. Every rule about them could live in the application, and then the first script that writes to the tables directly, or the second service, breaks them. Rules in the schema hold for every writer.

Each rule has its clause. An id the database hands out is an identity column. A column that must have a value is `NOT NULL`, and one no two rows may share is `UNIQUE`. A member points at their team with a foreign key, and `ON DELETE CASCADE` says what happens to members when the team goes. `CHECK` limits a column to the values that make sense, and `DEFAULT` fills it when an insert leaves it out.

The grader never looks at what you named your constraints. It tries the writes each rule is about and checks the database says no.

## You get
An empty database.

## You return
SQL that creates the two tables `teams` and `members`, with every rule below enforced by the database.

## Rules
- `teams`: `id`, an integer the database generates, the primary key; `name`, text, required, no two teams alike
- `members`: `id`, an integer the database generates, the primary key; `team_id`, an integer, required, pointing at a team, and deleted with it
- `members.email`: text, required, no two members alike
- `members.role`: text, required, either `owner` or `{role}`, and `{role}` when an insert leaves it out

## Hints
### Hint 1
One `CREATE TABLE` per table, `teams` first, since `members` points at it. Each column is `name type`, then its constraints on the same line.

### Hint 2
`id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY` is the whole id column. A foreign key inline is `REFERENCES teams (id)`, and `ON DELETE CASCADE` follows it.

### Hint 3
The same shape on other tables, authors and their books:

```sql
CREATE TABLE authors (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name text NOT NULL
);

CREATE TABLE books (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  author_id integer NOT NULL REFERENCES authors (id) ON DELETE CASCADE,
  isbn text NOT NULL UNIQUE,
  format text NOT NULL DEFAULT 'paper' CHECK (format IN ('paper', 'ebook'))
);
```
