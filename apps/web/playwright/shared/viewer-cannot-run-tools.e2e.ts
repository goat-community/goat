import { expect, test } from "@playwright/test";

import { datasetOf } from "../fixtures/datasets";
import {
  addDatasetsToProject,
  createProject,
  deleteProject,
  shareProjectWithUsers,
} from "../fixtures/projects";
import { API_URL, actAs, apiAs, needsAuth, userOf } from "../fixtures/users";

/**
 * A viewer of a shared project sees it but changes nothing: the toolbox is
 * not offered, and processes refuses a tool run that would write into the
 * project even when asked directly.
 */
needsAuth(test);
actAs(test, "viewer");

const PROCESSES_URL = process.env.NEXT_PUBLIC_PROCESSES_URL ?? "http://127.0.0.1:8300";

let projectId: string;
let folderId: string;

test.beforeAll(async () => {
  const owner = await apiAs("owner");
  try {
    projectId = await createProject(owner, `E2E Viewer Tools ${Date.now()}`);
    await addDatasetsToProject(owner, projectId, [datasetOf("points")]);
    await shareProjectWithUsers(owner, projectId, [{ id: userOf("viewer").id, role: "project-viewer" }]);
    const project = await owner.get(`${API_URL}/api/v2/project/${projectId}`);
    folderId = ((await project.json()) as { folder_id: string }).folder_id;
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

test("a viewer of a shared project is not offered the toolbox", async ({ page }) => {
  await page.goto(`/map/${projectId}`);
  await expect(page.locator(".tree-item").filter({ hasText: "E2E Points" })).toBeVisible({ timeout: 30000 });
  await expect(page.getByRole("button", { name: "Open Toolbox" })).toHaveCount(0);
});

test("processes refuses a viewer's tool run into the project", async () => {
  const viewer = await apiAs("viewer");
  try {
    const run = await viewer.post(`${PROCESSES_URL}/processes/buffer/execution`, {
      data: {
        inputs: {
          input_layer_id: datasetOf("points"),
          distances: [100],
          project_id: projectId,
          folder_id: folderId,
        },
      },
    });
    expect([401, 403, 404]).toContain(run.status());
  } finally {
    await viewer.dispose();
  }
});
