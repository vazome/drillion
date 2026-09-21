import assert from "node:assert/strict";
import { test } from "node:test";
import { createServer } from "vite";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

test("manifest failures render the grader's diagnostics as they arrive", async () => {
  const server = await createServer({ root: new URL("../", import.meta.url).pathname, configFile: false, server: { middlewareMode: true, ws: false, watch: null } });
  try {
    const { ManifestFailure } = await server.ssrLoadModule("/src/ManifestWorkspace.tsx");
    const render = (component, props) => renderToStaticMarkup(createElement(component, props));

    // a field the validator named: its path, its message, and the validator credited
    const field = render(ManifestFailure, { diagnostics: [
      { path: "/spec/replicas", message: "expected integer, but got string" },
      { path: "/metadata/name", message: "too long" },
    ] });
    assert.match(field, /data-state="failed"/);
    assert.match(field, /Check these manifest fields/);
    assert.match(field, /kubeconform/);
    assert.match(field, /\/spec\/replicas/);
    assert.match(field, /\/metadata\/name/);
    assert.match(field, /data-wrong/);
    assert.match(field, /without quotes/);

    // a requirement check() missed: a sentence about the document, and no validator credit
    const missed = render(ManifestFailure, { diagnostics: [
      { path: null, message: "metadata.name is 'web', and it should be 'checkout'" },
    ] });
    assert.match(missed, /Your manifest needs another look/);
    assert.match(missed, /should be &#x27;checkout&#x27;/);
    assert.doesNotMatch(missed, /kubeconform/);
    assert.doesNotMatch(missed, /undefined|null|AssertionError/);

    const { FailedCase } = await server.ssrLoadModule("/src/ds/FailedCase.jsx");
    const python = render(FailedCase, { case: { args: { n: "2" }, expected: "4", actual: "3", source: "assert solve(n) == 4" } });
    assert.match(python, /Input/);
    assert.match(python, /Your output/);
    assert.match(python, /Expected/);
    assert.match(python, /data-wrong/);
    assert.match(python, /data-right/);
  } finally { await server.close(); }
});
