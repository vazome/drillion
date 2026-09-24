import { expect, test, type Locator } from "@playwright/test";

/** The two task-screen splitters. The output under the editor fits what it shows until its
 *  splitter is dragged; a drag fixes the height across reloads, and a double-click lets it fit
 *  again. */
const height = async (locator: Locator) => (await locator.boundingBox())!.height;

test("the output height follows its splitter, survives a reload, and fits again on double-click", async ({ page }) => {
  await page.goto("/#/task/012_sortkey");
  const splitter = page.getByRole("separator", { name: "Output height" });
  const output = page.getByRole("region", { name: /^(Result|Output of your run)/ });
  await expect(splitter).toBeVisible();
  const fitted = await height(output);

  const box = (await splitter.boundingBox())!;
  const x = box.x + box.width / 2;
  const y = box.y + box.height / 2;
  await page.mouse.move(x, y);
  await page.mouse.down();
  await page.mouse.move(x, y - 150, { steps: 10 });
  await page.mouse.up();
  await expect.poll(() => height(output)).toBeGreaterThan(fitted + 140);
  const dragged = await height(output);

  await page.reload();
  await expect(splitter).toBeVisible();
  await expect.poll(() => height(output)).toBeCloseTo(dragged, -1);

  // the keyboard moves it too, up for a taller output
  const before = Number(await splitter.getAttribute("aria-valuenow"));
  await splitter.focus();
  await page.keyboard.press("ArrowUp");
  await expect.poll(async () => Number(await splitter.getAttribute("aria-valuenow"))).toBeCloseTo(before + 2, 5);

  await splitter.dblclick();
  await expect.poll(() => height(output)).toBeCloseTo(fitted, -1);
});

test("the brief pane width follows its splitter", async ({ page }) => {
  await page.goto("/#/task/012_sortkey");
  const splitter = page.getByRole("separator", { name: "Brief pane width" });
  const brief = page.locator(`[id="${await splitter.getAttribute("aria-controls")}"]`);
  const before = (await brief.boundingBox())!.width;
  const box = (await splitter.boundingBox())!;
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await page.mouse.down();
  await page.mouse.move(box.x + box.width / 2 + 100, box.y + box.height / 2, { steps: 10 });
  await page.mouse.up();
  await expect.poll(async () => (await brief.boundingBox())!.width).toBeCloseTo(before + 100, -1);
  await splitter.focus();
  await page.keyboard.press("Home");
  await expect.poll(async () => (await brief.boundingBox())!.width).toBeCloseTo(340, -1);
});
