import { configureStore } from "@reduxjs/toolkit";
import { act, renderHook } from "@testing-library/react";
import type { ReactNode } from "react";
import { Provider } from "react-redux";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { WorkflowIssuesError } from "@/lib/api/workflows";
import { selectWorkflow, setNodes, setWorkflows, workflowReducer } from "@/lib/store/workflow/slice";
import type { Workflow } from "@/lib/validations/workflow";

import { AUTOSAVE_DELAY_MS, useWorkflowAutosave } from "@/hooks/workflows/useWorkflowAutosave";

import { makeIssue } from "@/components/workflows/issues/__tests__/issueFixtures";

const { updateMock } = vi.hoisted(() => ({ updateMock: vi.fn() }));

vi.mock("@/lib/api/workflows", () => {
  class WorkflowIssuesError extends Error {
    constructor(
      public readonly issues: unknown[],
      message = "The workflow has issues."
    ) {
      super(message);
    }
  }
  return { updateWorkflow: updateMock, WorkflowIssuesError };
});

const workflow = {
  id: "wf-1",
  name: "Workflow 1",
  project_id: "p1",
  config: { nodes: [], edges: [], viewport: { x: 0, y: 0, zoom: 1 }, variables: [] },
} as unknown as Workflow;

const note = (id: string) => ({
  id,
  type: "textAnnotation",
  position: { x: 0, y: 0 },
  data: { type: "textAnnotation", text: `<p>${id}</p>` },
});

const setup = (enabled = true) => {
  const store = configureStore({ reducer: { workflow: workflowReducer } });
  store.dispatch(setWorkflows([workflow]));
  store.dispatch(selectWorkflow("wf-1"));
  const onSaved = vi.fn();
  const wrapper = ({ children }: { children: ReactNode }) => <Provider store={store}>{children}</Provider>;
  const hook = renderHook(() => useWorkflowAutosave({ projectId: "p1", enabled, onSaved }), { wrapper });
  return { store, onSaved, hook };
};

const edit = (store: ReturnType<typeof setup>["store"], id = "text-1") =>
  act(() => {
    store.dispatch(setNodes([note(id)] as never));
  });

const wait = (ms: number) =>
  act(async () => {
    await vi.advanceTimersByTimeAsync(ms);
  });

const savedIds = (call: number) =>
  (updateMock.mock.calls[call][2] as { config: { nodes: { id: string }[] } }).config.nodes.map(
    (node) => node.id
  );

describe("useWorkflowAutosave", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    updateMock.mockReset();
    vi.spyOn(console, "error").mockImplementation(() => undefined);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("saves a moment after the last change, once", async () => {
    updateMock.mockResolvedValue({});
    const { store, onSaved } = setup();

    edit(store);
    await wait(AUTOSAVE_DELAY_MS - 1);
    expect(updateMock).not.toHaveBeenCalled();
    await wait(1);

    expect(updateMock).toHaveBeenCalledWith("p1", "wf-1", { config: expect.objectContaining({ edges: [] }) });
    expect(savedIds(0)).toEqual(["text-1"]);
    expect(store.getState().workflow.isDirty).toBe(false);
    expect(onSaved).toHaveBeenCalledTimes(1);

    await wait(5 * AUTOSAVE_DELAY_MS);
    expect(updateMock).toHaveBeenCalledTimes(1);
  });

  it("never saves a workflow it must not write over", async () => {
    const { store } = setup(false);
    edit(store);
    await wait(5 * AUTOSAVE_DELAY_MS);
    expect(updateMock).not.toHaveBeenCalled();
  });

  it("reports a failed save until Retry saves it, without retrying on its own", async () => {
    updateMock.mockRejectedValueOnce(new Error("offline")).mockResolvedValue({});
    const { store, hook } = setup();

    edit(store);
    await wait(AUTOSAVE_DELAY_MS);
    expect(hook.result.current.status).toBe("failed");
    expect(hook.result.current.issues).toEqual([]);

    await wait(5 * AUTOSAVE_DELAY_MS);
    expect(updateMock).toHaveBeenCalledTimes(1);

    await act(async () => {
      hook.result.current.retry();
      await vi.advanceTimersByTimeAsync(0);
    });
    expect(updateMock).toHaveBeenCalledTimes(2);
    expect(hook.result.current.status).toBe("idle");
    expect(store.getState().workflow.isDirty).toBe(false);
  });

  it("carries the issues core lists when it refuses the config as damaged", async () => {
    const damaged = makeIssue({ code: "node_duplicate_id", level: "damaged", params: { id: "a" } });
    updateMock.mockRejectedValueOnce(new WorkflowIssuesError([damaged], "The workflow is damaged."));
    const { store, hook } = setup();

    edit(store);
    await wait(AUTOSAVE_DELAY_MS);

    expect(hook.result.current.status).toBe("failed");
    expect(hook.result.current.issues).toEqual([damaged]);
  });

  it("saves an edit made while the previous save was still under way", async () => {
    let finish: (value: unknown) => void = () => undefined;
    updateMock
      .mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            finish = resolve;
          })
      )
      .mockResolvedValue({});
    const { store } = setup();

    edit(store, "text-1");
    await wait(AUTOSAVE_DELAY_MS);
    expect(updateMock).toHaveBeenCalledTimes(1);

    edit(store, "text-2");
    await act(async () => {
      finish({});
      await vi.advanceTimersByTimeAsync(0);
    });
    expect(store.getState().workflow.isDirty).toBe(true);

    await wait(AUTOSAVE_DELAY_MS);
    expect(updateMock).toHaveBeenCalledTimes(2);
    expect(savedIds(1)).toEqual(["text-2"]);
    expect(store.getState().workflow.isDirty).toBe(false);
  });
});
