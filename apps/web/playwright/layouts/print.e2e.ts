import { expect, test } from "@playwright/test";

import { datasetOf } from "../fixtures/datasets";
import { addDatasetsToProject, createProject, deleteProject } from "../fixtures/projects";
import { apiAs, needsAuth } from "../fixtures/users";

/**
 * Printing a layout to PDF: the print worker opens the layout in its own
 * browser, renders it and stores the file, which the jobs menu then hands
 * to this browser.
 */
needsAuth(test);
// Jobs run in Windmill and take longer than the suite's default timeout.
test.describe.configure({ timeout: 360000 });

let projectId: string;

test.beforeAll(async () => {
  const api = await apiAs("owner");
  try {
    projectId = await createProject(api, `E2E Print ${Date.now()}`);
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

test("a new layout prints to a PDF", async ({ page }) => {
  // A project without layouts offers one from a template on its own, with
  // Blank chosen.
  await page.goto(`/map/${projectId}?mode=reports`);
  const templates = page.getByRole("dialog").filter({ hasText: "New layout from a template" });
  await expect(templates).toBeVisible({ timeout: 30000 });
  await templates.getByRole("button", { name: "Use template" }).click();
  const confirm = page.getByRole("dialog").filter({ hasText: "Add to project" });
  await confirm.getByRole("button", { name: "Add to project" }).click();
  await expect(templates).toBeHidden();

  const print = page.getByRole("button", { name: "Print Layout" });
  await expect(print).toBeEnabled();
  // Stay on the page until the file arrives: the jobs menu only downloads
  // jobs it saw running.
  const download = page.waitForEvent("download", { timeout: 300000 });
  await print.click();

  const file = await download;
  expect(file.suggestedFilename()).toMatch(/\.pdf$/);
  expect(await file.failure()).toBeNull();
});
