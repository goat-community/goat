import { type Page, expect, test } from "@playwright/test";

import { deleteContentItem } from "../fixtures/content";

/** The Workflows panel's "New" button opens a menu; "From scratch" creates
 * an empty workflow and opens its canvas. */
const newWorkflow = async (page: Page) => {
  await page.getByRole("button", { name: "New", exact: true }).click();
  await page.getByRole("menuitem", { name: "From scratch" }).click();
};

test.describe("Workflow Management", () => {
  // Set by beforeEach, read by afterEach — safe as a describe-scoped
  // variable because Playwright never runs two tests of the same describe
  // concurrently within one worker.
  let projectName: string;

  test.beforeEach(async ({ page }) => {
    // Create a fresh project for workflow tests. The old dedicated
    // /projects page now redirects to /content; project creation lives
    // behind its "Add new" menu instead.
    await page.goto("/content");
    await page.getByRole("button", { name: "Add new" }).click();
    await page.getByRole("menuitem", { name: "Blank project" }).click();
    await expect(page.getByRole("dialog").getByText("New project", { exact: true })).toBeVisible();

    // The dialog asks for a name and nothing else — the destination is the
    // folder being browsed.
    projectName = `E2E Workflow Test ${Date.now()}`;
    await page.getByLabel("New project").fill(projectName);
    await page.getByRole("button", { name: "Create project" }).click();

    await expect(page).toHaveURL(/\/map\//, { timeout: 30000 });
  });

  test.afterEach(async ({ page }) => {
    await deleteContentItem(page, projectName);
  });

  test("create a new workflow and see the canvas", async ({ page }) => {
    // Switch to Workflows tab
    await page.getByText("Workflows").click();

    // Should see workflows panel
    await expect(page.getByRole("heading", { name: "Workflows" })).toBeVisible();

    // Create a new workflow: "New" opens a menu, "From scratch" starts empty.
    await newWorkflow(page);

    // Should see the workflow canvas with toolbar
    await expect(page.getByRole("button", { name: "Run" })).toBeVisible({ timeout: 5000 });
    await expect(page.getByRole("button", { name: "Select" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Zoom In" })).toBeVisible();

    // Tools panel should be visible with tool categories
    await expect(page.getByText("Geoprocessing")).toBeVisible();
    await expect(page.getByText("Buffer")).toBeVisible();
    await expect(page.getByText("Accessibility Indicators")).toBeVisible();
  });

  test("add a tool node by dragging it onto the canvas", async ({ page }) => {
    await page.getByText("Workflows").click();
    await newWorkflow(page);
    await expect(page.getByRole("button", { name: "Run" })).toBeVisible({ timeout: 5000 });

    // A real pointer drag: the palette reads what is dragged in React's
    // onDragStart, which synthetic DragEvents never reach.
    await page.getByText("Buffer", { exact: true }).first().dragTo(page.locator(".react-flow__pane"));
    await expect(page.locator(".react-flow__node").filter({ hasText: "Buffer" })).toBeVisible({
      timeout: 10000,
    });
  });

  test("the canvas zooms out below React Flow's default limit", async ({ page }) => {
    await page.getByText("Workflows").click();
    await newWorkflow(page);
    await expect(page.getByRole("button", { name: "Run" })).toBeVisible({ timeout: 5000 });

    // React Flow stops at 0.5 by default, too tight to see a large workflow
    // as a whole; the canvas allows zooming out to 0.1.
    const scale = async () =>
      page
        .locator(".react-flow__viewport")
        .evaluate((el) => new DOMMatrixReadOnly(getComputedStyle(el).transform).a);
    const zoomOut = page.getByRole("button", { name: "Zoom Out" });
    for (let i = 0; i < 20; i++) await zoomOut.click();
    await expect.poll(scale).toBeLessThan(0.5);
    expect(await scale()).toBeGreaterThanOrEqual(0.1 - 1e-6);
  });

  test("tools panel search works", async ({ page }) => {
    await page.getByText("Workflows").click();
    await newWorkflow(page);
    await expect(page.getByRole("button", { name: "Run" })).toBeVisible({ timeout: 5000 });

    // Search for a tool
    const searchBox = page.getByPlaceholder("Search");
    await searchBox.fill("buffer");

    // Buffer should be visible, other tools should be hidden
    await expect(page.getByText("Buffer")).toBeVisible();
    await expect(page.getByText("Geoprocessing")).toBeVisible();

    // Clear search and verify all categories return
    await searchBox.clear();
    await expect(page.getByText("Accessibility Indicators")).toBeVisible();
    await expect(page.getByText("Geoanalysis")).toBeVisible();
    await expect(page.getByText("Data Management")).toBeVisible();
  });
});
