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

const [first, second, third] = process.argv.slice(2);
if (first === "--snapshot") await snapshot(second, third);
// PGlite keeps the event loop alive, so a finished run has to say so
process.exit(0);
