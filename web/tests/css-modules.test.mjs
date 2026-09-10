import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { test } from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { createServer } from "vite";

test("CSS Modules resolve every component class and preserve renderer contracts", async () => {
  const root = fileURLToPath(new URL("../", import.meta.url));
  const server = await createServer({
    root, configFile: false, appType: "custom",
    server: { middlewareMode: true, ws: false, watch: null },
  });
  try {
    for (const file of await readdir(new URL("../src/ds/", import.meta.url))) {
      if (!file.endsWith(".jsx")) continue;
      const source = await readFile(new URL(`../src/ds/${file}`, import.meta.url), "utf8");
      const imported = source.match(/import (\w+) from "\.\/(\w+\.module\.css)"/);
      if (!imported) continue;
      const [, name, css] = imported;
      const { default: classes } = await server.ssrLoadModule(`/src/ds/${css}`);
      for (const match of source.matchAll(new RegExp(`\\b${name}\\.(\\w+)`, "g"))) {
        assert.ok(classes[match[1]], `${file}: missing CSS class ${match[1]}`);
      }
    }

    const ds = await server.ssrLoadModule("/src/ds/index.js");
    const render = (name, props) => renderToStaticMarkup(createElement(ds[name], props));
    const spec = render("SpecText", {
      slug: "example", text: "## Heading\n\n> [!NOTE]\n> Read this\n\n1. First\n\n![asset](assets/example.png)\n\n```python\nreturn 42\n```",
    });
    assert.match(spec, /class="markdown-alert-title"/);
    assert.match(spec, /<ol class="_[^"]+">/);
    assert.match(spec, /src="\/api\/task\/example\/assets\/assets\/example.png"/);
    assert.match(spec, /data-tok="keyword">return/);
    assert.match(spec, /<pre tabindex="0" class="_[^"]+">/);
    assert.doesNotMatch(spec, /class="[^"]*undefined/);

    const toggle = render("Toggle", { checked: true, disabled: true, ariaLabel: "Timer" });
    assert.match(toggle, /aria-checked="true"/);
    assert.match(toggle, /data-checked=""/);
    assert.doesNotMatch(toggle, /data-on=/);
    const nudge = render("StuckNudge", { hintReady: false });
    assert.match(nudge, /disabled="">Show hint 1/);
    assert.doesNotMatch(nudge, /bury|tomorrow/i);
    const table = render("Table", {
      columns: [{ key: "title", label: "Title", sortable: true }],
      sortKey: "title", sortDir: "asc", onSort() {},
    });
    assert.match(table, /aria-sort="ascending"/);
    assert.match(table, /aria-label="Sort by Title descending"/);
  } finally {
    await server.close();
  }
});
