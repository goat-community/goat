import { describe, expect, it } from "vitest";

import {
  workflowReducer as reducer,
  selectWorkflow,
  setNodes,
  setVariables,
  setWorkflows,
  syncToWorkflowConfig,
} from "@/lib/store/workflow/slice";
import type { Workflow } from "@/lib/validations/workflow";

const node = (id: string) => ({
  id,
  type: "textAnnotation",
  position: { x: 0, y: 0 },
  data: { text: id },
});

const workflow = (id: string, nodeIds: string[]): Workflow =>
  ({
    id,
    name: id,
    project_id: "p1",
    config: { nodes: nodeIds.map(node), edges: [], viewport: { x: 0, y: 0, zoom: 1 }, variables: [] },
    created_at: "2026-09-11T00:00:00Z",
    updated_at: "2026-09-11T00:00:00Z",
  }) as unknown as Workflow;

const initial = reducer(undefined, { type: "@@init" });

describe("workflow slice — a workflow selected before the list carried it", () => {
  it("loads its config once setWorkflows brings the workflow in", () => {
    // A workflow created from a template is selected by the panel the moment
    // its own list has it; the layout's copy of the list reaches the store a
    // render later. The canvas must not stay empty in between and, worse,
    // auto-save that emptiness back over the freshly created config.
    let state = reducer(initial, selectWorkflow("wf-new"));
    expect(state.selectedWorkflowId).toBe("wf-new");
    expect(state.nodes).toEqual([]);

    state = reducer(state, setWorkflows([workflow("wf-new", ["a", "b", "c"])]));
    expect(state.nodes.map((n) => n.id)).toEqual(["a", "b", "c"]);
    expect(state.isDirty).toBe(false);
  });

  it("leaves a canvas the author already changed alone", () => {
    let state = reducer(initial, setWorkflows([workflow("wf-1", ["a"])]));
    state = reducer(state, selectWorkflow("wf-1"));
    state = reducer(state, setNodes([node("a"), node("typed")] as never));
    expect(state.isDirty).toBe(true);

    state = reducer(state, setWorkflows([workflow("wf-1", ["a"])]));
    expect(state.nodes.map((n) => n.id)).toEqual(["a", "typed"]);
  });

  it("keeps a selected workflow's loaded canvas when the list merely refreshes", () => {
    let state = reducer(initial, setWorkflows([workflow("wf-1", ["a", "b"])]));
    state = reducer(state, selectWorkflow("wf-1"));
    state = reducer(state, setWorkflows([workflow("wf-1", ["a", "b"]), workflow("wf-2", ["z"])]));
    expect(state.nodes.map((n) => n.id)).toEqual(["a", "b"]);
  });
});

describe("workflow slice — variable labels and descriptions", () => {
  const labelled = {
    id: "var-1",
    name: "max_abstand_gruppierung",
    label: "Maximaler Abstand",
    description: "Größter Abstand zwischen zwei Punkten einer Gruppe, in Metern.",
    type: "number" as const,
    defaultValue: 250,
    order: 0,
  };
  const legacy = { id: "var-2", name: "radius", type: "number" as const, defaultValue: 100, order: 1 };

  const withVariables = (variables: unknown[]): Workflow =>
    ({
      ...workflow("wf-vars", ["a"]),
      config: { nodes: [node("a")], edges: [], viewport: { x: 0, y: 0, zoom: 1 }, variables },
    }) as unknown as Workflow;

  it("loads label and description with the workflow, and a legacy variable as it was", () => {
    let state = reducer(initial, setWorkflows([withVariables([labelled, legacy])]));
    state = reducer(state, selectWorkflow("wf-vars"));

    expect(state.variables).toEqual([labelled, legacy]);
    expect(state.variables[1]).not.toHaveProperty("label");
    expect(state.variables[1]).not.toHaveProperty("description");
  });

  it("writes them back into the config it saves", () => {
    let state = reducer(initial, setWorkflows([withVariables([legacy])]));
    state = reducer(state, selectWorkflow("wf-vars"));
    state = reducer(state, setVariables([labelled, legacy]));
    state = reducer(state, syncToWorkflowConfig());

    const saved = state.workflows.find((w) => w.id === "wf-vars")?.config.variables;
    expect(saved).toEqual([labelled, legacy]);
  });
});


describe("workflow slice — a stored config the canvas cannot draw", () => {
  const damaged = (config: unknown): Workflow =>
    ({ ...workflow("wf-bad", []), config }) as unknown as Workflow;

  it("opens as an empty canvas instead of throwing", () => {
    let state = reducer(initial, setWorkflows([damaged({ nodes: "not a list", edges: [] })]));
    state = reducer(state, selectWorkflow("wf-bad"));
    expect(state.nodes).toEqual([]);
    expect(state.edges).toEqual([]);
    expect(state.variables).toEqual([]);
  });

  it("also when the list brings it after it was selected", () => {
    let state = reducer(initial, selectWorkflow("wf-bad"));
    state = reducer(state, setWorkflows([damaged({ nodes: [{ id: "a", type: "tool", data: {} }], edges: [] })]));
    expect(state.nodes).toEqual([]);
  });

  it("keeps the stored config as it is, for the notice and the check", () => {
    const config = { nodes: [{ id: "a", type: "chart", position: { x: 0, y: 0 }, data: {} }], edges: [] };
    let state = reducer(initial, setWorkflows([damaged(config)]));
    state = reducer(state, selectWorkflow("wf-bad"));
    expect(state.workflows[0].config).toEqual(config);
  });
});
