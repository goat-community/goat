import { expect, test } from "@playwright/test";

import { datasetOf } from "../fixtures/datasets";
import {
  addDatasetsToProject,
  createBufferWorkflow,
  createProject,
  deleteProject,
  shareProjectWithUsers,
} from "../fixtures/projects";
import { actAs, apiAs, needsAuth, userOf } from "../fixtures/users";

/**
 * A saved workflow, run by an editor of the project it belongs to, who does
 * not own it. Its Buffer still holds the id of a layer that no longer
 * exists for the input its edge feeds, as a workflow keeps after its dataset
 * was replaced: the runner never reads it, so the run must not be refused.
 */
needsAuth(test);
// Jobs run in Windmill and take longer than the suite's default timeout.
test.describe.configure({ timeout: 360000 });
actAs(test, "editor");

let projectId: string;

test.beforeAll(async () => {
  const owner = await apiAs("owner");
  try {
    projectId = await createProject(owner, `E2E Shared Workflow ${Date.now()}`);
    await addDatasetsToProject(owner, projectId, [datasetOf("points")]);
    await createBufferWorkflow(
      owner,
      projectId,
      { id: datasetOf("points"), name: "E2E Points" },
      // A layer id nothing has: the dataset this input once had.
      { name: "Buffer the points", staleInput: "e3c4967b-906f-4f20-a83b-6812b1088ab2" }
    );
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

test("an editor runs a saved workflow in a project shared with them", async ({ page }) => {
  await page.goto(`/map/${projectId}?mode=workflows`);
  // The project's only workflow opens on its own.
  await expect(page.locator(".react-flow__node").filter({ hasText: "Buffer" })).toBeVisible({
    timeout: 30000,
  });

  await page.getByRole("button", { name: "Run", exact: true }).click();
  await expect(page.getByText("Workflow completed successfully")).toBeVisible({ timeout: 300000 });
});
