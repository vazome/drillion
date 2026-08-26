/** What the client looks like on this branch, as PNGs a reviewer can open.
 *
 * This is a review aid, not a visual regression test: nothing is diffed against a committed
 * baseline and nothing fails on pixel drift (issue #29). It fails when the app cannot be
 * driven at all — a catalogue that never loads, a Run that never returns a verdict — which
 * is the other half of what a screenshot is worth.
 */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { expect, test, type Page } from "@playwright/test";
import { repoRoot, scratchRoot } from "../playwright.config";

const SHOTS = join(import.meta.dirname, "..", "screenshots");
const SLUG = "001_fstrings";
/** 001's own `_reference`, written as the learner would: enough to make the grader say pass,
 *  which is the only way to photograph the pass state. If 001 ever changes shape this test
 *  fails loudly rather than quietly capturing a failure and calling it a pass. */
const SOLUTION = [
  "def solve(rows):",
  '    return "\\n".join(f"{name:<14}{value:>12,.2f}" for name, value in rows)',
].join("\n");

/** When the throwaway root was built, which is the instant before the server was started:
 *  any file newer than this was written by the run. Read off the copy rather than from a
 *  clock, because a failed test restarts its worker and a `Date.now()` in this module would
 *  then be re-read *after* the writes it is supposed to predate. */
const runStart = statSync(join(scratchRoot, "tasks")).mtimeMs;

/** fullPage everywhere: a result banner or a long spec runs past 900px, and the part that
 *  scrolled off is usually the part worth reviewing. */
const shot = (page: Page, name: string) =>
  page.screenshot({ path: join(SHOTS, `${name}.png`), fullPage: true, animations: "disabled" });

test("captures the screens a reviewer needs", async ({ page }) => {
  await page.goto("/#/");
  await expect(page.getByText("Today", { exact: true })).toBeVisible();
  await shot(page, "1-catalogue");

  await page.goto(`/#/task/${SLUG}`);
  const run = page.getByRole("button", { name: "Run tests" });
  await expect(run).toBeVisible();
  await shot(page, "2-task");

  // Grading is the product, so both verdicts get photographed. The stub raises
  // NotImplementedError, so the first run is a real failure with real pytest output.
  await run.click();
  await expect(page.getByText("Result · attempt 1")).toBeVisible();
  await page.getByText("Full output").click(); // the pytest output is the point of the shot
  await shot(page, "3-task-tests-failed");

  // insertText, not type(): CodeMirror auto-indents keystrokes and would mangle the body.
  await page.locator(".cm-content").click();
  await page.keyboard.press("ControlOrMeta+a");
  await page.keyboard.insertText(SOLUTION);
  await run.click();
  await expect(page.getByRole("button", { name: "Back to Today" })).toBeVisible();
  await shot(page, "4-task-tests-passed");

  // Last, so the ladder and the session table have something in them.
  await page.goto("/#/progress");
  await expect(page.getByText("The ladder", { exact: true })).toBeVisible();
  await shot(page, "5-progress");
});

test("the run cannot have touched the repository's own state", () => {
  // Acceptance criterion 4. The server was handed DRILLION_ROOT; this is the assertion that
  // it was actually obeyed, and it is deliberately about the checkout, not about the copy.
  const untouched = (path: string) =>
    !existsSync(path) || statSync(path).mtimeMs < runStart;

  for (const slug of readdirSync(join(repoRoot, "tasks")))
    expect(untouched(join(repoRoot, "tasks", slug, "task.py")), `${slug} was written`).toBe(true);
  for (const name of ["progress.json", "progress.json.bak"])
    expect(untouched(join(repoRoot, name)), `${name} was written`).toBe(true);

  // ...and the same writes landed in the scratch root, so the checks above are not vacuous:
  // passing a task rewrites its file twice (the learner's code, then the stub again) and
  // schedules the card.
  expect(statSync(join(scratchRoot, "tasks", SLUG, "task.py")).mtimeMs).toBeGreaterThan(runStart);
  expect(readFileSync(join(scratchRoot, "progress.json"), "utf8")).toContain(SLUG);
});
