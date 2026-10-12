import { expect, test } from "@playwright/test";

import { datasetOf, shareDatasetWithUsers } from "../fixtures/datasets";
import { actAs, apiAs, needsAuth, userOf } from "../fixtures/users";

/**
 * Downloading a dataset someone else owns and shared: the export reads the
 * owner's data on behalf of the person it was shared with.
 */
needsAuth(test);
// Jobs run in Windmill and take longer than the suite's default timeout.
test.describe.configure({ timeout: 360000 });
actAs(test, "editor");

test.beforeAll(async () => {
  const owner = await apiAs("owner");
  try {
    await shareDatasetWithUsers(owner, datasetOf("table"), [
      { id: userOf("editor").id, role: "layer-viewer" },
    ]);
  } finally {
    await owner.dispose();
  }
});

test("a dataset shared with you downloads", async ({ page }) => {
  await page.goto("/content/shared");
  const card = page.locator(".content-card").filter({ hasText: "E2E Table" });
  await expect(card).toBeVisible({ timeout: 30000 });
  await card.getByRole("button", { name: "More" }).click();
  await page.getByRole("button", { name: "Download" }).click();

  const dialog = page.getByRole("dialog").filter({ hasText: "Download Type" });
  // Stay on the page until the file arrives: the jobs menu only downloads
  // jobs it saw running.
  const download = page.waitForEvent("download", { timeout: 180000 });
  await dialog.getByRole("button", { name: "Download" }).click();

  const file = await download;
  expect(file.suggestedFilename()).toMatch(/\.zip$/);
  expect(await file.failure()).toBeNull();
});
