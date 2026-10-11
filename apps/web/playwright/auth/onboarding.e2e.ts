import { expect, test } from "@playwright/test";

import { API_URL, PASSWORD, apiAs, logIn, needsAuth, userOf } from "../fixtures/users";

/**
 * A new user's first login: with no organization they are sent to create
 * one, and they land on Home as its owner.
 *
 * The newcomer is provisioned in Keycloak only. Creating the organization is
 * one-way, so a retry would find them already onboarded: retries are off.
 */
needsAuth(test);
test.use({ storageState: { cookies: [], origins: [] } });
test.describe.configure({ retries: 0 });

/** Opens a dropdown by its label and picks an option, until the field shows
 * it: MUI drops a click that lands while its menu is still opening, and the
 * menu then stays open over the rest of the form. */
const choose = async (page: import("@playwright/test").Page, label: RegExp, option: string) => {
  const field = page.getByRole("combobox", { name: label });
  await expect(async () => {
    await page.keyboard.press("Escape"); // a menu a dropped click left open
    await field.click();
    await page.getByRole("option", { name: option, exact: true }).click({ timeout: 5000 });
    await expect(field).toHaveText(option, { timeout: 2000 });
  }).toPass({ timeout: 30000 });
};

test("a user without an organization creates one on first login", async ({ page }) => {
  await logIn(page, userOf("newcomer").email, PASSWORD);
  await page.waitForURL(/\/onboarding\/organization\/create/, { timeout: 30000 });

  await page.getByLabel("Your organization's name").fill("Newcomer Planning");
  await page.getByRole("button", { name: "Next" }).click();

  await choose(page, /Organization type/, "Public sector");
  await choose(page, /Organization size/, "5-25");
  await choose(page, /Industry/, "Architecture");
  await page.getByLabel(/Organization department/).fill("Mobility");
  await choose(page, /What are your main use cases\?/, "Geospatial data management and analysis");
  await page.getByRole("button", { name: "Next" }).click();
  // Every profile field is required: the step does not let anyone on without them.

  await page.getByLabel(/Phone number/).fill("+49 89 1234567");
  await page.getByRole("combobox", { name: /Country/ }).fill("Germany");
  // The option leads with the country's flag.
  await page.getByRole("option", { name: /Germany/ }).click();
  await page.getByRole("button", { name: "Let's get started" }).click();

  await page.waitForURL(/\/home/, { timeout: 30000 });
  await expect(page.getByRole("heading", { level: 1 })).toContainText(userOf("newcomer").firstname);

  // They own the new organization: it shows up as theirs.
  const newcomer = await apiAs("newcomer");
  try {
    const organization = await newcomer.get(`${API_URL}/api/v2/users/organization`);
    expect(organization.status()).toBe(200);
    expect((await organization.json()).name).toBe("Newcomer Planning");
  } finally {
    await newcomer.dispose();
  }
});
