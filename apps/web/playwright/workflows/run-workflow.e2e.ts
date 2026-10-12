import { expect, test } from "@playwright/test";

import { datasetOf } from "../fixtures/datasets";
import { addDatasetsToProject, createProject, deleteProject } from "../fixtures/projects";
import { apiAs, needsAuth } from "../fixtures/users";

/**
 * Running a workflow: the provisioned points into a Buffer, built on the
 * canvas and run in Windmill.
 */
needsAuth(test);
// Jobs run in Windmill and take longer than the suite's default timeout.
test.describe.configure({ timeout: 360000 });

let projectId: string;

test.beforeAll(async () => {
  const api = await apiAs("owner");
  try {
    projectId = await createProject(api, `E2E Workflow Run ${Date.now()}`);
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

test("a dataset into a Buffer runs to completion", async ({ page }) => {
  await page.goto(`/map/${projectId}?mode=workflows`);
  await page.getByRole("button", { name: "New", exact: true }).click({ timeout: 30000 });
  await page.getByRole("menuitem", { name: "From scratch" }).click();
  const pane = page.locator(".react-flow__pane");
  await expect(pane).toBeVisible();

  // A project layer dragged onto the canvas becomes a dataset node bound to
  // it; a tool from the palette becomes a tool node.
  await page
    .getByText("E2E Points", { exact: true })
    .first()
    .dragTo(pane, { targetPosition: { x: 150, y: 150 } });
  await page
    .getByText("Buffer", { exact: true })
    .first()
    .dragTo(pane, { targetPosition: { x: 500, y: 150 } });
  const dataset = page.locator(".react-flow__node").filter({ hasText: "E2E Points" });
  const buffer = page.locator(".react-flow__node").filter({ hasText: "Buffer" });
  await expect(dataset).toBeVisible({ timeout: 10000 });
  await expect(buffer).toBeVisible({ timeout: 10000 });

  // Handles connect by clicking one, then the other.
  await dataset.locator(".react-flow__handle.source").first().click();
  await buffer.locator('.react-flow__handle.target[data-handleid="input_layer_id"]').click();
  await expect(page.locator(".react-flow__edge")).toHaveCount(1);

  await buffer.click();
  const distances = page.getByPlaceholder("e.g. 100, 200, 300");
  await distances.fill("100");
  await distances.press("Tab");

  await page.getByRole("button", { name: "Run", exact: true }).click();
  await expect(page.getByText("Workflow completed successfully")).toBeVisible({ timeout: 300000 });
});
