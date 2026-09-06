/** What the client looks like on this branch, as PNGs a reviewer can open. A review aid,
 *  not a visual regression test: nothing is diffed, and it fails only when the app cannot
 *  be driven at all. */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { expect, test, type Page } from "@playwright/test";
import { repoRoot, scratchRoot } from "../playwright.config";

const SHOTS = join(import.meta.dirname, "..", "screenshots");
const SLUG = "009_fstrings";
const GATED = "049_counter";   // has both a prereq and something waiting on it
/** 001's own `_reference`: the only way to photograph the pass state. */
const SOLUTION = [
  "def solve(rows):",
  '    return "\\n".join(f"{name:<14}{value:>12,.2f}" for name, value in rows)',
].join("\n");

/** When the throwaway root was built: anything newer was written by this run. Read off the
 *  copy, not a clock — a restarted worker would re-read a `Date.now()` too late. */
const runStart = statSync(join(scratchRoot, "tasks")).mtimeMs;

/** fullPage everywhere: the part that scrolled off is usually the part worth reviewing. */
const shot = (page: Page, name: string) =>
  page.screenshot({ path: join(SHOTS, `${name}.png`), fullPage: true, animations: "disabled" });

test("captures the screens a reviewer needs", async ({ page }) => {
  await page.goto("/#/");
  await expect(page.getByText("Today", { exact: true })).toBeVisible();
  await shot(page, "1-catalogue");

  await page.goto(`/#/task/${SLUG}`);
  const submit = page.getByRole("button", { name: "Submit" });
  await expect(page.getByRole("button", { name: "Run" })).toBeVisible();
  await shot(page, "2-task");

  // both verdicts get photographed; the stub raises NotImplementedError, so attempt 1 really fails
  await submit.click();
  await expect(page.getByText("Result · attempt 1")).toBeVisible();
  await page.getByText("Full output").click(); // the pytest output is the point of the shot
  await shot(page, "3-task-tests-failed");

  // insertText, not type(): Monaco auto-indents keystrokes and would mangle the body.
  await page.locator(".monaco-editor .view-lines").first().click();
  await page.keyboard.press("ControlOrMeta+a");
  await page.keyboard.insertText(SOLUTION);
  await submit.click();
  await expect(page.getByRole("button", { name: "Back to Today" })).toBeVisible();
  // the spec pane scrolls on its own, and the diff against the reference is the point of the shot
  await page.locator(".monaco-diff-editor").scrollIntoViewIfNeeded();
  await shot(page, "4-task-tests-passed");

  // Last, so the ladder and the session table have something in them.
  await page.goto("/#/progress");
  await expect(page.getByText("The ladder", { exact: true })).toBeVisible();
  await shot(page, "5-progress");

  // The panes stack below 1000px. After the others, so each of those keeps the fixed viewport.
  await page.setViewportSize({ width: 900, height: 1200 });
  await page.goto(`/#/task/${SLUG}`);
  await expect(page.getByRole("button", { name: "Run" })).toBeVisible();
  await shot(page, "6-task-tablet");

  // the lineage as its own screen, the way a catalogue row's `needs` flag reaches it
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(`/#/task/${GATED}/deps`);
  await expect(page.getByText("what gates this task")).toBeVisible();
  await shot(page, "7-lineage");

  // ...and the header chips plus the panel over the task, which is the other way in
  await page.goto(`/#/task/${GATED}`);
  await page.getByRole("button", { name: "unlocks" }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await shot(page, "8-task-lineage-panel");
});

test("the run cannot have touched the repository's own state", () => {
  // the server was handed DRILLION_ROOT; this asserts the checkout itself was left alone
  const untouched = (path: string) =>
    !existsSync(path) || statSync(path).mtimeMs < runStart;

  for (const slug of readdirSync(join(repoRoot, "tasks")))
    expect(untouched(join(repoRoot, "tasks", slug, "task.py")), `${slug} was written`).toBe(true);
  for (const name of ["progress.json", "progress.json.bak"])
    expect(untouched(join(repoRoot, name)), `${name} was written`).toBe(true);

  // ...and the same writes landed in the scratch root, so the checks above are not vacuous
  expect(statSync(join(scratchRoot, "tasks", SLUG, "task.py")).mtimeMs).toBeGreaterThan(runStart);
  expect(readFileSync(join(scratchRoot, "progress.json"), "utf8")).toContain(SLUG);
});
