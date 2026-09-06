/** Every task page, in the real browser: the spec Markdown, the editor and the hint panel
 *  all mount without a console error. The one check that has to see all 182 specs. */
import { expect, test } from "@playwright/test";

test("every task in the catalogue renders", async ({ page }) => {
  test.slow(); // 182 navigations
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
    await expect(page.getByRole("button", { name: "Run" })).toBeVisible();
    // ...and that the spec rendered as Markdown: every README is contract-tested to carry
    // `## ` headings, and a callout must never reach the page as its literal marker
    const html = await page.locator("main").innerHTML();
    if (!html.includes("<h2") || /\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]/.test(html))
      problems.push(`${slug}: spec did not render as Markdown`);
  }
  expect(problems.join("\n")).toBe("");
});
