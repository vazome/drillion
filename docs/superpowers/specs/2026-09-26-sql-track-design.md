# SQL tasks: design

Status: agreed in conversation up to the engine; the surfaces, the first tasks and testing
below are for review.

## Scope

Postgres-flavoured SQL: querying, changing data, and schema work (DDL). Transactions, locks,
roles and performance tuning are out: they need concurrent sessions or a real server, and
belong to a later track if one is wanted.

## What the learner does

A SQL task is a database with a question about it. The task ships `schema.sql`, shown
read-only in the same `FileTabs` strip a Helm chart or a build context uses. The learner
writes `task.sql`, the whole file, with no machinery marker.

```
tasks/324_sql_first_select/
  README.md      kind: sql, track: sql, tags, prereqs; spec with {placeholders}
  schema.sql     read-only, the tables this sitting's data lives in
  task.sql       the learner's file
  solution.sql   the answer key, with the same {placeholders}
  grade.py       brief(r), rows(r, b), and optionally probes(b), check(result, b)
```

- `brief(r)` picks the sitting's parameters, as a Dockerfile task's does ("customers with more
  than `{n}` orders since `{since}`"). It is stored on the sitting, and the README is rendered
  against it.
- `rows(r, b)` generates table contents: `{table: [row, ...]}`, each row a dict keyed by column.
  Rows are inserted with bound parameters, so no generated value is ever spliced into SQL.

Three shapes, one grading model:

1. **Query.** `task.sql` is one `SELECT` (CTEs allowed). It is run, and so is `solution.sql`,
   on the same data; the column names and rows are compared. Row order counts only when the
   frontmatter says `ordered: true`.
2. **Change the data.** `INSERT`, `UPDATE`, `DELETE`, an upsert with `ON CONFLICT`. `probes(b)`
   then queries the tables, and each probe's result is compared with the same probe run after
   the answer key.
3. **Schema.** Tables, constraints, `ALTER` migrations, views, generated columns, PL/pgSQL
   triggers. The probes read `information_schema` and `pg_catalog`, and exercise behaviour: an
   insert that must fail with SQLSTATE `23505`, a row whose trigger must have set a column.
   Each probe runs inside its own savepoint, so an expected error never aborts the ones after it.

A probe's result is compared with the answer key's by default, so a schema probe asks about
behaviour and shape (which insert fails, which columns are `NOT NULL`), never about names the
learner was free to choose, such as a constraint's.

`check(result, b)` is optional, for rules a comparison cannot see. It receives every probe's
raw result, and, when the frontmatter says `explain: true`, the plan of the learner's query
from `EXPLAIN (FORMAT JSON)`. "Use a window function" is then a `WindowAgg` node in
Postgres's own plan, never a substring of the text.

## How it is graded

**Two datasets.** Every grade runs on the sitting's seed, which is the data the learner sees
results for, and on a second seed derived from it that is never shown. A query that returns a
hard-coded `VALUES` list matching the visible data fails the hidden one. Its failure message
says only that the query passes on the shown data and not on other data, and which part
differed (row count, a column, a value), never the hidden rows.

**Comparison.** Column names must match, since the spec names every column to return and
aliasing is part of the lesson. Values compare by their JSON value, with numbers compared as
decimals so `2.50` and `2.5` are equal; a column's type is not compared, so `count(*)` as
`bigint` and a learner's `int` agree. Unordered results compare as multisets. The first
difference found is the message: a missing column, a row count, or row N with the expected
and actual values side by side, for the visible dataset.

**Errors.** Postgres reports an error's character position. The grader turns it into a line in
`task.sql` and returns it as a diagnostic, so the editor draws it through the same diagnostics
channel a parser error already uses, with the SQLSTATE in the message.

**Verdict fingerprint** `s1:`: the grader's files, `schema.sql`, the PGlite pin and
`sqlrun.mjs`.

## Engine

[PGlite](https://github.com/electric-sql/pglite), Postgres 18 compiled to WASM, run by the
Node that basedpyright already ships (`nodejs_wheel`), in the image and in the dev venv alike.
No database server, no socket, no new Python dependency.

**Pin.** `tools.py` gains `pglite`: the npm tarball, pinned by sha256. Every earlier pin is
one executable out of an archive; this one is a directory (`pglite.wasm`, `initdb.wasm`,
`pglite.data`, the JS). `doctor --fetch` checks the tarball and unpacks it to
`tools/pglite-<version>/`, and before every run the directory is checked against a pinned
digest, reusing the length-prefixed set digest the schema set already has. The image fetches
it at build time beside kubeconform, so a learner never downloads anything.

**Runner.** `kind.grade` → `runner.run_manifest` → the sandboxed `grading.py` →
`grade_sql(job)`, which spawns `node sqlrun.mjs job.json`. `sqlrun.mjs` ships inside the
package. One Node process runs a fresh in-memory PGlite instance per side per dataset: learner
and answer key, visible and hidden. Each instance loads `schema.sql`, inserts the rows, runs
its SQL, then its probes, and the process prints JSON: rows with column names, or an error
with SQLSTATE and position. Python compares and runs `check()`, so every rule a task author
writes stays in Python, as in every other kind. A separate instance per side means the
learner's SQL cannot touch the answer key's database, `DROP TABLE` included.

**Sandbox.** The Node child inherits the grading child's Landlock ruleset, widened to read the
Node directory and the PGlite directory. TCP stays denied. The sandbox's `RLIMIT_AS` is 4 GB,
and V8 reserves about 10 GB of address space per WASM memory; Node's
`--disable-wasm-trap-handler` trades that reservation for explicit bounds checks and is the
intended fix. If it fails, the cap is raised for this job alone.

**Limits.** `statement_timeout` relies on signals WASM does not have. The existing wall-clock
kill on the grading child is the limit, and a runaway `WITH RECURSIVE` ends as "grading did
not finish within Ns".

**Speed.** Each instance runs `initdb` on start. If that dominates a grade, `doctor --fetch`
builds one data directory with `dumpDataDir` and every instance starts from it with
`loadDataDir`. Measured before it is built.

## Surfaces

- **Editor.** Monaco's built-in `pgsql` language, registered beside python, yaml and
  dockerfile. No SQL language server.
- **You get.** `schema.sql` in the file tabs, through `kind.chart()`. There is no data tab:
  the learner explores with `SELECT * FROM orders` and Run, which is free.
- **Result panel.** A result grid: the learner's rows under their column names and, on a
  mismatch, the expected rows beside them with the first difference marked. This is a new
  component, requested from the maintainers per AGENTS.md; until it exists the panel falls
  back to the text report the other non-Python kinds show.
- **Catalogue.** Track `sql`, in the track rail with a logo from devicon like the others. SQL
  tags follow the tag rule (a concept some other task could practise too): `joins`,
  `aggregates`, `window-functions`, `cte`, `null-handling`, `jsonb`, `upsert`, `constraints`,
  `migrations`, `triggers`, `dates`.
- **Missing grader.** A SQL task with PGlite absent says so and names `drillion doctor
  --fetch`, as a manifest task with kubeconform absent already does.
- **Upgrades and backups.** Whole-file artifact, like a manifest: nothing new.
- **Run modes.** The image carries the pin; the checkout fetches it with `doctor --fetch`.
  Verified in the image, since only it is what learners run.

## Proof

- **selfcheck** runs `solution.sql` as the learner's file, on both datasets.
- **doctor** rejects a SQL task whose `schema.sql` does not load, whose answer key fails on
  the self-check seed, whose query returns no rows on either dataset, or whose result is the
  same on both datasets (a task that cannot tell a hard-coded answer from a real one).
- **pytest** for the comparison (ordered and multiset, decimals, missing columns), for mapping
  an error position to a line, and for the pin's directory digest.
- **screens**: one SQL task added to the Playwright set, light and dark.

## Docs

- ADR 0012, "a SQL task runs on PGlite": the options were PGlite, pinned Postgres binaries
  with a supervised server, and emulation on sqlite. Emulation was rejected because a wrong
  dialect teaches wrong answers; a server was rejected for this scope because nothing here
  needs a second session.
- `CONTEXT.md`: `schema.sql` as the SQL kind's **chart** analogue, **probe**, **dataset**
  (visible and hidden); the task counts.
- `docs/authoring-tasks.md`: a SQL section (the three shapes, `rows`, `probes`, `ordered`).

## The first fifteen tasks (324 to 338)

| # | Task | Shape | What it drills |
|---|------|-------|----------------|
| 324 | first select | query | `WHERE`, `ORDER BY`, `LIMIT`, column aliases |
| 325 | group and count | query | `GROUP BY`, `HAVING`, `count` vs `count(col)` |
| 326 | inner join | query | joining on a key, qualifying columns |
| 327 | left join and NULL | query | `LEFT JOIN`, `COALESCE`, why `= NULL` is never true |
| 328 | who never ordered | query | anti-join with `NOT EXISTS`, the `NOT IN` NULL trap |
| 329 | CTE | query | `WITH`, one step per name |
| 330 | top N per group | query | `row_number()` over a partition |
| 331 | running total | query | `sum() OVER (ORDER BY ...)`, `lag()` |
| 332 | days with no sales | query | `generate_series`, `date_trunc`, filling gaps |
| 333 | latest per customer | query | `DISTINCT ON`, a Postgres-only answer to 330's shape |
| 334 | JSONB | query | `->>`, `@>`, a JSON column read as rows |
| 335 | upsert | data | `INSERT ... ON CONFLICT DO UPDATE`, `RETURNING` |
| 336 | first schema | schema | primary and foreign keys, `CHECK`, `UNIQUE`, `ON DELETE` |
| 337 | safe migration | schema | adding a `NOT NULL` column to a table that has rows |
| 338 | updated_at trigger | schema | a PL/pgSQL trigger function |

## Not now

- Transactions, isolation levels, locks, roles and `GRANT`s.
- Indexes and `EXPLAIN` as a subject (a plan is read only to enforce a rule).
- A SQL language server, `psql` meta-commands, extensions beyond PGlite's own.
