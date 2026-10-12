import type { APIRequestContext } from "@playwright/test";
import { expect, test } from "@playwright/test";

import { API_URL, apiAs } from "../fixtures/users";

// The fixtures below talk to core directly (as the owner, `apiAs`) rather
// than through the UI, since a project's own layers/canvas play no part in
// what these tests check.

const INITIAL_VIEW_STATE = {
  latitude: 48.1502132,
  longitude: 11.5696284,
  zoom: 12,
  min_zoom: 0,
  max_zoom: 20,
  bearing: 0,
  pitch: 0,
};

test.describe("Home", () => {
  // Unique per run and per worker (fullyParallel spreads this file's tests
  // over several workers, each running beforeAll, and two workers can load
  // the module in the same millisecond), and embedded in the project's own
  // name, so the search test's query cannot also match some other spec's
  // leftover "E2E …" project (several already exist by that looser name).
  const searchTerm = `e2ehome${Date.now()}p${process.pid}`;
  const projectName = `${searchTerm} project`;

  let apiContext: APIRequestContext;
  let projectId: string;

  test.beforeAll(async () => {
    apiContext = await apiAs("owner");

    // The create endpoint 400s on a bare folder-less body (folder_id ends
    // up required at the model layer despite being optional in the schema),
    // so the personal space's own root folder has to be resolved first —
    // it is the one folder in the list this caller owns named "home"
    // (a shared team's root folder also comes back named "home", but with
    // `is_owned: false`).
    const foldersResponse = await apiContext.get(`${API_URL}/api/v2/folder`);
    expect(foldersResponse.ok()).toBeTruthy();
    const folders: { id: string; name: string; is_owned: boolean }[] = await foldersResponse.json();
    const homeFolder = folders.find((folder) => folder.name === "home" && folder.is_owned);
    expect(homeFolder, "no owned personal 'home' folder found").toBeTruthy();

    const createResponse = await apiContext.post(`${API_URL}/api/v2/project`, {
      data: {
        folder_id: homeFolder?.id,
        name: projectName,
        initial_view_state: INITIAL_VIEW_STATE,
      },
    });
    expect(createResponse.ok()).toBeTruthy();
    const created: { id: string } = await createResponse.json();
    projectId = created.id;
  });

  test.afterAll(async () => {
    // Unpin before the soft delete, so a re-run against the same account
    // never finds this project's id still pinned once the project itself
    // is gone.
    if (projectId) await apiContext.delete(`${API_URL}/api/v2/favorite/project/${projectId}`);
    // Soft delete — the project lands in the personal space's trash, same
    // as every project the UI-driven specs clean up; nothing purges it, but
    // it is out of every feed that matters.
    if (projectId) await apiContext.delete(`${API_URL}/api/v2/project/${projectId}`);
    await apiContext.dispose();
  });

  test("greeting shows the default user's first name", async ({ page }) => {
    await page.goto("/home");
    await expect(page.getByRole("heading", { level: 1 })).toContainText("GOAT");
  });

  test("what's new and the status strip do not render while their feed env vars are unset", async ({
    page,
  }) => {
    await page.goto("/home");
    await expect(page.getByRole("heading", { name: "What's New" })).toHaveCount(0);
    // The status strip has no heading of its own — its dismiss button's
    // label is the most specific thing on the page that only it renders.
    await expect(page.getByLabel("Hide until the next update")).toHaveCount(0);
  });

  test("search finds the project created via the API", async ({ page }) => {
    await page.goto("/home");

    const searchInput = page.getByPlaceholder("Search…", { exact: true });
    await searchInput.click();
    await searchInput.fill(searchTerm);

    await expect(page.getByText("Projects", { exact: true })).toBeVisible();
    await expect(page.getByRole("option", { name: new RegExp(projectName) })).toBeVisible();
  });

  test("pinning a project from its kebab keeps it first in Jump back in across a reload", async ({
    page,
  }) => {
    await page.goto("/home");

    const jumpBackIn = page.locator("section").filter({ hasText: "Jump back in" });
    await expect(jumpBackIn).toBeVisible({ timeout: 15000 });

    const projectCard = jumpBackIn.locator(".content-card").filter({ hasText: projectName });
    await expect(projectCard).toBeVisible({ timeout: 15000 });
    await projectCard.getByRole("button", { name: "More" }).click();

    // "Pin to Home" is ambiguous on its own — every other (unpinned) card on
    // the page carries its own standalone bookmark button with the same
    // accessible name — so the click is scoped to the open kebab menu's
    // portal, the only place that name resolves once.
    await page.locator(".MuiPopper-root").getByRole("button", { name: "Pin to Home" }).click();

    // The optimistic pin flips the card's own bookmark to "Unpin" immediately.
    await expect(projectCard.getByRole("button", { name: "Unpin from Home" })).toBeVisible();

    await page.reload();

    const jumpBackInAfterReload = page.locator("section").filter({ hasText: "Jump back in" });
    await expect(jumpBackInAfterReload).toBeVisible({ timeout: 15000 });
    const firstCard = jumpBackInAfterReload.locator(".content-card").first();
    await expect(firstCard).toContainText(projectName, { timeout: 15000 });
  });
});
