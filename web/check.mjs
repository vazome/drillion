// One check: the catalogue's sort order, then every task's spec rendered through SpecText
// with an assert that nothing leaks or throws.
// Needs a running server:  DRILLION_PORT=8816 uv run drillion &   then  node check.mjs [port]
import { build } from "esbuild";
import { readFileSync, rmSync } from "node:fs";
import { pathToFileURL } from "node:url";

const port = process.argv[2] || "8765";
const base = `http://127.0.0.1:${port}/api`;
const out = new URL("./.check.bundle.mjs", import.meta.url);

await build({
  stdin: {
    contents: `
      import { renderToStaticMarkup } from "react-dom/server";
      import { SpecText } from "./src/ds/SpecText.jsx";
      export { sortRows, blockedBy, noPicks } from "./src/Catalogue.tsx";
      export const render = (text, slug) => renderToStaticMarkup(<SpecText text={text} slug={slug} />);
      export const html = (node) => renderToStaticMarkup(node);
    `,
    resolveDir: ".", loader: "jsx", sourcefile: "check-entry.jsx",
  },
  bundle: true, format: "esm", platform: "node", packages: "external", jsx: "automatic",   // only our JSX is bundled; node resolves the deps
  outfile: out.pathname, logLevel: "error",
});
const { render, html, sortRows, blockedBy, noPicks } = await import(pathToFileURL(out.pathname).href + "?t=" + Date.now());
rmSync(out.pathname);

// The catalogue sorts on meaning, not on the alphabet, and ties fall back to the task number.
const row = (topic, difficulty) => ({ topic, difficulty, title: "t", tier: "core", tags: [], seen: 0, box: 0, status: "new" });
const order = (rows, sort) => sortRows(rows, sort).map((r) => r.topic).join(",");
const spread = [row(3, "medium"), row(1, "hard"), row(2, "easy")];
if (order(spread, { key: "difficulty", dir: "asc" }) !== "2,3,1") throw new Error("difficulty must sort easy → hard");
if (order(spread, { key: "difficulty", dir: "desc" }) !== "1,3,2") throw new Error("difficulty desc must sort hard → easy");
if (order([row(9, "easy"), row(4, "easy")], { key: "difficulty", dir: "desc" }) !== "4,9") throw new Error("ties must fall back to the task number, ascending");

// A locked row must name what it is waiting for, and the Today card must name the one reason
// New picks is empty rather than listing all of them (#11). Both re-run rules that live in
// src/drillion/scheduler.py, so they are the pair most likely to drift away from the server.
const ok = (label, cond) => { if (!cond) throw new Error(label); };
const t = (topic, over = {}) => ({ ...row(topic, "easy"), slug: `${topic}`, prereqs: [], lapses: 0, ...over });
const map = (rows) => new Map(rows.map((r) => [r.topic, r]));

const box0 = t(1), box1 = t(2, { seen: 1, box: 1 });
const gated = t(5, { prereqs: [1, 2] });
ok("an unmet prereq must show", blockedBy(gated, map([box0, box1, gated]), null).length === 1);
ok("box 1 clears a prereq; box 0 does not", blockedBy(gated, map([box0, box1, gated]), null)[0].topic === 1);
ok("a prereq that is not in the catalogue is ignored", blockedBy(t(6, { prereqs: [99] }), map([]), null).length === 0);
ok("a card already seen is never blocked", blockedBy(t(7, { seen: 1, prereqs: [1] }), map([box0]), null).length === 0);
const out_of_focus = t(1, { tier: "advanced" });
ok("under a focus, a prereq outside it is ignored",
  blockedBy(t(8, { prereqs: [1] }), map([out_of_focus]), "core").length === 0);

const day = (over = {}) => ({ review: [], new: [], recent: [], done_today: 0, due_total: 0, behind: false, ...over });
const why = (rows, focus, today) =>
  noPicks(rows, new Map(rows.map((r) => [r.slug, blockedBy(r, map(rows), focus)])), focus, today);
// the order matters as much as the answers: the backlog holds everything, so it is named
// before the cap, and the cap before a prereq that was never the reason today
const CASES = [
  ["behind", [t(1)], null, day({ behind: true, due_total: 40, review: Array(12) })],
  ["cap", [t(1)], null, day({ done_today: 2 })],
  // #1 is seen but still in box 0 — a first pass graded `struggled` clears no prereq
  ["prereqs", [t(1, { seen: 1, box: 0 }), t(5, { prereqs: [1] })], null, day()],
  ["focus", [t(1, { tier: "advanced" })], "core", day()],
  ["done", [t(1, { seen: 1, box: 2 })], null, day()],
];
for (const [reason, rows, focus, today] of CASES) {
  const got = why(rows, focus, today);
  ok(`New picks must blame ${reason}, not ${got.why}`, got.why === reason);
  const markup = html(got.message);
  ok(`the ${reason} copy must render`, markup.length > 20 && !markup.includes("undefined"));
}

const cat = await (await fetch(`${base}/catalogue`)).json();
const slugs = cat.tasks.map((e) => e.slug);

// The payload seam the page reads: a capped review list next to the real backlog, the lapse
// limit the rows are flagged against, and the spec text the search box matches on (#14).
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
  let html;
  try { html = render(task.spec_md, slug); }
  catch (e) { problems.push(`${slug}: threw ${e.message}`); continue; }

  // an unparsed GitHub alert marker means the alert plugin stopped firing
  for (const kind of ["NOTE", "TIP", "WARNING", "IMPORTANT", "CAUTION"]) {
    if (html.includes(`[!${kind}]`)) problems.push(`${slug}: literal [!${kind}] in output`);
  }
  // …and a callout whose label lost its class renders unstyled, with the raw octicon showing
  const alerts = (task.spec_md.match(/^> \[!\w+\]/gm) || []).length;
  const titled = (html.match(/class="markdown-alert-title"/g) || []).length;
  if (alerts !== titled) problems.push(`${slug}: ${alerts} callouts, ${titled} styled labels`);
  // every `## Heading` in the source must come out as an <h2>
  const heads = [...task.spec_md.matchAll(/^## (.+)$/gm)].map((m) => m[1].trim());
  const rendered = (html.match(/<h2[^>]*>/g) || []).length;
  if (heads.length !== rendered) problems.push(`${slug}: ${heads.length} '## ' headings, ${rendered} <h2>`);
  // ordered lists must not degrade into paragraphs (the old regex parser's failure)
  if (/^\d+\. /m.test(task.spec_md) && !html.includes("<ol")) problems.push(`${slug}: ordered list did not render as <ol>`);
  if (/^\s*[-*] /m.test(task.spec_md) && !html.includes("<ul")) problems.push(`${slug}: bullet list did not render as <ul>`);
  if (html.includes("undefined")) problems.push(`${slug}: 'undefined' leaked into the markup`);
  checked++;
}

console.log(`${checked}/${slugs.length} specs rendered`);
if (problems.length) { console.error(problems.slice(0, 20).join("\n")); process.exit(1); }
console.log("ok — no leaked markers, headings and lists intact");
