import { expect, test } from "@playwright/test";

import { datasetOf, rowCount } from "../fixtures/datasets";
import { addDatasetsToProject, createProject, deleteProject, projectLayers } from "../fixtures/projects";
import { apiAs, needsAuth } from "../fixtures/users";

/**
 * Running an analysis tool from the map's toolbox: Buffer on the provisioned
 * points. The job runs in Windmill and its result joins the project.
 */
needsAuth(test);
// Jobs run in Windmill and take longer than the suite's default timeout.
test.describe.configure({ timeout: 360000 });

let projectId: string;

test.beforeAll(async () => {
  const api = await apiAs("owner");
  try {
    projectId = await createProject(api, `E2E Buffer ${Date.now()}`);
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

test("buffering the points adds a Buffer layer to the project", async ({ page }) => {
  await page.goto(`/map/${projectId}`);
  await page.getByRole("button", { name: "Open Toolbox" }).click({ timeout: 30000 });
  await page.getByText("Buffer", { exact: true }).first().click();

  await page.getByRole("combobox", { name: "Input layer" }).click();
  await page.getByRole("option", { name: "E2E Points" }).click();
  // The distances commit when the field loses focus.
  await page.getByPlaceholder("e.g. 100, 200, 300").fill("100");
  await page.getByPlaceholder("e.g. 100, 200, 300").press("Tab");

  const run = page.getByRole("button", { name: "Run", exact: true });
  await expect(run).toBeEnabled();
  await run.click();
  await expect(page.getByText('"Buffer" - Job finished successfully')).toBeVisible({ timeout: 180000 });

  // The result joins the project, one buffer per point.
  const api = await apiAs("owner");
  try {
    let buffer: { layer_id: string } | undefined;
    await expect
      .poll(
        async () => {
          buffer = (await projectLayers(api, projectId)).find((layer) => layer.name === "Buffer");
          return !!buffer;
        },
        { timeout: 15000 }
      )
      .toBe(true);
    expect(await rowCount(api, buffer!.layer_id)).toBe(26);
  } finally {
    await api.dispose();
  }
});
