"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useDispatch, useSelector, useStore } from "react-redux";

import { WorkflowIssuesError, updateWorkflow } from "@/lib/api/workflows";
import type { AppDispatch, RootState } from "@/lib/store";
import {
  selectEdges,
  selectIsDirty,
  selectNodes,
  selectSelectedWorkflowId,
  selectVariables,
  selectViewport,
} from "@/lib/store/workflow/selectors";
import { markSaved, syncToWorkflowConfig } from "@/lib/store/workflow/slice";
import type { Workflow, WorkflowNode } from "@/lib/validations/workflow";
import type { WorkflowIssue } from "@/lib/validations/workflowIssues";

/** How long the editor waits after the last change before it saves. */
export const AUTOSAVE_DELAY_MS = 1000;

export type AutosaveStatus = "idle" | "saving" | "failed";

export interface WorkflowAutosave {
  status: AutosaveStatus;
  /** What core listed when it refused the config as damaged; empty otherwise. */
  issues: WorkflowIssue[];
  /** Saves the open workflow now, as the "Not saved" notice's Retry does. */
  retry: () => void;
}

interface UseWorkflowAutosaveArgs {
  projectId?: string;
  /** False for a workflow the editor shows as damaged: it is never saved over. */
  enabled: boolean;
  /** After a save went through (the layout refreshes its workflow list). */
  onSaved: () => void;
}

/**
 * Saves the open workflow a moment after its last change. The config is read
 * from the store when the save starts, so the debounce restarts on every
 * change but a failed save does not retry on its own: it stays "failed" until
 * Retry or the next change. A change made while a save is under way keeps the
 * workflow unsaved, and the debounce that change started saves it.
 */
export function useWorkflowAutosave({
  projectId,
  enabled,
  onSaved,
}: UseWorkflowAutosaveArgs): WorkflowAutosave {
  const dispatch = useDispatch<AppDispatch>();
  const store = useStore<RootState>();
  const workflowId = useSelector(selectSelectedWorkflowId);
  const nodes = useSelector(selectNodes);
  const edges = useSelector(selectEdges);
  const viewport = useSelector(selectViewport);
  const variables = useSelector(selectVariables);
  const isDirty = useSelector(selectIsDirty);
  const [status, setStatus] = useState<AutosaveStatus>("idle");
  const [issues, setIssues] = useState<WorkflowIssue[]>([]);
  const timeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  const save = useCallback(async () => {
    const state = store.getState().workflow;
    const workflow = state.workflows.find((w) => w.id === state.selectedWorkflowId);
    if (!enabled || !projectId || !workflow) return;

    const saved = {
      nodes: state.nodes,
      edges: state.edges,
      viewport: state.viewport,
      variables: state.variables,
    };
    const config: Workflow["config"] = {
      ...workflow.config,
      nodes: saved.nodes.map((node) => ({
        id: node.id,
        type: node.type as WorkflowNode["type"],
        position: node.position,
        data: node.data as WorkflowNode["data"],
      })),
      edges: saved.edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        sourceHandle: edge.sourceHandle || undefined,
        target: edge.target,
        targetHandle: edge.targetHandle || undefined,
      })),
      viewport: saved.viewport,
      variables: saved.variables,
    };

    setStatus("saving");
    try {
      dispatch(syncToWorkflowConfig());
      await updateWorkflow(projectId, workflow.id, { config });
      const now = store.getState().workflow;
      if (
        now.nodes === saved.nodes &&
        now.edges === saved.edges &&
        now.viewport === saved.viewport &&
        now.variables === saved.variables
      ) {
        dispatch(markSaved());
      }
      setStatus("idle");
      setIssues([]);
      onSaved();
    } catch (error) {
      console.error("Failed to save workflow:", error);
      setStatus("failed");
      setIssues(error instanceof WorkflowIssuesError ? error.issues : []);
    }
  }, [enabled, projectId, store, dispatch, onSaved]);

  useEffect(() => {
    if (!isDirty || !enabled) return;
    if (timeout.current) clearTimeout(timeout.current);
    timeout.current = setTimeout(() => {
      void save();
    }, AUTOSAVE_DELAY_MS);
    return () => {
      if (timeout.current) clearTimeout(timeout.current);
    };
  }, [isDirty, enabled, save, nodes, edges, viewport, variables]);

  // Another workflow opened: the last one's failed save no longer applies here.
  useEffect(() => {
    setStatus("idle");
    setIssues([]);
  }, [workflowId]);

  const retry = useCallback(() => {
    if (timeout.current) clearTimeout(timeout.current);
    void save();
  }, [save]);

  return { status, issues, retry };
}
