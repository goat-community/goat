import { expect, test } from "@playwright/test";

test.describe("Navigation & Smoke Tests", () => {
  test("home page loads and shows the greeting", async ({ page }) => {
    await page.goto("/home");
    await expect(page).toHaveTitle(/GOAT/);
    await expect(page.getByRole("heading", { name: /Welcome/ })).toBeVisible();
  });

  test("can navigate to all main sections", async ({ page }) => {
    await page.goto("/home");

    // Navigate to Content
    await page.getByRole("link", { name: "Content" }).click();
    await expect(page.getByRole("heading", { name: "Content" })).toBeVisible();
    // Exact — a substring match also catches the "Team spaces" row header.
    await expect(page.getByText("Spaces", { exact: true })).toBeVisible();

    // Navigate to Catalog
    await page.getByRole("link", { name: "Catalog" }).click();
    await expect(page.getByRole("heading", { name: "Catalog" })).toBeVisible();

    // Navigate to Settings
    await page.getByRole("link", { name: "Settings" }).click();
    await expect(page.getByRole("heading", { name: "Settings" })).toBeVisible();

    // Navigate back Home
    await page.getByRole("link", { name: "Home" }).click();
    await expect(page.getByRole("heading", { name: /Welcome/ })).toBeVisible();
  });

  test("home's hero shows the quick-create actions", async ({ page }) => {
    await page.goto("/home");
    await expect(page.getByRole("heading", { name: /Welcome/ })).toBeVisible();
    await expect(page.getByRole("button", { name: "New project" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Upload dataset" })).toBeVisible();
  });
});
