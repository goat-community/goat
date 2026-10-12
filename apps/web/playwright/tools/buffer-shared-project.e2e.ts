import { expect, test } from "@playwright/test";

import { datasetOf, rowCount } from "../fixtures/datasets";
import {
  addDatasetsToProject,
  createProject,
  deleteProject,
  projectLayers,
  shareProjectWithUsers,
} from "../fixtures/projects";
import { actAs, apiAs, needsAuth, userOf } from "../fixtures/users";

/**
 * An editor of a project someone else owns runs a tool in it. The result
 * goes into the project's folder, which belongs to the owner: the editor
 * may write there for this project, and only for it.
 */
needsAuth(test);
// Jobs run in Windmill and take longer than the suite's default timeout.
test.describe.configure({ timeout: 360000 });
actAs(test, "editor");

let projectId: string;

test.beforeAll(async () => {
  const owner = await apiAs("owner");
  try {
    projectId = await createProject(owner, `E2E Shared Buffer ${Date.now()}`);
    await addDatasetsToProject(owner, projectId, [datasetOf("points")]);
    await shareProjectWithUsers(owner, projectId, [{ id: userOf("editor").id, role: "project-editor" }]);
  } finally {
    await owner.dispose();
  }
});

test.afterAll(async () => {
  const owner = await apiAs("owner");
  try {
    await deleteProject(owner, projectId);
  } finally {
    await owner.dispose();
  }
});

test("an editor of a shared project runs Buffer in it", async ({ page }) => {
  await page.goto(`/map/${projectId}`);
  await page.getByRole("button", { name: "Open Toolbox" }).click({ timeout: 30000 });
  await page.getByText("Buffer", { exact: true }).first().click();

  await page.getByRole("combobox", { name: "Input layer" }).click();
  await page.getByRole("option", { name: "E2E Points" }).click();
  // The distances commit when the field loses focus.
  await page.getByPlaceholder("e.g. 100, 200, 300").fill("100");
  await page.getByPlaceholder("e.g. 100, 200, 300").press("Tab");

  await page.getByRole("button", { name: "Run", exact: true }).click();
  await expect(page.getByText('"Buffer" - Job finished successfully')).toBeVisible({ timeout: 180000 });

  const owner = await apiAs("owner");
  try {
    let buffer: { layer_id: string } | undefined;
    await expect
      .poll(
        async () => {
          buffer = (await projectLayers(owner, projectId)).find((layer) => layer.name === "Buffer");
          return !!buffer;
        },
        { timeout: 15000 }
      )
      .toBe(true);
    // The owner sees the editor's result, one buffer per point.
    expect(await rowCount(owner, buffer!.layer_id)).toBe(26);
  } finally {
    await owner.dispose();
  }
});
