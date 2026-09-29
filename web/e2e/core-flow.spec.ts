import { expect, test } from "@playwright/test";

test("a passing submission reaches Review", async ({ page }) => {
  await page.goto("/#/task/009_fstrings");
  await expect(page.getByRole("button", { name: "Run" })).toBeVisible();
  const solution = [
    "def solve(rows):",
    '    return "\\n".join(f"{name:<14}{value:>12,.2f}" for name, value in rows)',
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
