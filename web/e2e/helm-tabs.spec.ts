import { expect, test } from "@playwright/test";

/** A Helm task shows its chart around the editor: the learner's one file first, the rest
 *  read-only. Opening a chart file lays it over the editor, and coming back finds the
 *  learner's text where it was. */
test("a Helm task's chart files open read-only and the learner's file comes back", async ({ page }) => {
  await page.goto("/#/task/284_helm_template_deployment");
  const tabs = page.getByRole("tablist", { name: "Chart files" });
  const mine = tabs.getByRole("tab", { name: /^templates\/deployment\.yaml, yours/ });
  await expect(mine).toHaveAttribute("aria-selected", "true");

  const editor = page.locator(".monaco-editor[data-uri]").first();
  // insertText, not type(): Monaco treats keystrokes as editing commands
  await editor.locator(".view-lines").click();
  await page.keyboard.insertText("apiVersion: apps/v1");

  await tabs.getByRole("tab", { name: /^values\.yaml, part of the chart, read-only/ }).click();
  const file = page.getByRole("tabpanel").locator("pre");
  await expect(file).toContainText("replicaCount: 1");
  // the note under the strip says it in words, not only with the lock
  await expect(page.getByText("values.yaml · part of the chart, read-only", { exact: false }).filter({ visible: true })).toHaveCount(1);

  // arrows move and open in one step, and wrap
  await page.keyboard.press("ArrowLeft");
  await expect(tabs.getByRole("tab", { name: /^Chart\.yaml/ })).toHaveAttribute("aria-selected", "true");
  await expect(file).toContainText("apiVersion: v2");
  await page.keyboard.press("Home");
  await expect(mine).toHaveAttribute("aria-selected", "true");
  await expect(page.getByRole("tabpanel").locator("pre")).toHaveCount(0);
  await expect(editor.locator(".view-lines")).toContainText("apiVersion: apps/v1");
});
