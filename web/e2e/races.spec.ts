/** The two races on the task page that only exist in a real browser: the localStorage draft
 *  offered after a save never landed, and the 409 the optimistic lock raises when the file
 *  moved underneath the editor. */
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { expect, test, type Page } from "@playwright/test";
import { port, repoRoot, scratchRoot } from "../playwright.config";

/** Not 001: `screens.spec.ts` photographs a clean pass on that one. */
const SLUG = "002_slicing";
const TASK_PY = join(scratchRoot, "tasks", SLUG, "task.py");
const MARKER = "# ══ machinery";
/** `region.py`'s `splice`, over the checkout's copy — the scratch file is what we rewrite. */
const PRISTINE = readFileSync(join(repoRoot, "tasks", SLUG, "task.py"), "utf8");
const MARKER_AT = PRISTINE.indexOf(MARKER);
if (MARKER_AT < 0) throw new Error(`${SLUG} has no ${MARKER} line: these tests would write a task with no grader`);
const TAIL = PRISTINE.slice(MARKER_AT);
const setDisk = (body: string) => writeFileSync(TASK_PY, `${body}\n\n\n${TAIL}`);

const body = (marker: string) => `def solve(xs):\n    return "${marker}"`;
const STUB = "def solve(xs):\n    raise NotImplementedError";

const editor = (page: Page) => page.locator(".monaco-editor .view-lines").first();

/** insertText, not type(): Monaco auto-indents keystrokes and would mangle the body. */
async function typeCode(page: Page, text: string) {
  await editor(page).click();
  await page.keyboard.press("ControlOrMeta+a");
  await page.keyboard.insertText(text);
}

/** the code save, not `PUT …/note`, which the same debounce can fire alongside it */
const isSave = (r: { method(): string; url(): string }) => r.method() === "PUT" && r.url().endsWith(SLUG);
const putRequest = (page: Page) => page.waitForRequest(isSave);
const putOk = (page: Page) =>
  page.waitForResponse((r) => isSave(r.request()) && r.status() === 200);

test.beforeEach(async ({ page }) => {
  setDisk(STUB);
  // the reloads below leave with a dirty buffer, which arms the beforeunload prompt
  page.on("dialog", (d) => d.accept());
});

/** Give the attempt back: it puts the stub on disk and keeps 002 out of the Open band of
 *  the catalogue and progress screenshots the next spec file takes. */
test.afterAll(async () => {
  const url = `http://127.0.0.1:${port}/api/task/${SLUG}`;
  const { etag } = await (await fetch(url)).json();
  const gone = await fetch(`${url}/abandon`, {
    method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ etag }),
  });
  expect(gone.ok, await gone.text()).toBe(true);
});

test("the page starts the clock by itself, with nothing typed", async ({ page }) => {
  await page.goto(`/#/task/${SLUG}`);
  await expect(page.getByRole("button", { name: "Run tests" })).toBeVisible();
  // reading the task is work: the attempt opens on a timer, not on the first keystroke
  const opened = () => page.evaluate(async (s) => (await (await fetch(`/api/task/${s}`)).json()).attempt !== null, SLUG);
  await expect.poll(opened, { timeout: 10_000 }).toBe(true);
});

test("a draft that never reached the server is offered back, unless the file moved", async ({ page }) => {
  await page.route("**/api/task/*", (route) =>
    route.request().method() === "PUT" ? route.abort() : route.continue());

  await page.goto(`/#/task/${SLUG}`);
  await expect(page.getByRole("button", { name: "Run tests" })).toBeVisible();

  const blocked = putRequest(page);
  await typeCode(page, body("DRAFT"));
  await blocked;                      // the debounce elapsed and the save was refused

  await page.reload();
  await expect(page.getByText("A newer local draft exists for this task.")).toBeVisible();
  await page.getByRole("button", { name: "Restore it" }).click();
  await expect(editor(page)).toContainText('"DRAFT"');

  // the file moves under the draft: same task, new etag, so the draft is no longer about it
  setDisk(body("DISK"));
  await page.reload();
  await expect(editor(page)).toContainText('"DISK"');
  await expect(page.getByText("A newer local draft exists for this task.")).toBeHidden();
});

for (const [action, kept] of [
  ["Reload from disk", "DISK"],
  ["Keep mine", "MINE"],
] as const) {
  test(`a save against a moved file offers both versions — ${action}`, async ({ page }) => {
    await page.goto(`/#/task/${SLUG}`);
    await expect(page.getByRole("button", { name: "Run tests" })).toBeVisible();

    // one clean save first: it opens the attempt and gives the page an etag to go stale
    const first = putOk(page);
    await typeCode(page, body("SEED"));
    await first;

    setDisk(body("DISK"));
    await typeCode(page, body("MINE"));

    const banner = page.getByRole("alert").filter({ hasText: "This task changed on disk." });
    await expect(banner).toBeVisible();
    await expect(banner).toContainText("Your draft and the file on disk have diverged.");

    const settled = kept === "MINE" ? putOk(page) : Promise.resolve();
    await banner.getByRole("button", { name: action }).click();
    await settled;

    await expect(banner).toBeHidden();
    await expect(editor(page)).toContainText(`"${kept}"`);
    expect(readFileSync(TASK_PY, "utf8")).toContain(`return "${kept}"`);
  });
}
