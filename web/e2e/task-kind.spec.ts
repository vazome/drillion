import { expect, test } from "@playwright/test";

/** A manifest is edited as YAML and never meets the python language server. Switching
 *  between kinds has to leave the right mode and the right text behind every time: a stale
 *  model is the failure this guards, and it looks like the previous task's code. */
for (const unavailable of [false, true]) {
  test(`task kinds switch without stale models with LSP ${unavailable ? "unavailable" : "available"}`, async ({ page, request }) => {
    const response = await request.get("/api/task/008_slicing");
    expect(response.ok()).toBe(true);
    const template = await response.json();
    const errors: string[] = [];
    page.on("pageerror", (error) => errors.push(error.message));
    let connections = 0;
    await page.routeWebSocket("**/lsp", (socket) => {
      connections++;
      if (unavailable) {
        socket.close();
        return;
      }
      socket.onMessage((message) => {
        const rpc = JSON.parse(String(message));
        if (rpc.id !== undefined) socket.send(JSON.stringify({
          jsonrpc: "2.0", id: rpc.id,
          result: rpc.method === "initialize" ? { capabilities: {} } : null,
        }));
      });
    });
    await page.route("**/api/task/kind-*", (route) => {
      const slug = route.request().url().split("/").at(-1)!;
      const manifest = slug === "kind-manifest";
      return route.fulfill({ json: {
        ...template, slug, attempt: null, reference: null,
        meta: { ...template.meta, kind: manifest ? "manifest" : "python",
          tier: manifest ? undefined : "core", track: manifest ? "kubernetes" : undefined },
        code: manifest ? "apiVersion: v1\nkind: Pod\n" : `def solve():\n    return "${slug}"\n`,
      } });
    });

    // opening a manifest first: the server is never asked for, and the track stands in for
    // the tier a manifest task need not carry
    await page.goto("/#/task/kind-manifest");
    // Monaco takes the language off the file name, so the uri is the mode.
    const editor = page.locator(".monaco-editor[data-uri]").first();
    await expect(editor).toHaveAttribute("data-uri", /\.yaml$/);
    await expect(page.locator('[title^="kubernetes/"]')).toBeVisible();
    expect(connections).toBe(0);

    for (const slug of ["kind-python", "kind-second", "kind-manifest", "kind-python", "kind-manifest"]) {
      await page.evaluate((next) => { location.hash = `#/task/${next}`; }, slug);
      const manifest = slug === "kind-manifest";
      await expect(editor).toHaveAttribute("data-uri", manifest ? /\.yaml$/ : /\.py$/);
      await expect(editor.locator(".view-lines")).toContainText(manifest ? "apiVersion" : slug);
    }
    // a live client is a per-page singleton, so python asks for it once however often it is
    // shown; a refused one is only given up on after the library's 5s connect timeout
    if (!unavailable) expect(connections).toBe(1);
    expect(errors).toEqual([]);
  });
}

/** A language server that goes away mid-session (the bridge dies, the container restarts)
 *  must not cost completions for the rest of the page: the next python task asks again. */
test("a dropped language server reconnects on the next python task", async ({ page, request }) => {
  const template = await (await request.get("/api/task/008_slicing")).json();
  let connections = 0;
  await page.routeWebSocket("**/lsp", (socket) => {
    const first = ++connections === 1;
    socket.onMessage((message) => {
      const rpc = JSON.parse(String(message));
      if (rpc.id === undefined) return;
      socket.send(JSON.stringify({ jsonrpc: "2.0", id: rpc.id, result: rpc.method === "initialize" ? { capabilities: {} } : null }));
      if (first && rpc.method === "initialize") setTimeout(() => socket.close(), 500);
    });
  });
  await page.route("**/api/task/kind-*", (route) => {
    const slug = route.request().url().split("/").at(-1)!;
    return route.fulfill({ json: {
      ...template, slug, attempt: null, reference: null,
      meta: { ...template.meta, kind: "python", tier: "core" },
      code: `def solve():\n    return "${slug}"\n`,
    } });
  });

  await page.goto("/#/task/kind-first");
  const editor = page.locator(".monaco-editor[data-uri]").first();
  await expect(editor.locator(".view-lines")).toContainText("kind-first");
  await expect.poll(() => connections).toBe(1);
  // the drop lands, then a python task opens
  await page.waitForTimeout(1500);
  await page.evaluate(() => { location.hash = "#/task/kind-second"; });
  await expect(editor.locator(".view-lines")).toContainText("kind-second");
  await expect.poll(() => connections).toBe(2);
});
