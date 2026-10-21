/**
 * A dataset step without a layer (a template's open input, or an empty step
 * from the palette) is reported by the workflow check as `layer_not_chosen`.
 * The node shows that issue on its badge and keeps its "Pick a layer" action,
 * which selects the node so the sidebar opens on its Dataset settings.
 */
import { configureStore } from "@reduxjs/toolkit";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ComponentProps } from "react";
import React from "react";
import { Provider } from "react-redux";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { workflowReducer } from "@/lib/store/workflow/slice";
import type { DatasetNodeData } from "@/lib/validations/workflow";

import { makeIssue } from "@/components/workflows/issues/__tests__/issueFixtures";
import DatasetNode from "@/components/workflows/nodes/DatasetNode";

const { issuesByNode } = vi.hoisted(() => ({ issuesByNode: new Map<string, unknown[]>() }));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock("next/navigation", () => ({
  useParams: () => ({ projectId: "p1" }),
}));

vi.mock("@xyflow/react", () => ({
  Handle: () => null,
  NodeToolbar: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  Position: { Top: "top", Right: "right", Left: "left", Bottom: "bottom" },
}));

vi.mock("@/lib/api/layers", () => ({
  useDatasetCollectionItems: () => ({ data: undefined }),
}));

vi.mock("@/lib/api/projects", () => ({
  useProjectLayers: () => ({ layers: [] }),
}));

vi.mock("@/hooks/map/CommonHooks", () => ({
  default: () => ({ layerFields: [] }),
}));

vi.mock("@/components/workflows/issues/WorkflowIssuesContext", () => ({
  useStepIssues: (nodeId: string) => issuesByNode.get(nodeId) ?? [],
  useWorkflowIssuesContext: () => ({
    issues: [],
    byNode: issuesByNode,
    blockingCount: 0,
    damaged: [],
    focus: vi.fn(),
    focusRequest: null,
  }),
}));

vi.mock("@/lib/utils/workflowIssueText", () => ({
  issueText: (_t: unknown, issue: { message: string }) => issue.message,
}));

type DatasetNodeProps = ComponentProps<typeof DatasetNode>;

const makeStore = () => configureStore({ reducer: { workflow: workflowReducer } });

const nodeProps = (data: DatasetNodeData): DatasetNodeProps =>
  ({
    id: "dataset-1",
    type: "dataset",
    data,
    selected: false,
    dragging: false,
    zIndex: 0,
    isConnectable: true,
    positionAbsoluteX: 0,
    positionAbsoluteY: 0,
  }) as unknown as DatasetNodeProps;

const renderNode = (data: DatasetNodeData, store: ReturnType<typeof makeStore>) =>
  render(
    <Provider store={store}>
      <DatasetNode {...nodeProps(data)} />
    </Provider>
  );

const baseData: DatasetNodeData = { type: "dataset", label: "Dataset" };
const notChosen = makeIssue({ code: "layer_not_chosen", node_ids: ["dataset-1"], message: "Dataset: no layer chosen." });

describe("DatasetNode without a chosen layer", () => {
  let store: ReturnType<typeof makeStore>;

  beforeEach(() => {
    store = makeStore();
    issuesByNode.clear();
  });

  it("shows nothing extra while the check reports nothing for the step", () => {
    renderNode(baseData, store);
    expect(screen.queryByTestId("step-issue-badge")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "pick_a_layer" })).not.toBeInTheDocument();
  });

  it("shows the issue on its badge and offers Pick a layer", async () => {
    issuesByNode.set("dataset-1", [notChosen]);
    renderNode(baseData, store);
    await expect(screen.getByTestId("step-issue-badge")).toHaveAttribute("data-severity", "error");
    expect(screen.getByRole("button", { name: "pick_a_layer" })).toBeInTheDocument();
  });

  it("selects the node (opening its Dataset settings picker) when Pick a layer is clicked", async () => {
    issuesByNode.set("dataset-1", [notChosen]);
    const user = userEvent.setup();
    renderNode(baseData, store);

    await user.click(screen.getByRole("button", { name: "pick_a_layer" }));

    expect(store.getState().workflow.selectedNodeId).toBe("dataset-1");
  });

  it("drops the action once the check no longer reports the layer as missing", () => {
    issuesByNode.set("dataset-1", [notChosen]);
    const { rerender } = renderNode(baseData, store);
    expect(screen.getByRole("button", { name: "pick_a_layer" })).toBeInTheDocument();

    issuesByNode.clear();
    rerender(
      <Provider store={store}>
        <DatasetNode {...nodeProps({ ...baseData, layerId: "11111111-1111-4111-8111-111111111111" })} />
      </Provider>
    );

    expect(screen.queryByTestId("step-issue-badge")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "pick_a_layer" })).not.toBeInTheDocument();
  });

  it("follows the check rather than the template's own flag", () => {
    renderNode({ ...baseData, unresolved: true } as DatasetNodeData, store);
    expect(screen.queryByRole("button", { name: "pick_a_layer" })).not.toBeInTheDocument();
  });
});
