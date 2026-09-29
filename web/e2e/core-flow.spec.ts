import { expect, test } from "@playwright/test";

test("a passing submission reaches Review", async ({ page }) => {
  // Other required specs open 009_fstrings as an unpassed task. Keep this pass separate.
  await page.goto("/#/task/001_guidos_gorgeous_lasagna");
  await expect(page.getByRole("button", { name: "Run" })).toBeVisible();
  const solution = [
    "def solve():",
    "    def bake_time_remaining(elapsed): return 40 - elapsed",
    "    def preparation_time_in_minutes(layers): return layers * 2",
    "    def elapsed_time_in_minutes(layers, elapsed): return preparation_time_in_minutes(layers) + elapsed",
    "    return {",
    '        "EXPECTED_BAKE_TIME": 40,',
    '        "bake_time_remaining": bake_time_remaining,',
    '        "preparation_time_in_minutes": preparation_time_in_minutes,',
    '        "elapsed_time_in_minutes": elapsed_time_in_minutes,',
    "    }",
  ].join("\n");
  await page.locator(".monaco-editor .view-lines").first().click();
  await page.keyboard.press("ControlOrMeta+a");
  await page.keyboard.insertText(solution);
  await page.getByRole("button", { name: /^Submit/ }).click();
  await expect(page.getByRole("button", { name: "Back to Today" })).toBeVisible();
  await expect(page.getByRole("region", { name: "Review" })).toBeVisible();
});

test("git tasks offer a terminal", async ({ page }) => {
  await page.goto("/#/task/339_git_first_commit");
  await expect(page.getByRole("region", { name: "Terminal, in the task's repository" })).toBeVisible();
});

test("the Run shortcut survives Vim and Emacs", async ({ page }) => {
  const task = "/#/task/049_counter";
  for (const mode of ["Vim", "Emacs"] as const) {
    await page.goto("/#/settings");
    await page.getByRole("button", { name: mode, exact: true }).click();
    await page.keyboard.press("Escape");
    await page.goto(task);
    await expect(page.getByRole("button", { name: "Run" })).toBeVisible();
    await page.locator(".monaco-editor .view-lines").first().click();
    if (mode === "Emacs") {
      await page.keyboard.press("Control+x");
      const pending = page.getByText("C-x", { exact: true });
      await expect(pending).toBeVisible();
      await page.keyboard.press("Control+g");
      await expect(pending).toHaveCount(0);
    }
    await page.keyboard.press("ControlOrMeta+Enter");
    await expect(page.getByRole("status").filter({ hasText: /not met|not passing/i }).first()).toBeVisible();
  }
  await page.goto("/#/settings");
  await page.getByRole("button", { name: "Standard", exact: true }).click();
});
