import { expect, test } from "@playwright/test";
import path from "path";

import { datasetOf, rowCount } from "../fixtures/datasets";
import { addDatasetsToProject, createProject, deleteProject } from "../fixtures/projects";
import { ensureTeamSpace, spaceItem } from "../fixtures/spaces";
import { bufferRows, runBufferFromToolbox } from "../fixtures/tools";
import { actAs, apiAs, needsAuth, userOf } from "../fixtures/users";

/**
 * A team space: its members edit its content by default, so a member who
 * owns neither the project nor the space runs tools in its projects and
 * uploads into its folders.
 */
needsAuth(test);
// Jobs run in Windmill and take longer than the suite's default timeout.
test.describe.configure({ timeout: 360000 });
actAs(test, "editor");

const TEAM = "E2E Team Space";
let space: { teamId: string; spaceId: string; folderId: string };
let projectId: string;

test.beforeAll(async () => {
  const owner = await apiAs("owner");
  try {
    space = await ensureTeamSpace(owner, TEAM, [userOf("editor").id]);
    projectId = await createProject(owner, `E2E Team Project ${Date.now()}`, space.folderId);
    await addDatasetsToProject(owner, projectId, [datasetOf("points")]);
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

test("a team member runs Buffer in a project of the team's space", async ({ page }) => {
  await runBufferFromToolbox(page, projectId, "E2E Points");
  const owner = await apiAs("owner");
  try {
    expect(await bufferRows(owner, projectId)).toBe(26);
  } finally {
    await owner.dispose();
  }
});

test("a team member uploads a dataset into the team's space", async ({ page }) => {
  await page.goto("/content");
  await page.getByText(TEAM, { exact: true }).click();
  // The space is open once its search offers to look in it.
  await expect(page.getByPlaceholder(new RegExp(`^Search in ${TEAM}`))).toBeVisible({ timeout: 15000 });

  await page.getByRole("button", { name: "Add new" }).click();
  await page.getByRole("menuitem", { name: "Upload dataset" }).click();
  await page.locator('input[type="file"]').setInputFiles(path.join(__dirname, "../fixtures/data/table.csv"));
  const datasetName = `e2e_team_table_${Date.now()}`;
  await page.getByRole("textbox", { name: "Layer name" }).fill(datasetName);
  await page.getByRole("button", { name: "Upload" }).click();
  await expect(page.getByText("1 layer imported")).toBeVisible({ timeout: 120000 });

  // It is in the team space's folder, with every row of the file.
  const editor = await apiAs("editor");
  try {
    const item = await spaceItem(editor, space.spaceId, datasetName);
    expect(item, `no dataset named ${datasetName} in the team space`).toBeTruthy();
    expect(item!.folder_id).toBe(space.folderId);
    expect(await rowCount(editor, item!.id)).toBe(10);
  } finally {
    await editor.dispose();
  }
});
