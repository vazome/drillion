# A SQL task runs on PGlite

Postgres is the database most teams reach for, and SQL is the one language a Python
programmer is sure to meet beside Python. The question was how to run a learner's Postgres
SQL when the grader runs in a read-only container with every capability dropped, under
Landlock, and with no network.

The design is
[docs/superpowers/specs/2026-09-26-sql-track-design.md](../superpowers/specs/2026-09-26-sql-track-design.md).
The scope is querying, changing data and schema work; transactions, locks, roles and tuning
are left out.

## Considered options

**Emulate Postgres on sqlite**, translating with a library such as sqlglot. Rejected. A
dialect that is almost Postgres teaches answers that fail on the real thing, which is worse
than teaching nothing.

**Pinned Postgres binaries and a supervised server.** Rejected for this scope. It is full
Postgres, and it is what a later transactions and locks track would need, since that is the
one subject that takes a second session. Here it would add a server's lifecycle and crashes,
a Python driver, and more than 10 MB per platform, and it moves the boundary around a
learner's SQL from Landlock to Postgres roles.

**PGlite on the Node that basedpyright already ships.** Taken. PGlite is Postgres 18 compiled
to WASM. It needs no server, no socket and no new Python dependency, and the Node child it
runs in inherits the grading child's Landlock ruleset like any tool a grader starts. It is
one platform-independent pin: the npm tarball by checksum on download, the unpacked tree by
digest before every run.

## Consequences

- **One PGlite instance per grade, reset between four passes**: the answer key and the
  learner's SQL, each on the data shown and on a hidden second dataset. A second instance in
  the same process does not fit the sandbox's 4 GB address-space cap ("Array buffer
  allocation failed"). The key runs first and its rows leave the database as soon as they
  are read, so nothing the learner's SQL does can reach them.
- **Node runs PGlite with `--disable-wasm-trap-handler --liftoff-only`.** Without them V8
  dies compiling the module under that cap ("Fatal process out of memory: Zone"). The cap is
  not raised.
- **`doctor --fetch` builds a data directory** every grade starts from with `loadDataDir`,
  so no grade runs `initdb`: a ready instance in 1.1 s against 3.5 s. It is built with
  PL/pgSQL enabled, and PGlite's extension tarballs are not unpacked, so no other extension
  exists.
- **A learner's query that never ends is their failure, not a 503.** `statement_timeout`
  needs signals WASM lacks, so the grade's wall-clock limit ends it, and `selfcheck` has
  already shown the answer key finishes.
- **Values compare as Postgres text**, numbers as decimals, so JavaScript's numbers and time
  zones never enter a verdict.
- A SQL verdict is fingerprinted `s1:`: the grader and its `db/`, the PGlite pin, and the
  runner.
