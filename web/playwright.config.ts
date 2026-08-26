import { defineConfig, devices } from "@playwright/test";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

export const repoRoot = resolve(import.meta.dirname, "..");

/** The content root the server under test is given: a throwaway copy of `tasks/`, never
 *  the checkout, which a run would write into. */
export const scratchRoot = join(tmpdir(), "drillion-e2e-root");

/** 8766, not the app's 8765, so a run never collides with a dev server someone left up.
 *  Override with DRILLION_PORT. */
const port = Number(process.env.DRILLION_PORT ?? 8766);

export default defineConfig({
  testDir: "e2e",
  outputDir: "test-results",
  // the captures walk one server through one session, which is not safe to run twice at once
  workers: 1,
  retries: 0,
  timeout: 60_000,
  reporter: [["list"]],
  use: {
    ...devices["Desktop Chrome"],
    baseURL: `http://127.0.0.1:${port}`,
    trace: "retain-on-failure",
    // fixed, so a screenshot changes when the UI changes and not when the runner does
    viewport: { width: 1440, height: 900 },
  },
  webServer: {
    // built here, not in a fixture: the root must exist before the server reads it, and
    // this runs once where a fixture re-runs on every restarted worker
    command: `rm -rf ${scratchRoot} web/screenshots && mkdir -p ${scratchRoot} && cp -r tasks ${scratchRoot}/ && uv run drillion`,
    cwd: repoRoot,
    url: `http://127.0.0.1:${port}/api/health`,
    env: {
      DRILLION_ROOT: scratchRoot,
      DRILLION_PORT: String(port),
      DRILLION_OPEN_BROWSER: "0",
    },
    reuseExistingServer: false, // see `scratchRoot`: reuse would mean an unknown root
    stdout: "pipe",
    timeout: 120_000, // `uv run` may still be resolving the environment
  },
});
