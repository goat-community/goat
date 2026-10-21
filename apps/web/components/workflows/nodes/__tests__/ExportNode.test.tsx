import { configureStore } from "@reduxjs/toolkit";
import { render, screen } from "@testing-library/react";
import type { ComponentProps } from "react";
import React from "react";
import { Provider } from "react-redux";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { workflowReducer } from "@/lib/store/workflow/slice";
import type { ExportNodeData } from "@/lib/validations/workflow";

import { makeIssue } from "@/components/workflows/issues/__tests__/issueFixtures";
import ExportNode from "@/components/workflows/nodes/ExportNode";

const { issuesByNode } = vi.hoisted(() => ({ issuesByNode: new Map<string, unknown[]>() }));

vi.mock("react-i18next", () => ({ useTranslation: () => ({ t: (key: string) => key }) }));

vi.mock("@xyflow/react", async () => {
  const { forwardRef } = await import("react");
  return {
    Handle: forwardRef<HTMLDivElement, Record<string, unknown>>(function Handle(props, ref) {
      return (
        <div
          ref={ref}
          data-testid={`handle-${String(props.type)}-${String(props.id)}`}
          data-issue={props["data-issue"] as string | undefined}
        />
      );
    }),
    NodeToolbar: ({ children }: { children: React.ReactNode }) => <>{children}</>,
    Position: { Top: "top", Right: "right", Left: "left", Bottom: "bottom" },
  };
});

vi.mock("@p4b/ui/assets/svg/ToolIcons", () => ({ toolIconMap: { export_dataset: () => null } }));

vi.mock("@/components/workflows/context/WorkflowExecutionContext", () => ({
  useNodeExecutionStatus: () => ({ status: undefined, info: undefined }),
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

type ExportNodeProps = ComponentProps<typeof ExportNode>;

const data: ExportNodeData = {
  type: "export",
  label: "Export",
  datasetName: "",
  addToProject: true,
  overwritePrevious: false,
  status: "idle",
};

const renderNode = () =>
  render(
    <Provider store={configureStore({ reducer: { workflow: workflowReducer } })}>
      <ExportNode
        {...({
          id: "export-1",
          type: "export",
          data,
          selected: false,
          dragging: false,
          zIndex: 0,
          isConnectable: true,
          positionAbsoluteX: 0,
          positionAbsoluteY: 0,
        } as unknown as ExportNodeProps)}
      />
    </Provider>
  );

describe("ExportNode issues", () => {
  beforeEach(() => {
    issuesByNode.clear();
  });

  it("shows its issues although its stored status is idle", () => {
    issuesByNode.set("export-1", [
      makeIssue({ code: "export_name_missing", node_ids: ["export-1"], field: "datasetName" }),
    ]);
    renderNode();
    expect(screen.getByTestId("step-issue-badge")).toBeInTheDocument();
  });

  it("shows a warning, not the amber ring, while nothing is connected to it", async () => {
    issuesByNode.set("export-1", [
      makeIssue({ code: "export_not_connected", level: "warning", node_ids: ["export-1"] }),
    ]);
    renderNode();
    await expect(screen.getByTestId("step-issue-badge")).toHaveAttribute("data-severity", "warning");
    await expect(screen.getByTestId("handle-target-input")).not.toHaveAttribute("data-issue");
  });

  it("shows nothing while the check reports nothing", async () => {
    renderNode();
    expect(screen.queryByTestId("step-issue-badge")).not.toBeInTheDocument();
    await expect(screen.getByTestId("handle-target-input")).not.toHaveAttribute("data-issue");
  });
});
