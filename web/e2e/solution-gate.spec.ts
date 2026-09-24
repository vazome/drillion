import { expect, test } from "@playwright/test";

/** A locked Solution says what it still needs only when pressed, and the notice clears itself. */
test("a locked solution explains itself when pressed, then gets out of the way", async ({ page }) => {
  await page.goto("/#/task/013_card_games");
  const button = page.getByRole("button", { name: "Solution" });
  await expect(button).toHaveText("Solution");
  await button.click();
  const notice = page.getByRole("status").filter({ hasText: "Not yet: the solution opens after" });
  await expect(notice).toContainText(/more submits? and .+ more work\./);
  await expect(notice).toBeHidden({ timeout: 8_000 });
});
