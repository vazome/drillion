/** Every task page, in the real browser: the spec Markdown, the editor and the hint panel
 *  all mount without a console error. The one check that has to see all 171 specs. */
import { expect, test } from "@playwright/test";

test("every task in the catalogue renders", async ({ page }) => {
  test.slow(); // 171 navigations
  const problems: string[] = [];
  let at = "";
  page.on("console", (m) => m.type() === "error" && problems.push(`${at}: ${m.text()}`));
  page.on("pageerror", (e) => problems.push(`${at}: ${e.message}`));

  await page.goto("/#/");
  const slugs: string[] = await page.evaluate(async () =>
    (await (await fetch("/api/catalogue")).json()).tasks.map((t: { slug: string }) => t.slug));
  expect(slugs.length).toBeGreaterThan(100);

  for (const slug of slugs) {
    at = slug;
    await page.goto(`/#/task/${slug}`);
    // the button lives below the spec pane, so it is only there once the spec rendered
    await expect(page.getByRole("button", { name: "Run tests" })).toBeVisible();
  }
  expect(problems.join("\n")).toBe("");
});
