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

/** The strip is one tab stop, says "read-only" on each locked tab rather than in a label of
 *  its own, and holds its height: nothing it does may move the editor under the cursor. */
test("the chart strip never moves the editor and is one tab stop", async ({ page }) => {
  await page.goto("/#/task/284_helm_template_deployment");
  const tabs = page.getByRole("tablist", { name: "Chart files" });
  const panel = page.getByRole("tabpanel");
  await expect(tabs.getByRole("tab").first()).toBeVisible();
  // against the document, not the viewport: a run may scroll the page, which moves nothing
  const top = () => panel.evaluate((el) => el.getBoundingClientRect().top + window.scrollY);
  const before = await top();

  await expect(tabs.locator('[tabindex="0"]')).toHaveCount(1);
  await expect(tabs.getByText("read-only", { exact: true }).first()).toBeVisible();
  await expect(page.getByText("READ-ONLY", { exact: true })).toHaveCount(0);

  await tabs.getByRole("tab").first().focus();
  for (const key of ["ArrowRight", "End", "ArrowLeft", "Home"]) {
    await page.keyboard.press(key);
    await expect(tabs.locator('[tabindex="0"]')).toHaveCount(1);
    await expect(tabs.locator('[tabindex="0"]')).toBeFocused();
    expect(await top(), `after ${key}`).toBe(before);
  }
  await page.keyboard.press("End");
  await expect(tabs.getByRole("tab").last()).toHaveAttribute("aria-selected", "true");
  await page.keyboard.press("Home");

  // a run that fails in the learner's file marks its tab, and the strip keeps its height.
  // Measured from the strip's own top: the first run starts an attempt, and the action row
  // above can wrap when its seed and Abandon arrive. Needs Helm, which CI does not install.
  const strip = async () => (await top()) - (await tabs.evaluate((el) => el.getBoundingClientRect().top + window.scrollY));
  const height = await strip();
  await page.locator(".monaco-editor[data-uri] .view-lines").first().click();
  await page.keyboard.insertText("{{ .Values.nope.nope }}\n");
  await page.getByRole("button", { name: "Run" }).click();
  await expect(page.getByRole("status").filter({ hasText: /failed|passed|not installed/i }).first()).toBeVisible({ timeout: 30_000 });
  if (await page.getByText(/helm is not installed/).count()) return;
  await expect(tabs.getByRole("tab", { name: /the last run reported a problem here/ })).toHaveCount(1);
  expect(await strip(), "after a run marked a tab").toBe(height);
});
