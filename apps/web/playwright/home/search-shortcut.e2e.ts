import { devices, expect, test } from "@playwright/test";

/**
 * Home's search shortcut: Ctrl+K on Windows and Linux, ⌘K on a Mac, and no
 * hint on a phone. The browser is told it runs on Windows by its user agent
 * and `navigator.platform`, which is all the page reads; whether Windows
 * itself hands Ctrl+K to the page needs a real Windows machine.
 */

const WINDOWS_CHROME =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36";

test.describe("on Windows", () => {
  test.use({ userAgent: WINDOWS_CHROME });

  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      Object.defineProperty(navigator, "platform", { get: () => "Win32" });
      Object.defineProperty(navigator, "userAgentData", {
        get: () => ({ platform: "Windows", mobile: false, brands: [] }),
      });
    });
  });

  test("the hint reads Ctrl+K, and Ctrl+K puts the cursor in the search", async ({ page }) => {
    await page.goto("/home");
    const search = page.getByPlaceholder("Search…", { exact: true });
    await expect(search).toBeVisible({ timeout: 30000 });
    await expect(page.locator("kbd").filter({ hasText: "Ctrl+K" })).toBeVisible();
    await expect(page.locator("kbd").filter({ hasText: "⌘" })).toHaveCount(0);

    // Focus somewhere else on the page first, as after reading it.
    await page.getByRole("heading", { level: 1 }).click();
    await expect(search).not.toBeFocused();
    await page.keyboard.press("Control+k");
    await expect(search).toBeFocused();
  });
});

test.describe("on a phone", () => {
  const { viewport, userAgent, deviceScaleFactor, isMobile, hasTouch } = devices["iPhone 13"];
  test.use({ viewport, userAgent, deviceScaleFactor, isMobile, hasTouch });

  test("no shortcut hint is shown", async ({ page }) => {
    await page.goto("/home");
    await expect(page.getByPlaceholder("Search…", { exact: true })).toBeVisible({ timeout: 30000 });
    await expect(page.locator("kbd")).toHaveCount(0);
  });
});
