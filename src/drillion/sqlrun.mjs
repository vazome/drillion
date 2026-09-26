// How drillion runs SQL on PGlite. Two uses:
//   node sqlrun.mjs --snapshot <pglite dir> <out.tar.gz>   once, when PGlite is fetched
//   node sqlrun.mjs <job.json> <out.json>                  every SQL grade, in the sandbox
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const load = async (dir) => (await import(pathToFileURL(join(dir, "index.js")).href)).PGlite;

async function snapshot(dir, out) {
  const PGlite = await load(dir);
  const db = await PGlite.create();
  await db.exec("CREATE EXTENSION IF NOT EXISTS plpgsql");
  const file = await db.dumpDataDir("gzip");
  writeFileSync(out, Buffer.from(await file.arrayBuffer()));
}

// every type's parser replaced by the identity: values come back as Postgres's own text,
// which keeps a bigint whole and a timestamp free of JavaScript's time zone
const same = (x) => x;
const TEXT = {};
for (let oid = 0; oid < 65536; oid++) TEXT[oid] = same;
const AS_TEXT = { parsers: TEXT, rowMode: "array" };
const MAX_ROWS = 1000;

const ident = (name) => `"${String(name).replaceAll('"', '""')}"`;
const error = (e) => ({
  code: e?.code ?? null,
  message: String(e?.message ?? e),
  position: e?.position ? Number(e.position) : null,
});

// what a script returned: its last statement that had columns
function last(results) {
  for (let i = results.length - 1; i >= 0; i--) {
    const r = results[i];
    if (r.fields?.length) {
      return { fields: r.fields.map((f) => f.name), rows: r.rows.slice(0, MAX_ROWS), count: r.rows.length };
    }
  }
  return null;
}

// a learner's unfinished transaction ends here, as a closed psql session's would; then
// every schema they could have made goes, and the settings DISCARD clears
async function reset(db) {
  await db.exec("ROLLBACK");
  await db.exec("DISCARD ALL");
  const { rows } = await db.query(
    "SELECT nspname FROM pg_namespace WHERE nspname NOT LIKE 'pg\\_%' AND nspname <> 'information_schema'",
    [],
    { rowMode: "array" },
  );
  for (const [name] of rows) await db.exec(`DROP SCHEMA ${ident(name)} CASCADE`);
  await db.exec("CREATE SCHEMA public");
}

async function insert(db, tables) {
  for (const [table, rows] of Object.entries(tables)) {
    for (const row of rows) {
      const cols = Object.keys(row);
      const slots = cols.map((_, i) => `$${i + 1}`).join(", ");
      await db.query(
        `INSERT INTO ${ident(table)} (${cols.map(ident).join(", ")}) VALUES (${slots})`,
        cols.map((c) => row[c]),
      );
    }
  }
}

async function run(db, schema, pass) {
  await reset(db);
  try {
    await db.exec(schema);
    await insert(db, pass.rows);
  } catch (e) {
    return { setup: error(e) };
  }
  const out = { result: null, error: null, probes: {}, plan: null };
  try {
    out.result = last(await db.exec(pass.sql, AS_TEXT));
  } catch (e) {
    out.error = error(e);
    return out;
  }
  await db.exec("ROLLBACK");
  if (pass.explain && out.result) {
    try {
      out.plan = (await db.query(`EXPLAIN (FORMAT JSON) ${pass.sql}`, [], AS_TEXT)).rows[0][0];
    } catch {
      out.plan = null;
    }
  }
  for (const [name, sql] of pass.probes) {
    await db.exec("BEGIN");
    try {
      out.probes[name] = last(await db.exec(sql, AS_TEXT)) ?? { fields: [], rows: [], count: 0 };
    } catch (e) {
      out.probes[name] = { error: error(e) };
    }
    await db.exec("ROLLBACK");
  }
  return out;
}

async function grade(jobPath, outPath) {
  const job = JSON.parse(readFileSync(jobPath, "utf8"));
  const PGlite = await load(job.pglite);
  const db = await PGlite.create({
    loadDataDir: new Blob([readFileSync(join(job.pglite, "datadir.tar.gz"))]),
  });
  const passes = [];
  for (const pass of job.passes) passes.push(await run(db, job.schema, pass));
  writeFileSync(outPath, JSON.stringify({ passes }));
}

const [first, second, third] = process.argv.slice(2);
if (first === "--snapshot") await snapshot(second, third);
else await grade(first, second);
// PGlite keeps the event loop alive, so a finished run has to say so
process.exit(0);
