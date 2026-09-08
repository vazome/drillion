# SQLite progress and recoverable task resets

Progress now lives in `progress.sqlite3`, using Python's standard-library `sqlite3`. Atomic
JSON replacement did not coordinate separate processes or guarantee power-loss durability;
every heartbeat also rewrote the entire archive. SQLite owns locking and durable commits,
with a rollback journal and `synchronous=EXTRA`, on a local filesystem.

Keep the existing dictionary interface used by the scheduler and API. Each card, attempt,
note, log entry and archived solution is a separate row; record payloads remain JSON to
preserve historical and unknown fields without an ORM or a parallel domain model. Only changed
rows are written. Requests still load the full state and serialize it to detect changes:
this is appropriate for one learner, but targeted reads belong here if measured history size
makes that expensive. This is not a database intended for shared multi-user hosting.

Import legacy JSON and stamp the SQLite version in one transaction. Preserve the original
JSON bytes and never re-import once the database is initialized. This supersedes ADR 0002's
no-migration consequence, while preserving its rule that personal history is never shipped.
Old JSON-only releases cannot read subsequent SQLite progress; stop old servers before import.

SQLite cannot transact a task-file replacement. Submit and Abandon therefore commit both the
archive and a pending reset before touching the task region. Every subsequent state access
finishes pending resets under the database write lock, and clears the intent only after the
replacement is synced. Recovery preserves changed external code and the current machinery.
This closes the archive-loss window without making task files database-owned blobs.

Backups remain necessary; copy the whole root with servers stopped. Stable task identifiers
remain a separate decision under ADR 0005: SQLite does not repair orphaned slugs.
