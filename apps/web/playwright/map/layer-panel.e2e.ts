import { type Page, expect, test } from "@playwright/test";

import { datasetOf } from "../fixtures/datasets";
import { addDatasetsToProject, createProject, deleteProject } from "../fixtures/projects";
import { API_URL, apiAs, needsAuth } from "../fixtures/users";

/**
 * A project's layer panel: hiding, renaming, styling, the data table and
 * removing a layer, each checked against what the project stores.
 */
needsAuth(test);
// Each step builds on the last, so a retry would start from a changed layer.
test.describe.configure({ mode: "serial", retries: 0 });

let projectId: string;

test.beforeAll(async () => {
  const api = await apiAs("owner");
  try {
    projectId = await createProject(api, `E2E Layer Panel ${Date.now()}`);
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

type ProjectLayer = { id: number; name: string; properties?: Record<string, unknown> };

/** The project's one layer, as stored. */
const storedLayer = async (): Promise<ProjectLayer | undefined> => {
  const api = await apiAs("owner");
  try {
    const layers = await api.get(`${API_URL}/api/v2/project/${projectId}/layer`);
    expect(layers.ok()).toBeTruthy();
    return ((await layers.json()) as ProjectLayer[])[0];
  } finally {
    await api.dispose();
  }
};

const openProject = async (page: Page, layerName: string) => {
  await page.goto(`/map/${projectId}`);
  const row = page.locator(".tree-item").filter({ hasText: layerName });
  await expect(row).toBeVisible({ timeout: 30000 });
  return row;
};

const rowMenu = async (page: Page, layerName: string, item: string) => {
  const row = await openProject(page, layerName);
  await row.getByRole("button", { name: "More Options" }).click();
  await page.getByRole("button", { name: item, exact: true }).click();
};

test("hiding a layer is stored with the project", async ({ page }) => {
  const row = await openProject(page, "E2E Points");
  await row.getByRole("button", { name: "Hide" }).click();
  await expect(row.getByRole("button", { name: "Show" })).toBeVisible();
  await expect.poll(async () => (await storedLayer())?.properties?.visibility).toBe(false);

  await row.getByRole("button", { name: "Show" }).click();
  await expect.poll(async () => (await storedLayer())?.properties?.visibility).toBe(true);
});

test("a fill colour typed as hex is stored as RGB", async ({ page }) => {
  const row = await openProject(page, "E2E Points");
  await row.getByText("E2E Points", { exact: true }).click();
  await expect(page.getByRole("tab", { name: "Style" })).toBeVisible();

  // Fill comes before Stroke; both are labelled "Color".
  await page.getByRole("button", { name: "Color", exact: true }).first().click();
  const saved = page.waitForResponse(
    (r) => r.url().includes(`/project/${projectId}/layer/`) && r.request().method() === "PUT"
  );
  await page.getByLabel("Layer color Hex input").fill("ff0000");
  await saved;
  await expect.poll(async () => (await storedLayer())?.properties?.color).toEqual([255, 0, 0]);
});

test("the data table shows the layer's rows", async ({ page }) => {
  await rowMenu(page, "E2E Points", "View Data");
  await expect(page.getByText("1–25 of 26")).toBeVisible({ timeout: 30000 });
});

test("renaming a layer renames it in the project only", async ({ page }) => {
  await rowMenu(page, "E2E Points", "Rename");
  const dialog = page.getByRole("dialog").filter({ hasText: "Rename project layer" });
  await dialog.getByRole("textbox").fill("Bus stops");
  await dialog.getByRole("button", { name: "Rename", exact: true }).click();
  await expect(dialog).toBeHidden();

  await expect.poll(async () => (await storedLayer())?.name).toBe("Bus stops");
  await expect(page.locator(".tree-item").filter({ hasText: "Bus stops" })).toBeVisible();
});

test("deleting a layer removes it from the project", async ({ page }) => {
  await rowMenu(page, "Bus stops", "Delete");
  const dialog = page.getByRole("dialog").filter({ hasText: "Delete project layer" });
  await dialog.getByRole("button", { name: "Delete", exact: true }).click();
  await expect(dialog).toBeHidden();

  await expect.poll(storedLayer).toBeUndefined();
  // The dataset itself is untouched.
  const api = await apiAs("owner");
  try {
    expect((await api.get(`${API_URL}/api/v2/layer/${datasetOf("points")}`)).status()).toBe(200);
  } finally {
    await api.dispose();
  }
});
