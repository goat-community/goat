import { type APIRequestContext, expect, test } from "@playwright/test";

import { createProject, deleteProject, shareProjectWithUsers } from "../fixtures/projects";
import { API_URL, actAs, apiAs, needsAuth, userOf } from "../fixtures/users";

/**
 * Who may reach a project in someone's personal space.
 *
 * The owner creates a private project. A user in another organization is
 * refused it outright. A colleague it is shared with as a viewer sees it
 * under "Shared with me" and can open it, but can neither delete it from the
 * card's menu nor through the API.
 */
needsAuth(test);
test.describe.configure({ mode: "serial" });

let owner: APIRequestContext;
let projectId: string;
const projectName = `E2E Access ${Date.now()}`;

test.beforeAll(async () => {
  owner = await apiAs("owner");
  projectId = await createProject(owner, projectName);
  await shareProjectWithUsers(owner, projectId, [{ id: userOf("viewer").id, role: "project-viewer" }]);
});

test.afterAll(async () => {
  await deleteProject(owner, projectId);
  await owner.dispose();
});

test.describe("an outsider", () => {
  actAs(test, "outsider");

  test("is refused the project and does not see it anywhere", async ({ page }) => {
    const outsider = await apiAs("outsider");
    try {
      // core answers a refused permission check with 401, a refused
      // resource with 403 or 404: any of them is a refusal.
      const read = await outsider.get(`${API_URL}/api/v2/project/${projectId}`);
      expect([401, 403, 404]).toContain(read.status());
      const removed = await outsider.delete(`${API_URL}/api/v2/project/${projectId}`);
      expect([401, 403, 404]).toContain(removed.status());
    } finally {
      await outsider.dispose();
    }

    await page.goto("/content/shared");
    await expect(page.getByRole("heading", { name: "Content" })).toBeVisible();
    await expect(page.getByText(projectName)).toHaveCount(0);
  });
});

test.describe("a viewer it is shared with", () => {
  actAs(test, "viewer");

  test("sees it under Shared with me but cannot delete it", async ({ page }) => {
    await page.goto("/content/shared");
    const card = page.locator(".content-card").filter({ hasText: projectName });
    await expect(card).toBeVisible({ timeout: 15000 });

    // The card's menu offers no Delete to a viewer.
    await card.getByRole("button", { name: "More" }).click();
    await expect(page.getByRole("button", { name: "Delete" })).toHaveCount(0);
    await page.keyboard.press("Escape");

    // Nor does the API let them.
    const viewer = await apiAs("viewer");
    try {
      const removed = await viewer.delete(`${API_URL}/api/v2/project/${projectId}`);
      expect([401, 403, 404]).toContain(removed.status());
      const read = await viewer.get(`${API_URL}/api/v2/project/${projectId}`);
      expect(read.status()).toBe(200);
    } finally {
      await viewer.dispose();
    }
  });
});

test("the owner still has the project afterwards", async () => {
  const read = await owner.get(`${API_URL}/api/v2/project/${projectId}`);
  expect(read.status()).toBe(200);
});
