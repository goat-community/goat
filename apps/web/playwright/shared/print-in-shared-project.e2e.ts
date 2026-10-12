import { expect, test } from "@playwright/test";

import { datasetOf } from "../fixtures/datasets";
import {
  addDatasetsToProject,
  createProject,
  deleteProject,
  shareProjectWithUsers,
} from "../fixtures/projects";
import { actAs, apiAs, needsAuth, userOf } from "../fixtures/users";

/** An editor of a project someone else owns prints one of its layouts. */
needsAuth(test);
// Jobs run in Windmill and take longer than the suite's default timeout.
test.describe.configure({ timeout: 360000 });
actAs(test, "editor");

let projectId: string;

test.beforeAll(async () => {
  const owner = await apiAs("owner");
  try {
    projectId = await createProject(owner, `E2E Shared Print ${Date.now()}`);
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

test("an editor of a shared project prints a layout to PDF", async ({ page }) => {
  // A project without layouts offers one from a template, Blank chosen.
  await page.goto(`/map/${projectId}?mode=reports`);
  const templates = page.getByRole("dialog").filter({ hasText: "New layout from a template" });
  await expect(templates).toBeVisible({ timeout: 30000 });
  await templates.getByRole("button", { name: "Use template" }).click();
  await page
    .getByRole("dialog")
    .filter({ hasText: "Add to project" })
    .getByRole("button", { name: "Add to project" })
    .click();
  await expect(templates).toBeHidden();

  // Only the PDF: an export of the same user finishing meanwhile downloads too.
  const download = page.waitForEvent("download", {
    predicate: (d) => d.suggestedFilename().endsWith(".pdf"),
    timeout: 300000,
  });
  await page.getByRole("button", { name: "Print Layout" }).click();
  const file = await download;
  expect(file.suggestedFilename()).toMatch(/\.pdf$/);
  expect(await file.failure()).toBeNull();
});
