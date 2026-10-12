import { defineConfig, devices } from "@playwright/test";
import dotEnv from "dotenv";
import * as os from "os";
import * as path from "path";

dotEnv.config({ path: ".env" });

const outputDir = path.join(__dirname, "test-results");
// Dev Server on local can be slow to start up and process requests. So, keep timeouts really high on local, so that tests run reliably locally
// So, if not in CI, keep the timers high, if the test is stuck somewhere and there is unnecessary wait developer can see in browser that it's stuck
const DEFAULT_NAVIGATION_TIMEOUT = process.env.CI ? 15000 : 50000;
const DEFAULT_EXPECT_TIMEOUT = process.env.CI ? 15000 : 50000;

// Test Timeout can hit due to slow expect, slow navigation.
// So, it should me much higher than sum of expect and navigation timeouts as there can be many async expects and navigations in a single test
const DEFAULT_TEST_TIMEOUT = process.env.CI ? 60000 : 120000;

const headless = !!process.env.CI || !!process.env.PLAYWRIGHT_HEADLESS || !process.env.DISPLAY;

// With auth on (E2E_AUTH, set by the CI workflow) the "setup" project logs
// each provisioned role in first, and the specs start as the owner unless a
// spec picks another role (apps/web/playwright/fixtures/users.ts).
const authOn = !!process.env.E2E_AUTH;
const ownerSession = path.join(__dirname, "apps/web/playwright/.auth/owner.json");

export default defineConfig({
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: os.cpus().length,
  timeout: DEFAULT_TEST_TIMEOUT,
  maxFailures: headless ? 10 : undefined,
  reporter: [
    [process.env.CI ? "github" : "list"],
    ...(process.env.DEPLOY_SENTINEL ? [["@deploysentinel/playwright" as const]] : []),
    ["html", { outputFolder: "./test-results/reports/playwright-html-report", open: "never" }],
    ["junit", { outputFile: "./test-results/reports/results.xml" }],
  ],
  outputDir: path.join(outputDir, "results"),
  use: {
    // E2E_BASE_URL points the suite at another stack, e.g. a worktree's (goat-stack run)
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000/",
    locale: "en-US",
    trace: "retain-on-failure",
    headless,
  },
  /* Configure projects for major browsers */
  projects: [
    {
      name: "setup",
      testDir: "./apps/web/playwright",
      testMatch: /auth\.setup\.ts/,
      use: { ...devices["Desktop Chrome"], navigationTimeout: DEFAULT_NAVIGATION_TIMEOUT },
    },
    {
      name: "@p4b/web",
      testDir: "./apps/web/playwright",
      testMatch: /.*\.e2e\.tsx?/,
      dependencies: authOn ? ["setup"] : [],
      expect: {
        timeout: DEFAULT_EXPECT_TIMEOUT,
      },
      use: {
        ...devices["Desktop Chrome"],
        /** If navigation takes more than this, then something's wrong, let's fail fast. */
        navigationTimeout: DEFAULT_NAVIGATION_TIMEOUT,
        ...(authOn ? { storageState: ownerSession } : {}),
      },
    },
  ],
});
