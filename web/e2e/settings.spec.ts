import { expect, test } from "@playwright/test";

test("Settings preferences persist, reset, and stay reachable on a narrow screen", async ({ page }) => {
  await page.goto("/#/settings");
  const dialog = page.getByRole("dialog", { name: "Settings" });
  const font = dialog.getByRole("combobox", { name: "Editor font", exact: true });
  await font.selectOption("fira");
  await dialog.getByRole("combobox", { name: "Editor font size" }).selectOption("18");
  await dialog.getByRole("combobox", { name: "Key binding" }).selectOption("emacs");
  await dialog.getByRole("combobox", { name: "Tab size" }).selectOption("8");
  for (const label of ["Font ligatures", "Word wrap", "Relative line numbers", "Practice timer"]) {
    await dialog.getByRole("group", { name: label, exact: true }).getByRole("switch").click();
  }
  await page.reload();
  await expect(font).toHaveValue("fira");
  const prefs = await page.evaluate(() => JSON.parse(localStorage.getItem("drillion-prefs")!));
  expect(prefs).toMatchObject({ font: "fira", fontSize: 18, keys: "emacs", tabSize: 8,
    ligatures: true, wordWrap: false, relativeLines: true, showTimer: false });
  await dialog.getByRole("button", { name: "Put these back to their defaults" }).click();
  await expect(font).toHaveValue("shipped");
  await expect(dialog.getByRole("combobox", { name: "Key binding" })).toHaveValue("regular");
  await expect(dialog.getByRole("group", { name: "Practice timer" }).getByRole("switch")).toBeChecked();

  await dialog.getByRole("button", { name: "Close", exact: true }).click();
  await expect(dialog).toBeHidden();
  await page.getByRole("button", { name: "Settings", exact: true }).click();
  await expect(dialog).toBeVisible();
  await page.setViewportSize({ width: 360, height: 640 });
  await dialog.getByRole("button", { name: "Erase all progress", exact: true }).click();
  await dialog.getByRole("textbox", { name: "Type erase progress to confirm" }).fill("erase progress");
  await expect(dialog.getByRole("button", { name: "I understand, erase everything" })).toBeEnabled();
  const spill = await dialog.evaluate((el) => el.scrollWidth - el.clientWidth);
  expect(spill).toBeLessThanOrEqual(1);
  await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
});

test("Settings downloads, previews, cancels and restores a real backup", async ({ page }) => {
  await page.goto("/#/settings");
  const download = page.waitForEvent("download");
  await page.getByRole("link", { name: "Download a backup" }).click();
  const backup = await download;
  expect(backup.suggestedFilename()).toMatch(/\.zip$/);
  const path = await backup.path();
  expect(path).not.toBeNull();
  const picker = page.getByLabel("Choose a backup file to restore");
  await picker.setInputFiles(path!);
  const replace = page.getByRole("button", { name: "Replace my data" });
  await expect(replace).toBeEnabled();
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(replace).toHaveCount(0);
  await expect(picker).toHaveValue("");
  await picker.setInputFiles(path!);
  await expect(replace).toBeEnabled();
  await replace.click();
  await expect(page.getByText(/^Restored \d+ cards/)).toBeVisible();
  await expect(page.getByText(/What you had before is at/)).toBeVisible();
  await expect(picker).toHaveValue("");
});
