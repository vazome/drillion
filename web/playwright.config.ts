import { defineConfig, devices } from "@playwright/test";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

export const repoRoot = resolve(import.meta.dirname, "..");

/** The content root the server under test is given: a throwaway copy of `tasks/`, never the
 *  checkout. A run writes a learner's code into `tasks/<slug>/task.py` and a schedule into
 *  `progress.json`, and neither of those belongs to whoever happens to be reviewing the
 *  branch. `e2e/screens.spec.ts` asserts the separation rather than trusting it. */
export const scratchRoot = join(tmpdir(), "drillion-e2e-root");

/** 8766, not the app's 8765, so a run never collides with a dev server someone left up — and
 *  never quietly reuses one, which would screenshot whatever root *that* was pointed at.
 *  Override with DRILLION_PORT. */
const port = Number(process.env.DRILLION_PORT ?? 8766);

export default defineConfig({
  testDir: "e2e",
  outputDir: "test-results",
  // The captures walk one server through one session: fail a task, pass it, then look at
  // Progress. None of that is safe to run twice at once, so: one worker, no retries.
  workers: 1,
  retries: 0,
  timeout: 60_000,
  reporter: [["list"]],
  use: {
    ...devices["Desktop Chrome"],
    baseURL: `http://127.0.0.1:${port}`,
    // A CI-only failure has to be debuggable without reproducing it locally: the trace
    // carries the DOM, the console, the network and a screenshot of every step, and the
    // workflow uploads it. Kept only when something actually went wrong.
    trace: "retain-on-failure",
    // Fixed, so a screenshot changes when the UI changes and not when the runner does.
    viewport: { width: 1440, height: 900 },
  },
  webServer: {
    // The scratch root is built here rather than in a fixture because it has to exist
    // before the server reads it, and this is the one command guaranteed to run first.
    // `web/screenshots` is cleared here too, for the same reason: this runs once, where a
    // fixture would run again every time a failed test restarts its worker.
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
