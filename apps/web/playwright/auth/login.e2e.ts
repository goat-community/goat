import { expect, test } from "@playwright/test";

import { PASSWORD, logIn, needsAuth, userOf } from "../fixtures/users";

/**
 * Signing in and out through Keycloak's login page.
 *
 * Each test starts signed out. Logging out ends only the session it was
 * started in, so it does not disturb the sessions the other specs reuse.
 */
needsAuth(test);
test.use({ storageState: { cookies: [], origins: [] } });

test("a wrong password is refused on the login page", async ({ page }) => {
  await page.goto("/home");
  await page.locator("input[name=username]").fill(userOf("editor").email);
  await page.locator("input[name=password]").fill("not-the-password");
  await page.locator("button[name=login]").click();

  await expect(page.getByRole("alert")).toContainText(/Invalid username or password/i);
  expect(new URL(page.url()).port).toBe("8080");
});

test("an anonymous visitor is sent to log in and brought back to the page they wanted", async ({ page }) => {
  await page.goto("/content");
  await expect(page.locator("input[name=username]")).toBeVisible({ timeout: 30000 });

  await page.locator("input[name=username]").fill(userOf("editor").email);
  await page.locator("input[name=password]").fill(PASSWORD);
  await page.locator("button[name=login]").click();

  // Back on the app's page the sign-in started from (Keycloak's pages are under /realms)
  await page.waitForURL((url) => url.pathname === "/content", { timeout: 30000 });
  await expect(page.getByRole("heading", { name: "Content" })).toBeVisible();
});

test("logging out ends the session", async ({ page }) => {
  await logIn(page, userOf("editor").email, PASSWORD);
  await expect(page.getByRole("heading", { level: 1 })).toContainText(userOf("editor").firstname);

  await page.getByRole("button", { name: "Account menu" }).click();
  await page.getByRole("button", { name: "Logout" }).click();

  // Signed out of the app and of Keycloak: the login page asks again.
  await expect(page.locator("input[name=username]")).toBeVisible({ timeout: 30000 });
  await page.goto("/home");
  await expect(page.locator("input[name=username]")).toBeVisible({ timeout: 30000 });
});
