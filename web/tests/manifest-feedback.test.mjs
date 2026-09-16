import assert from "node:assert/strict";
import { test } from "node:test";
import { createServer } from "vite";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

test("manifest feedback preserves field diagnostics and falls back without inventing a verdict", async () => {
  const server = await createServer({ root: new URL("../", import.meta.url).pathname, configFile: false, server: { middlewareMode: true, ws: false, watch: null } });
  try {
    const { manifestFeedback } = await server.ssrLoadModule("/src/manifestFeedback.ts");
    const feedback = manifestFeedback("E   AssertionError: /spec/replicas: expected integer, but got string\nE   /metadata/name: too long\nE   assert 1 == 0");
    assert.deepEqual(feedback.fields, [
      { path: "/spec/replicas", message: "expected integer, but got string" },
      { path: "/metadata/name", message: "too long" },
    ]);
    assert.match(manifestFeedback("E   AssertionError: replicas\nE   assert 3 == 2").message, /spec.replicas/);
    assert.match(manifestFeedback("E   AssertionError: name").message, /metadata.name/);
    assert.match(manifestFeedback("E   AssertionError: expected one document, found 2").message, /found 2/);
    assert.match(manifestFeedback("E   yaml.parser.ParserError: bad YAML").message, /checker problem/);
    assert.match(manifestFeedback("timed out after 60s").message, /checker problem/);
    const { ManifestHelp, ManifestFailure, ManifestBrief } = await server.ssrLoadModule("/src/ManifestWorkspace.tsx");
    const render = (component, props) => renderToStaticMarkup(createElement(component, props));
    const help = render(ManifestHelp, { code: "", onChange() {}, disabled: false });
    assert.match(help, /Insert outline/);
    assert.match(help, /incomplete/);
    assert.doesNotMatch(help, /undefined/);
    const failure = render(ManifestFailure, { headline: "E   AssertionError: /spec/replicas: expected integer, but got string" });
    assert.match(failure, /without quotes/);
    assert.match(failure, /data-state="failed"/);
    assert.match(failure, /kubeconform/);
    assert.match(failure, /data-wrong/);
    assert.match(failure, /\/spec\/replicas/);
    assert.doesNotMatch(failure, /undefined|Your output|Expected/);
    assert.doesNotMatch(failure, /AssertionError/);
    const { FailedCase } = await server.ssrLoadModule("/src/ds/FailedCase.jsx");
    const python = render(FailedCase, { case: { args: { n: "2" }, expected: "4", actual: "3", source: "assert solve(n) == 4" } });
    assert.match(python, /Input/);
    assert.match(python, /Your output/);
    assert.match(python, /Expected/);
    assert.match(python, /data-wrong/);
    assert.match(python, /data-right/);
    const brief = render(ManifestBrief, { text: "## You return\nA Deployment named `billing` with 4 replicas.", slug: "example", started: true });
    assert.match(brief, /billing/);
    assert.match(brief, /4 replicas/);
  } finally { await server.close(); }
});
