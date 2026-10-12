import { type Locator, type Page, expect, test } from "@playwright/test";

import { datasetOf } from "../fixtures/datasets";
import { addDatasetsToProject, createProject, deleteProject } from "../fixtures/projects";
import { API_URL, apiAs, needsAuth } from "../fixtures/users";

/**
 * A dashboard from build to public page: a Numbers widget counting the
 * provisioned points, published to the web, seen by an anonymous visitor,
 * then taken offline again.
 */
needsAuth(test);
test.describe.configure({ mode: "serial", retries: 0 });

let projectId: string;
const projectName = `E2E Dashboard ${Date.now()}`;

test.beforeAll(async () => {
  const api = await apiAs("owner");
  try {
    projectId = await createProject(api, projectName);
    await addDatasetsToProject(api, projectId, [datasetOf("points")]);
  } finally {
    await api.dispose();
  }
});

test.afterAll(async () => {
  const api = await apiAs("owner");
  try {
    await deleteProject(api, projectId);
  } finally {
    await api.dispose();
  }
});

/** A pointer drag in small steps: the builder inserts a widget while it is
 * dragged over a panel, which a single jump never reports. */
const dragOnto = async (page: Page, source: Locator, target: Locator): Promise<void> => {
  await source.hover();
  await page.mouse.down();
  const box = (await target.boundingBox())!;
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 20 });
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2 + 5, { steps: 5 });
  await page.mouse.up();
};

const savedProject = (page: Page) =>
  page.waitForResponse(
    (r) => r.request().method() === "PUT" && /\/api\/v2\/project\/[^/?]+$/.test(r.url()) && r.ok()
  );

test("a Numbers widget counts the points", async ({ page }) => {
  await page.goto(`/map/${projectId}?mode=builder`);
  const preview = page.locator(".goat-dashboard-preview");
  await expect(preview).toBeVisible({ timeout: 30000 });

  await dragOnto(
    page,
    page.getByRole("button", { name: "Numbers", exact: true }),
    preview.getByText("Layers").first()
  );

  await page.getByRole("combobox", { name: "Select Layer" }).click();
  await page.getByRole("option", { name: "E2E Points" }).click();
  await page.getByRole("combobox", { name: "Statistic Method" }).click();
  await page.getByRole("option", { name: "Count", exact: true }).click();
  // Counted across the dataset, not just the part in view.
  const saved = savedProject(page);
  await page.getByRole("checkbox", { name: "Filter viewport" }).uncheck();
  await saved;

  await expect(preview.getByText("26", { exact: true })).toBeVisible({ timeout: 30000 });
});

test("publishing puts the dashboard on a public page", async ({ page }) => {
  await page.goto(`/map/${projectId}`);
  await page.getByRole("button", { name: "Share" }).click({ timeout: 30000 });
  const dialog = page.getByRole("dialog").filter({ hasText: "Share “" });
  await dialog.getByRole("tab", { name: "Public" }).click();
  await dialog.getByRole("button", { name: "Publish to web" }).click();
  await expect(dialog.getByText("Published", { exact: true })).toBeVisible({ timeout: 30000 });
  await expect(dialog.getByRole("link", { name: new RegExp(`/map/public/${projectId}$`) })).toBeVisible();
});

test.describe("an anonymous visitor", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test("sees the published dashboard and its count", async ({ page }) => {
    await page.goto(`/map/public/${projectId}`);
    await expect(page).toHaveTitle(new RegExp(projectName));
    await expect(page.getByRole("region", { name: "Map" }).first()).toBeVisible({ timeout: 30000 });
    await expect(page.getByText("26", { exact: true })).toBeVisible({ timeout: 30000 });
  });
});

test("unpublishing takes the public page offline", async ({ page, request }) => {
  await page.goto(`/map/${projectId}`);
  await page.getByRole("button", { name: "Share" }).click({ timeout: 30000 });
  const dialog = page.getByRole("dialog").filter({ hasText: "Share “" });
  await dialog.getByRole("tab", { name: "Public" }).click();
  await dialog.getByRole("button", { name: "Unpublish" }).click();
  await expect(dialog.getByText("This project is private")).toBeVisible({ timeout: 30000 });

  // The public page has nothing left to load: its data answers 404.
  const offline = await request.get(`${API_URL}/api/v2/project/${projectId}/public`);
  expect(offline.status()).toBe(404);
});
