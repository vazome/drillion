/** The checks a screenshot cannot make: that the loop can be walked without a pointer, that
 *  what changes on screen is announced, that nothing here breaks WCAG A or AA, and that the
 *  page still reflows when it is half as wide. Runs on all three engines. */
import AxeBuilder from "@axe-core/playwright";
import { expect, type Page, test } from "@playwright/test";

const SLUG = "009_fstrings";
const SCREENS = ["/#/", `/#/task/${SLUG}`, "/#/progress"];

/** The screen is up and has its data: an audit of a half-rendered page proves nothing. */
async function settled(page: Page, route: string) {
  const there = route.includes("/task/")
    ? page.getByRole("button", { name: "Run" })
    : page.getByText(route === "/#/" ? "Today" : "How well you know them", { exact: true }).first();
  await expect(there).toBeVisible();
}

/** WCAG A and AA, everything but the editor: Monaco is vendored, its shortcomings are not
 *  drillion's to accept on a learner's behalf, and excluding it keeps the gate honest about
 *  the part we write. */
const audit = (page: Page) =>
  new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
    .exclude(".monaco-editor")
    .analyze();

const listed = (violations: { id: string; nodes: { html: string }[] }[]) =>
  violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.html.slice(0, 90)).join(" / ")}`).join("\n");

/** The focused element's own text, which is how these specs name what they landed on. */
const focused = (page: Page) =>
  page.evaluate(() => (document.activeElement as HTMLElement | null)?.innerText?.trim() ?? "");

/** Tab forward until the focus lands on something the page names this way — its own text,
 *  or the task its href opens. Anything a pointer can do has to be reachable like this. */
async function tabTo(page: Page, want: string, max = 60) {
  for (let i = 0; i < max; i++) {
    await page.keyboard.press("Tab");
    const at = await page.evaluate(() => {
      const el = document.activeElement as HTMLElement | null;
      return `${el?.getAttribute("href") ?? ""}\n${el?.innerText?.trim() ?? ""}`;
    });
    const [href, text] = at.split("\n");
    if (href === want || text === want || text.split(" ")[0] === want) return;
  }
  throw new Error(`${max} tabs and never reached "${want}"`);
}

test("every screen passes an axe audit", async ({ page }) => {
  // Both themes: the palettes are separate sets of values, so passing in one proves nothing
  // about the other. The theme is read out of storage when the app boots, so it is set there
  // and the page reloaded; the class assertion keeps the dark pass from going quietly vacuous.
  for (const scheme of ["light", "dark"] as const) {
    await page.goto(SCREENS[0]);
    await page.evaluate((s) => localStorage.setItem("drillion-theme", s), scheme);
    await page.reload();
    await expect(page.locator("html")).toHaveClass(scheme === "dark" ? /dark/ : /^(?!.*dark).*$/);
    for (const route of SCREENS) {
      await page.goto(route);
      await settled(page, route);
      expect(listed((await audit(page)).violations), `${route} (${scheme})`).toBe("");
    }
  }
});

test("Settings opens from the keyboard, keeps focus, and Escape gives it back", async ({ page }) => {
  await page.goto("/#/");
  await expect(page.getByText("Today", { exact: true })).toBeVisible();
  await tabTo(page, "Settings");
  await page.keyboard.press("Enter");

  const dialog = page.getByRole("dialog", { name: "Settings" });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole("tablist")).toHaveCount(0);
  await expect(dialog.getByRole("heading", { name: "Editor", exact: true })).toBeVisible();
  await expect(dialog.getByRole("heading", { name: "Your data", exact: true })).toBeVisible();
  await expect(dialog.getByText("Data folder")).toBeVisible();   // its paths have arrived
  expect(listed((await audit(page)).violations), "settings").toBe("");
  // the modal owns the focus: tabbing cycles inside it and never reaches the screen behind
  for (let i = 0; i < 25; i++) {
    await page.keyboard.press("Tab");
    const behind = await page.evaluate(() => {
      const el = document.activeElement;
      return !!(el && (el.closest("header") || el.closest("main")));
    });
    expect(behind, `tab ${i + 1} landed on the page behind the dialog`).toBe(false);
  }

  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
  // and the way back is the way in: focus lands on the control that opened it
  expect(await focused(page)).toBe("Settings");
});

test("a task can be opened, run and read without a pointer", async ({ page }) => {
  await page.goto("/#/");
  await expect(page.getByText("Today", { exact: true })).toBeVisible();

  // `/` is the app's own shortcut into the search box
  await page.keyboard.press("/");
  await page.keyboard.type("fstrings");
  await tabTo(page, `#/task/${SLUG}`);
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(new RegExp(`#/task/${SLUG}`));

  // Run sits above the editor in the tab order, so this never has to escape Monaco
  await tabTo(page, "Run");
  await page.keyboard.press("Enter");
  // the verdict arrives inside a live region, or a screen reader is never told the run ended
  const said = page.getByRole("status").filter({ hasText: /✗|✓|passed|failed/i });
  await expect(said.first()).toBeVisible({ timeout: 30_000 });
});

test("the page reflows at 200% zoom", async ({ page }) => {
  // 200% of the 1440x900 the rest of the suite uses: the same page in half the CSS pixels
  await page.setViewportSize({ width: 720, height: 450 });
  for (const route of [...SCREENS, "/#/settings"]) {
    await page.goto(route);
    if (route.endsWith("/settings")) {
      await expect(page.getByRole("dialog", { name: "Settings" })).toBeVisible();
      const spill = await page.getByRole("dialog", { name: "Settings" }).evaluate((el) => el.scrollWidth - el.clientWidth);
      expect(spill, "Settings scrolls sideways at 200%").toBeLessThanOrEqual(1);
    } else {
      await settled(page, route);
    }
    const spill = await page.evaluate(() =>
      document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(spill, `${route} scrolls sideways at 200%`).toBeLessThanOrEqual(1);
  }
});
