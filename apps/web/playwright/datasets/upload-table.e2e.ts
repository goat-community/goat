import { expect, test } from "@playwright/test";
import path from "path";

import { deleteContentItem } from "../fixtures/content";
import { datasetIdByName, rowCount } from "../fixtures/datasets";
import { apiAs } from "../fixtures/users";

// Jobs run in Windmill and take longer than the suite's default timeout.
test.describe.configure({ timeout: 360000 });
const FIXTURES_DIR = path.join(__dirname, "../fixtures/data");

test.describe("Dataset Upload - Non-Spatial Table", () => {
  test("upload a CSV table", async ({ page }) => {
    await page.goto("/content");

    // Add new -> Upload dataset opens the upload dialog directly.
    await page.getByRole("button", { name: "Add new" }).click();
    await page.getByRole("menuitem", { name: "Upload dataset" }).click();

    await expect(page.getByRole("dialog").getByText("Upload dataset", { exact: true })).toBeVisible();

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(path.join(FIXTURES_DIR, "table.csv"));

    const nameField = page.getByRole("textbox", { name: "Layer name" });
    await expect(nameField).toHaveValue("table");
    const datasetName = `e2e_table_${Date.now()}`;
    await nameField.fill(datasetName);

    // The dialog hands the file over and closes; the import job runs on in
    // Windmill and the job tray announces the result.
    const uploadButton = page.getByRole("button", { name: "Upload" });
    await expect(uploadButton).toBeEnabled();
    await uploadButton.click();
    await expect(page.getByRole("dialog").getByText("Upload dataset", { exact: true })).toBeHidden({
      timeout: 10000,
    });
    await expect(page.getByText("1 layer imported")).toBeVisible({ timeout: 120000 });

    // Every row of the file is in the dataset geoapi serves.
    const api = await apiAs("owner");
    try {
      const layerId = await datasetIdByName(api, datasetName);
      expect(layerId, `no dataset named ${datasetName}`).toBeTruthy();
      expect(await rowCount(api, layerId as string)).toBe(10);
    } finally {
      await api.dispose();
    }

    await deleteContentItem(page, datasetName);
  });
});
