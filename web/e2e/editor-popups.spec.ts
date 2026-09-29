import { expect, test } from "@playwright/test";

/** Monaco draws suggest, hover and the details panel `position: fixed`. An ancestor that still
 *  holds a transform, even an identity one left by a finished animation, becomes their
 *  containing block and moves them off the cursor by its own offset. */
test("nothing above the editor holds a transform once the page has arrived", async ({ page }) => {
  await page.goto("/#/task/010_little_sisters_vocab");
  const editor = page.locator(".monaco-editor").first();
  await expect(editor).toBeVisible();
  await page.waitForFunction(() => document.getAnimations().every((a) => a.playState !== "running"));
  const held = await editor.evaluate((el) => {
    const out: string[] = [];
    for (let e = el.parentElement; e; e = e.parentElement) {
      const s = getComputedStyle(e);
      if (s.transform !== "none" || s.filter !== "none" || s.willChange.includes("transform")) out.push(`${e.tagName}.${e.className}`);
    }
    return out;
  });
  expect(held).toEqual([]);
});
