/** What the client looks like on this branch, as PNGs a reviewer can open. A review aid,
 *  not a visual regression test: nothing is diffed, and it fails only when the app cannot
 *  be driven at all. */
import { join } from "node:path";
import { expect, test, type Page } from "@playwright/test";
import { scratchRoot } from "../playwright.config";

const SHOTS = join(import.meta.dirname, "..", "screenshots");
const SLUG = "009_fstrings";
const GATED = "049_counter";   // has both a prereq and something waiting on it
/** 001's own `_reference`: the only way to photograph the pass state. */
const SOLUTION = [
  "def solve(rows):",
  '    return "\\n".join(f"{name:<14}{value:>12,.2f}" for name, value in rows)',
].join("\n");

/** fullPage everywhere: the part that scrolled off is usually the part worth reviewing. */
const shot = (page: Page, name: string) =>
  page.screenshot({ path: join(SHOTS, `${name}.png`), fullPage: true, animations: "disabled" });

test("captures the screens a reviewer needs", { tag: "@capture" }, async ({ page, request }) => {
  await page.goto("/#/");
  await expect(page.getByRole("heading", { name: /^Up next/ })).toBeVisible();
  await shot(page, "1-catalogue");

  await page.goto(`/#/task/${SLUG}`);
  const submit = page.getByRole("button", { name: /^Submit/ });
  await expect(page.getByRole("button", { name: "Run" })).toBeVisible();
  // an earlier spec in this run may have opened this task and spent its reading minute, so
  // the attempt is dropped and reopened: these shots are of a task being met for the first
  // time, and that has to be true however long the run took to get here. Through the API
  // rather than the button, which asks a native confirm() first.
  const meta = async () => (await request.get(`/api/task/${SLUG}`)).json();
  // the attempt opens on a timer rather than on mount, the same wait races.spec.ts makes
  await expect.poll(async () => !!(await meta()).attempt, { timeout: 15_000 }).toBe(true);
  const dropped = await request.post(`/api/task/${SLUG}/abandon`, { data: { etag: (await meta()).etag } });
  expect(dropped.status()).toBe(200);
  await page.reload();
  await expect(page.getByRole("button", { name: "Run" })).toBeVisible();
  await shot(page, "2-task");

  // The reading grace. Dismissed straight after, or it sits in the corner of the next two shots.
  const grace = page.getByText(/The clock starts in \d+ seconds/);
  // the reopened attempt starts on the same timer the poll above waits for, and the notice
  // cannot be on screen before the server says the reading minute is running
  await expect.poll(async () => (await meta()).attempt?.grace ?? 0, { timeout: 15_000 }).toBeGreaterThan(0);
  await expect(grace).toBeVisible();
  await shot(page, "2b-task-reading-time");
  await page.getByRole("button", { name: "Dismiss" }).click();
  await expect(grace).toBeHidden();

  // both verdicts get photographed; the stub raises NotImplementedError, so attempt 1 really fails
  await submit.click();
  await expect(page.getByRole("region", { name: "Result of submit 1" }).getByText("Not yet", { exact: true })).toBeVisible();
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

  // A git task: the terminal takes the editor's place, Reset repository in its head.
  await page.goto("/#/task/339_git_first_commit");
  await expect(page.getByRole("region", { name: "Terminal, in the task's repository" })).toBeVisible();
  await shot(page, "task-git");

  // Last, so the strength counts and the session table have something in them.
  await page.goto("/#/progress");
  await expect(page.getByText("How well you know them", { exact: true })).toBeVisible();
  await shot(page, "5-progress");

  // Settings: a dialog over whatever is on screen, reached here by the link that still
  // deep-links to it. The data locations and both halves of the backup workflow.
  await page.goto("/#/settings");
  await expect(page.getByRole("heading", { name: "Editor", exact: true })).toBeVisible();
  await shot(page, "5b-settings-editor");
  await page.getByRole("heading", { name: "Your data", exact: true }).scrollIntoViewIfNeeded();
  await expect(page.getByText("Download a backup", { exact: true })).toBeVisible();
  await expect(page.getByText(scratchRoot, { exact: true })).toBeVisible();
  await shot(page, "5c-settings-data");

  // Arm the confirmation and disarm it again without erasing the session being photographed.
  const erase = page.getByRole("button", { name: "Erase all progress" });
  const phrase = page.getByRole("textbox", { name: "Type erase progress to confirm" });
  await expect(erase).toBeDisabled();
  await phrase.fill("erase progress");
  await expect(erase).toBeEnabled();
  await shot(page, "5d-danger-zone");
  await phrase.fill("");
  await expect(erase).toBeDisabled();

  // The panes stack below 1100px. After the others, so each of those keeps the fixed viewport.
  // The task passed above, so it opens on Review, which goes inline at this width.
  await page.setViewportSize({ width: 900, height: 1200 });
  await page.goto(`/#/task/${SLUG}`);
  await expect(page.getByRole("region", { name: "Review" })).toBeVisible();
  await shot(page, "6-task-tablet");

  // the lineage as its own screen, the way a catalogue row's `needs` flag reaches it
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(`/#/task/${GATED}/deps`);
  await expect(page.getByText(/^Needs · \d+$/)).toBeVisible();
  await shot(page, "7-lineage");

  // Vim mode last: it is a browser preference, so switching it on would follow the page
  // into every shot above. Turned back off before the run ends.
  await page.goto("/#/settings");
  await page.getByRole("button", { name: "Vim", exact: true }).click();
  await page.keyboard.press("Escape");
  await page.goto(`/#/task/${GATED}`);
  const modeLine = page.locator(".monaco-editor").locator("..").locator("..").getByText("--", { exact: false });
  await expect(page.getByText("NORMAL", { exact: false }).first()).toBeVisible();
  await shot(page, "9-task-vim");

  // The page's own chords must survive the binding: Vim swallowing Run would be the bug.
  await page.locator(".monaco-editor .view-lines").first().click();
  await page.keyboard.press("ControlOrMeta+Enter");
  await expect(page.getByRole("status").filter({ hasText: /not met|not passing/i }).first()).toBeVisible();
  await expect(modeLine.first()).toBeVisible();

  // Emacs is the third binding, and the same two rules: the page's chords survive it, and
  // C-g gets you out of a half-typed one.
  await page.goto("/#/settings");
  await page.getByRole("button", { name: "Emacs", exact: true }).click();
  await page.keyboard.press("Escape");
  await page.goto(`/#/task/${GATED}`);
  await page.locator(".monaco-editor .view-lines").first().click();
  await page.keyboard.press("Control+x");
  const pending = page.getByText("C-x", { exact: true });
  await expect(pending).toBeVisible();
  await page.keyboard.press("Control+g");
  await expect(pending).toHaveCount(0);
  await page.keyboard.press("ControlOrMeta+Enter");
  await expect(page.getByRole("status").filter({ hasText: /not met|not passing/i }).first()).toBeVisible();

  await page.goto("/#/settings");
  await page.getByRole("button", { name: "Standard", exact: true }).click();
  await page.keyboard.press("Escape");
});
