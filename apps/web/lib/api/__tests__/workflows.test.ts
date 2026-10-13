import { beforeEach, describe, expect, it, vi } from "vitest";

import { PROJECTS_API_BASE_URL } from "@/lib/api/projects";
import { WorkflowRefusedError, executeWorkflow, refreshWorkflow, updateWorkflow } from "@/lib/api/workflows";

const { fetchMock, mutateMock } = vi.hoisted(() => ({ fetchMock: vi.fn(), mutateMock: vi.fn() }));
vi.mock("@/lib/api/fetcher", () => ({ apiRequestAuth: fetchMock, fetcher: vi.fn() }));
vi.mock("swr", () => ({ default: vi.fn(() => ({})), mutate: mutateMock }));

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";
const WORKFLOW_ID = "22222222-2222-2222-2222-222222222222";
const itemKey = [`${PROJECTS_API_BASE_URL}/${PROJECT_ID}/workflow/${WORKFLOW_ID}`];

const config = { nodes: [], edges: [], viewport: { x: 0, y: 0, zoom: 1 }, variables: [] };

describe("workflows api cache invalidation", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    mutateMock.mockReset();
  });

  it("invalidates the workflow key after a successful update, so a saved config is never read stale", async () => {
    fetchMock.mockResolvedValue({ ok: true, json: () => Promise.resolve({ id: WORKFLOW_ID }) });

    const updated = await updateWorkflow(PROJECT_ID, WORKFLOW_ID, { config });

    expect(updated).toEqual({ id: WORKFLOW_ID });
    expect(mutateMock).toHaveBeenCalledTimes(1);
    expect(mutateMock).toHaveBeenCalledWith(itemKey);
  });

  it("does not invalidate when the update fails", async () => {
    fetchMock.mockResolvedValue({ ok: false, json: () => Promise.resolve({}) });

    await expect(updateWorkflow(PROJECT_ID, WORKFLOW_ID, { config })).rejects.toThrow(
      "Failed to update workflow"
    );
    expect(mutateMock).not.toHaveBeenCalled();
  });

  it("refreshWorkflow invalidates the array key the read hook uses", () => {
    refreshWorkflow(PROJECT_ID, WORKFLOW_ID);
    expect(mutateMock).toHaveBeenCalledWith(itemKey);
  });
});

describe("executeWorkflow refusals", () => {
  const request = { project_id: PROJECT_ID, nodes: [], edges: [] } as unknown as Parameters<
    typeof executeWorkflow
  >[1];

  beforeEach(() => {
    fetchMock.mockReset();
  });

  it("turns a refusal into the nodes it names", async () => {
    const body = {
      detail: { message: "Resource not found", refused_nodes: ["schools"], destination_refused: false },
    };
    fetchMock.mockResolvedValue({
      ok: false,
      status: 404,
      text: () => Promise.resolve(JSON.stringify(body)),
    });

    const refused = await executeWorkflow(WORKFLOW_ID, request).catch((e: unknown) => e);

    expect(refused).toBeInstanceOf(WorkflowRefusedError);
    expect((refused as WorkflowRefusedError).refusedNodes).toEqual(["schools"]);
    expect((refused as WorkflowRefusedError).destinationRefused).toBe(false);
  });

  it("keeps any other failure as it was", async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 500,
      text: () => Promise.resolve("Internal Server Error"),
    });

    await expect(executeWorkflow(WORKFLOW_ID, request)).rejects.toThrow(
      "Failed to execute workflow: Internal Server Error"
    );
  });
});
