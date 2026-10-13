import { type APIRequestContext, type Page, expect } from "@playwright/test";

import { rowCount } from "./datasets";
import { projectLayers } from "./projects";

/** Runs Buffer (100 m) on a layer from the map's toolbox and waits for the
 * job to finish. */
export const runBufferFromToolbox = async (
  page: Page,
  projectId: string,
  layerName: string
): Promise<void> => {
  await page.goto(`/map/${projectId}`);
  await page.getByRole("button", { name: "Open Toolbox" }).click({ timeout: 30000 });
  await page.getByText("Buffer", { exact: true }).first().click();

  await page.getByRole("combobox", { name: "Input layer" }).click();
  await page.getByRole("option", { name: layerName }).click();
  // The distances commit when the field loses focus.
  await page.getByPlaceholder("e.g. 100, 200, 300").fill("100");
  await page.getByPlaceholder("e.g. 100, 200, 300").press("Tab");

  await page.getByRole("button", { name: "Run", exact: true }).click();
  await expect(page.getByText('"Buffer" - Job finished successfully')).toBeVisible({ timeout: 180000 });
};

/** The rows of the project's "Buffer" layer, once it has joined the project. */
export const bufferRows = async (api: APIRequestContext, projectId: string): Promise<number> => {
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
  return rowCount(api, buffer!.layer_id);
};
