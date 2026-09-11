/** The case that failed, in the real browser: a value wraps inside its box rather than running
 *  off the right edge, its own lines are numbered so a wrapped line cannot read as two, and the
 *  pair still ends level when one side is longer than the other. */
import { expect, test } from "@playwright/test";

const SLUG = "008_slicing";
// right shape, wrong answer: a fixed list where five slices of the generated one are wanted
const WRONG = "def solve(xs: list[int]):\n    return [10, 11, 12, 13, 14, 15]";

test("a failed case wraps, numbers its lines, and keeps the pair level", async ({ page }) => {
  await page.goto(`/#/task/${SLUG}`);
  await expect(page.getByRole("button", { name: "Run" })).toBeVisible();

  // insertText, not type(): Monaco auto-indents keystrokes and would mangle the body
  await page.locator(".monaco-editor .view-lines").first().click();
  await page.keyboard.press("ControlOrMeta+a");
  await page.keyboard.insertText(WRONG);
  await page.getByRole("button", { name: "Run" }).first().click();
  await expect(page.getByText("Output · your run")).toBeVisible();

  const pair = await page.evaluate(() => {
    const boxes = [...document.querySelectorAll("[data-wrong], [data-right]")];
    return boxes.map((b) => ({
      height: Math.round(b.getBoundingClientRect().height),
      hidden: b.scrollWidth > b.clientWidth,
      numbers: [...b.querySelectorAll("span")].map((s) => s.textContent).filter((x) => /^\d+$/.test(x!)),
    }));
  });

  expect(pair.length, "your output beside what was expected").toBe(2);
  expect(pair.some((p) => p.hidden), "nothing sits off the right edge unread").toBe(false);
  // both values here are one line, and the expected one is long enough to wrap inside its box
  expect(pair.map((p) => p.numbers)).toEqual([["1"], ["1"]]);
  expect(pair[0].height, `the pair ends level: ${pair.map((p) => p.height).join(" vs ")}`)
    .toBe(pair[1].height);
});
