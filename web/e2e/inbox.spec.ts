/** The catalogue's hash inbox, which only exists in a real browser: `#/?q` from the `/` key
 *  pressed on another route, and `#/?tag=` arriving while the page is already mounted. */
import { expect, test } from "@playwright/test";

const search = /^Search tasks by title/;

test("`/` from the task page lands in the catalogue's search box", async ({ page }) => {
  await page.goto("/#/task/009_fstrings");
  await expect(page.getByRole("button", { name: "Run tests" })).toBeVisible();

  await page.keyboard.press("/");
  await expect(page.getByLabel(search)).toBeFocused();
  await expect.poll(() => page.evaluate(() => location.hash)).toBe("#/");
});

test("`#/?tag=` filters a catalogue that is already on screen", async ({ page, request }) => {
  const { tags } = await (await request.get("/api/catalogue")).json();
  await page.goto("/#/");
  await expect(page.getByLabel(search)).toBeVisible();
  await expect(page.getByRole("button", { name: "Clear", exact: true })).toHaveCount(0);

  await page.evaluate((tag) => { location.hash = `#/?tag=${encodeURIComponent(tag)}`; }, tags[0]);
  await expect(page.getByRole("button", { name: "Clear", exact: true })).toBeVisible();
  await expect.poll(() => page.evaluate(() => location.hash)).toBe("#/");
});
