// The catalogue's sort order, the payload seam the page reads, and every task's spec
// rendered through SpecText. Needs a running server:
//   DRILLION_PORT=8816 uv run drillion &   then   node check.mjs 8816
import { build } from "esbuild";
import { rmSync } from "node:fs";
import { pathToFileURL } from "node:url";

const port = process.argv[2] || "8765";
const base = `http://127.0.0.1:${port}/api`;
const out = new URL("./.check.bundle.mjs", import.meta.url);

await build({
  stdin: {
    contents: `
      import { renderToStaticMarkup } from "react-dom/server";
      import { SpecText } from "./src/ds/SpecText.jsx";
      export { sortRows } from "./src/Catalogue.tsx";
      export { stepLine } from "./src/Task.tsx";
      export const render = (text, slug) => renderToStaticMarkup(<SpecText text={text} slug={slug} />);
    `,
    resolveDir: ".", loader: "jsx", sourcefile: "check-entry.jsx",
  },
  bundle: true, format: "esm", platform: "node", packages: "external", jsx: "automatic",   // only our JSX is bundled; node resolves the deps
  outfile: out.pathname, logLevel: "error",
});
const { render, sortRows, stepLine } = await import(pathToFileURL(out.pathname).href + "?t=" + Date.now());
rmSync(out.pathname);

// stepLine(grade, box, from_box, stepped, boxes)
if (!stepLine("struggled", 2, 3, true, 7).includes("stepped back")) throw new Error("a demotion must not read as a climb");
if (stepLine("pass", 3, 2, true, 7) !== "the card stepped up") throw new Error("a promotion must read as a climb");
if (!stepLine("quick", 6, 6, false, 7).includes("top box")) throw new Error("a quick pass clamped at the top must say so");
if (!stepLine("struggled", 0, 0, false, 7).includes("first box")) throw new Error("a struggle on the floor must say so");
if (!stepLine("pass", 2, 2, false, 7).includes("keeps the card where it is")) throw new Error("a pass that moved nothing must say so");

const row = (topic, difficulty) => ({ topic, difficulty, title: "t", tier: "core", tags: [], seen: 0, box: 0, status: "new" });
const order = (rows, sort) => sortRows(rows, sort).map((r) => r.topic).join(",");
const spread = [row(3, "medium"), row(1, "hard"), row(2, "easy")];
if (order(spread, { key: "difficulty", dir: "asc" }) !== "2,3,1") throw new Error("difficulty must sort easy → hard");
if (order(spread, { key: "difficulty", dir: "desc" }) !== "1,3,2") throw new Error("difficulty desc must sort hard → easy");
if (order([row(9, "easy"), row(4, "easy")], { key: "difficulty", dir: "desc" }) !== "4,9") throw new Error("ties must fall back to the task number, ascending");

const cat = await (await fetch(`${base}/catalogue`)).json();
const slugs = cat.tasks.map((e) => e.slug);

const ok = (label, cond) => { if (!cond) throw new Error(label); };
ok("today must name the one reason New picks is empty, and only then",
  cat.today.new.length ? cat.today.no_new === null : !!cat.today.no_new?.why);
ok("every row must carry the prereqs it is waiting on",
  cat.tasks.every((e) => Array.isArray(e.blocked)));
ok("today must carry the real backlog and the behind flag",
  typeof cat.today.due_total === "number" && typeof cat.today.behind === "boolean");
ok("stats.due is the whole backlog, never the capped list's length", cat.stats.due === cat.today.due_total);
ok("stats must carry the lapse limit the rows are flagged against", cat.stats.lapse_limit > 0);
ok("every row must carry its lapse count", cat.tasks.every((e) => typeof e.lapses === "number"));
ok("every row must carry lowercased spec text",
  cat.tasks.every((e) => e.text && e.text === e.text.toLowerCase() && !e.text.includes("\n")));
const hit = (n) => cat.tasks.filter((e) => e.text.includes(n)).length;
ok("search must reach words no title carries", hit("finance") > 0 && hit("dictionary") > 0);
console.log(`catalogue payload ${(JSON.stringify(cat).length / 1024).toFixed(0)} KiB for ${slugs.length} tasks`);
let checked = 0;
const problems = [];

for (const slug of slugs) {
  const task = await (await fetch(`${base}/task/${encodeURIComponent(slug)}`)).json();
  let markup;
  try { markup = render(task.spec_md, slug); }
  catch (e) { problems.push(`${slug}: threw ${e.message}`); continue; }

  for (const kind of ["NOTE", "TIP", "WARNING", "IMPORTANT", "CAUTION"]) {
    if (markup.includes(`[!${kind}]`)) problems.push(`${slug}: literal [!${kind}] in output`);
  }
  const alerts = (task.spec_md.match(/^> \[!\w+\]/gm) || []).length;
  const titled = (markup.match(/class="markdown-alert-title"/g) || []).length;
  if (alerts !== titled) problems.push(`${slug}: ${alerts} callouts, ${titled} styled labels`);
  const heads = [...task.spec_md.matchAll(/^## (.+)$/gm)].map((m) => m[1].trim());
  const rendered = (markup.match(/<h2[^>]*>/g) || []).length;
  if (heads.length !== rendered) problems.push(`${slug}: ${heads.length} '## ' headings, ${rendered} <h2>`);
  if (/^\d+\. /m.test(task.spec_md) && !markup.includes("<ol")) problems.push(`${slug}: ordered list did not render as <ol>`);
  if (/^\s*[-*] /m.test(task.spec_md) && !markup.includes("<ul")) problems.push(`${slug}: bullet list did not render as <ul>`);
  if (markup.includes("undefined")) problems.push(`${slug}: 'undefined' leaked into the markup`);
  checked++;
}

console.log(`${checked}/${slugs.length} specs rendered`);
if (problems.length) { console.error(problems.slice(0, 20).join("\n")); process.exit(1); }
console.log("ok — no leaked markers, headings and lists intact");
