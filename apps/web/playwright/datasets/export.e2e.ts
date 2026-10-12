import { expect, test } from "@playwright/test";

import { locateContentCard } from "../fixtures/content";
import { needsAuth } from "../fixtures/users";

/**
 * Downloading a dataset: the export job runs in Windmill and the jobs menu
 * hands the file to the browser when it finishes.
 *
 * Needs the provisioned datasets, which only exist with auth on.
 */
needsAuth(test);
// Jobs run in Windmill and take longer than the suite's default timeout.
test.describe.configure({ timeout: 360000 });

test("a dataset downloads as a zipped GeoPackage", async ({ page }) => {
  const card = await locateContentCard(page, "E2E Points");
  expect(card, "the provisioned dataset is not in My Content").not.toBeNull();
  await card!.getByRole("button", { name: "More" }).click();
  await page.getByRole("button", { name: "Download" }).click();

  const dialog = page.getByRole("dialog").filter({ hasText: "Download Type" });
  await expect(dialog.getByRole("combobox", { name: "GeoPackage" })).toBeVisible();

  // The file arrives when the job finishes; stay on the page until then,
  // as the jobs menu only downloads jobs it saw running.
  const download = page.waitForEvent("download", { timeout: 180000 });
  await dialog.getByRole("button", { name: "Download" }).click();
  await expect(page.getByText("Export started. Check the jobs menu for progress.")).toBeVisible();

  const file = await download;
  expect(file.suggestedFilename()).toMatch(/\.zip$/);
  expect(await file.failure()).toBeNull();
});
