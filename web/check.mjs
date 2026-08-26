// One check: render every drill's spec through SpecText and assert nothing leaks or throws.
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
      export const render = (text, slug) => renderToStaticMarkup(<SpecText text={text} slug={slug} />);
    `,
    resolveDir: ".", loader: "jsx", sourcefile: "check-entry.jsx",
  },
  bundle: true, format: "esm", platform: "node", packages: "external", jsx: "automatic",   // only our JSX is bundled; node resolves the deps
  outfile: out.pathname, logLevel: "error",
});
const { render } = await import(pathToFileURL(out.pathname).href + "?t=" + Date.now());
rmSync(out.pathname);

const cat = await (await fetch(`${base}/catalogue`)).json();
const slugs = cat.exercises.map((e) => e.slug);
let checked = 0;
const problems = [];

for (const slug of slugs) {
  const ex = await (await fetch(`${base}/ex/${encodeURIComponent(slug)}`)).json();
  let html;
  try { html = render(ex.spec_md, slug); }
  catch (e) { problems.push(`${slug}: threw ${e.message}`); continue; }

  // an unparsed GitHub alert marker means the alert plugin stopped firing
  for (const kind of ["NOTE", "TIP", "WARNING", "IMPORTANT", "CAUTION"]) {
    if (html.includes(`[!${kind}]`)) problems.push(`${slug}: literal [!${kind}] in output`);
  }
  // every `## Heading` in the source must come out as an <h2>
  const heads = [...ex.spec_md.matchAll(/^## (.+)$/gm)].map((m) => m[1].trim());
  const rendered = (html.match(/<h2[^>]*>/g) || []).length;
  if (heads.length !== rendered) problems.push(`${slug}: ${heads.length} '## ' headings, ${rendered} <h2>`);
  // ordered lists must not degrade into paragraphs (the old regex parser's failure)
  if (/^\d+\. /m.test(ex.spec_md) && !html.includes("<ol")) problems.push(`${slug}: ordered list did not render as <ol>`);
  if (/^\s*[-*] /m.test(ex.spec_md) && !html.includes("<ul")) problems.push(`${slug}: bullet list did not render as <ul>`);
  if (html.includes("undefined")) problems.push(`${slug}: 'undefined' leaked into the markup`);
  checked++;
}

console.log(`${checked}/${slugs.length} specs rendered`);
if (problems.length) { console.error(problems.slice(0, 20).join("\n")); process.exit(1); }
console.log("ok — no leaked markers, headings and lists intact");
