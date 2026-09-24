import assert from "node:assert/strict";
import { test } from "node:test";
import { createServer } from "vite";

test("splitter bounds keep each pane its minimum and leave room for the editor", async () => {
  // prefs subscribes to cross-tab events at module load; no browser is needed for the bounds.
  const previous = globalThis.addEventListener;
  globalThis.addEventListener = () => {};
  const server = await createServer({ root: new URL("../", import.meta.url).pathname, configFile: false, server: { middlewareMode: true, ws: false, watch: null } });
  try {
    const { paneBounds, resultBounds } = await server.ssrLoadModule("/src/TaskPanes.tsx");
    for (const width of [900, 1000, 1200, 1600, 2200]) {
      const { min, max } = paneBounds(width);
      assert.ok(Math.abs(min / 100 * width - 340) < 0.001);
      assert.ok(max <= 70);
      assert.ok(max >= min);
      assert.ok(width * (1 - max / 100) - 20 >= 420 - 0.001);
    }
    assert.equal(paneBounds(2200).max, 70);
    assert.ok(Math.abs(paneBounds(1000).max - 56) < 0.001);
    for (const height of [500, 700, 900, 1400]) {
      const { min, max } = resultBounds(height);
      assert.ok(Math.abs(min / 100 * height - 120) < 0.001);
      assert.ok(max >= min && max <= 80);
      // the editor keeps its 240px under the 60px toolbar and the 8px splitter
      assert.ok(height * (1 - max / 100) >= 308 - 0.001);
    }
    assert.equal(resultBounds(2000).max, 80);
  } finally {
    await server.close();
    if (previous === undefined) delete globalThis.addEventListener;
    else globalThis.addEventListener = previous;
  }
});
