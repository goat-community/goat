import { beforeEach, describe, expect, it, vi } from "vitest";

import { WorkflowIssuesError, updateWorkflow } from "@/lib/api/workflows";

const { fetchMock, mutateMock } = vi.hoisted(() => ({ fetchMock: vi.fn(), mutateMock: vi.fn() }));
vi.mock("@/lib/api/fetcher", () => ({ apiRequestAuth: fetchMock, fetcher: vi.fn() }));
vi.mock("swr", () => ({ default: vi.fn(() => ({})), mutate: mutateMock }));

const PROJECT_ID = "11111111-1111-1111-1111-111111111111";
const WORKFLOW_ID = "22222222-2222-2222-2222-222222222222";
const config = { nodes: [], edges: [], viewport: { x: 0, y: 0, zoom: 1 }, variables: [] };

const DAMAGED = {
  code: "node_duplicate_id",
  level: "damaged",
  node_ids: ["tool-1"],
  field: null,
  message: "Two steps share the id tool-1.",
  params: { id: "tool-1" },
  source: "check",
};

const answer = (status: number, body: unknown) => ({
  ok: false,
  status,
  text: () => Promise.resolve(typeof body === "string" ? body : JSON.stringify(body)),
});

describe("updateWorkflow refusals", () => {
  beforeEach(() => {
    fetchMock.mockReset();
    mutateMock.mockReset();
  });

  it("turns core's refusal of a damaged config into the issues it lists", async () => {
    fetchMock.mockResolvedValue(
      answer(422, { detail: { message: "The workflow is damaged.", issues: [DAMAGED] } })
    );

    const refused = await updateWorkflow(PROJECT_ID, WORKFLOW_ID, { config }).catch((e: unknown) => e);

    expect(refused).toBeInstanceOf(WorkflowIssuesError);
    expect((refused as WorkflowIssuesError).issues).toEqual([DAMAGED]);
    expect(mutateMock).not.toHaveBeenCalled();
  });

  it("keeps a request validation error (422 with a list) a plain failure", async () => {
    fetchMock.mockResolvedValue(answer(422, { detail: [{ loc: ["body", "name"], msg: "too long" }] }));

    const failure = await updateWorkflow(PROJECT_ID, WORKFLOW_ID, { config }).catch((e: unknown) => e);

    expect(failure).not.toBeInstanceOf(WorkflowIssuesError);
    expect((failure as Error).message).toBe("Failed to update workflow");
  });

  it("keeps any other failure a plain failure", async () => {
    fetchMock.mockResolvedValue(answer(500, "Internal Server Error"));

    await expect(updateWorkflow(PROJECT_ID, WORKFLOW_ID, { config })).rejects.toThrow(
      "Failed to update workflow"
    );
  });
});
