"use client";

import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CancelIcon from "@mui/icons-material/Cancel";
import DeleteIcon from "@mui/icons-material/Delete";
import DuplicateIcon from "@mui/icons-material/ContentCopy";
import { Box, Stack, Tooltip, Typography } from "@mui/material";
import { styled } from "@mui/material/styles";
import { type NodeProps, NodeToolbar, Position } from "@xyflow/react";
import React, { memo, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { useDispatch, useSelector } from "react-redux";
import { v4 as uuidv4 } from "uuid";

import type { AppDispatch } from "@/lib/store";
import { selectNodes } from "@/lib/store/workflow/selectors";
import { addNode, removeNodes } from "@/lib/store/workflow/slice";
import type { ExportNodeData } from "@/lib/validations/workflow";

import { type TOOL_ICON_NAME, toolIconMap } from "@p4b/ui/assets/svg/ToolIcons";

import StepIssueBadge from "@/components/workflows/issues/StepIssueBadge";

import { useNodeExecutionStatus } from "../context/WorkflowExecutionContext";
import {
  AnimatedBorderWrapper,
  IconStatusBadge,
  NodeContainer,
  NodeHeader,
  NodeIconWrapper,
  NodeParamsSection,
  StyledHandle,
  ToolbarButton,
  ToolbarContainer,
} from "./shared";

const ParamRow = styled(Box)({
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-start",
  gap: 16,
});

interface ExportNodeProps extends NodeProps {
  data: ExportNodeData;
}

const ExportNode: React.FC<ExportNodeProps> = ({ id, data, selected }) => {
  const { t } = useTranslation("common");
  const dispatch = useDispatch<AppDispatch>();
  const nodes = useSelector(selectNodes);

  const { status: nodeStatus_ } = useNodeExecutionStatus(id);
  const nodeStatus = nodeStatus_ || data.status;

  // Handle duplicate node
  const handleDuplicate = useCallback(
    (event: React.MouseEvent) => {
      event.stopPropagation();
      const node = nodes.find((n) => n.id === id);
      if (!node) return;

      dispatch(
        addNode({
          ...node,
          id: `export-${uuidv4()}`,
          position: {
            x: node.position.x + 50,
            y: node.position.y + 50,
          },
          data: {
            ...node.data,
            status: "idle",
            exportedLayerId: undefined,
            jobId: undefined,
            error: undefined,
          },
        })
      );
    },
    [id, nodes, dispatch]
  );

  // Handle delete node
  const handleDelete = useCallback(
    (event: React.MouseEvent) => {
      event.stopPropagation();
      dispatch(removeNodes([id]));
    },
    [id, dispatch]
  );

  return (
    <>

      <NodeToolbar position={Position.Top} align="end">
        <ToolbarContainer>
          <Tooltip title={t("duplicate")} placement="top" arrow>
            <ToolbarButton onClick={handleDuplicate}>
              <DuplicateIcon fontSize="small" />
            </ToolbarButton>
          </Tooltip>
          <Tooltip title={t("delete")} placement="top" arrow>
            <ToolbarButton onClick={handleDelete}>
              <DeleteIcon fontSize="small" color="error" />
            </ToolbarButton>
          </Tooltip>
        </ToolbarContainer>
      </NodeToolbar>

      <NodeContainer selected={selected}>
        {/* The step's issues; stays after a run, next to the run status */}
        <StepIssueBadge nodeId={id} />

        {/* Input handle - left (receives tool output) */}
        <StyledHandle
          type="target"
          position={Position.Left}
          id="input"
          selected={selected}
        />

        <NodeHeader>
          <AnimatedBorderWrapper isRunning={nodeStatus === "running"}>
            <NodeIconWrapper status={nodeStatus}>
              {(() => {
                const ExportIcon = toolIconMap["export_dataset" as TOOL_ICON_NAME];
                return <ExportIcon sx={{ fontSize: 32 }} />;
              })()}
              {/* Checkmark badge — only on completed, same as tool nodes */}
              {nodeStatus === "completed" && (
                <IconStatusBadge status="completed">
                  <CheckCircleIcon sx={{ fontSize: 12 }} />
                </IconStatusBadge>
              )}
              {/* Cross badge on icon */}
              {nodeStatus === "failed" && (
                <IconStatusBadge status="failed">
                  <CancelIcon sx={{ fontSize: 12 }} />
                </IconStatusBadge>
              )}
            </NodeIconWrapper>
          </AnimatedBorderWrapper>
          <Typography variant="caption" fontWeight={700} sx={{ flex: 1, wordBreak: "break-word" }}>
            {t("export_dataset")}
          </Typography>
        </NodeHeader>

        {/* Parameters section — same layout as ToolNode's ParamRow */}
        <NodeParamsSection>
          <Stack spacing={0.25}>
          {data.datasetName && (
            <ParamRow>
              <Typography variant="caption" color="text.secondary" fontWeight="bold" sx={{ fontSize: 11 }}>
                {t("dataset_name")}:
              </Typography>
              <Typography variant="caption" fontWeight="medium" sx={{ fontSize: 11 }}>
                {data.datasetName}
              </Typography>
            </ParamRow>
          )}
          {data.addToProject && (
            <ParamRow>
              <Typography variant="caption" color="text.secondary" fontWeight="bold" sx={{ fontSize: 11 }}>
                {t("add_to_project")}:
              </Typography>
              <Typography variant="caption" fontWeight="medium" sx={{ fontSize: 11 }}>
                {t("yes")}
              </Typography>
            </ParamRow>
          )}
          {data.overwritePrevious && (
            <ParamRow>
              <Typography variant="caption" color="text.secondary" fontWeight="bold" sx={{ fontSize: 11 }}>
                {t("overwrite")}:
              </Typography>
              <Typography variant="caption" fontWeight="medium" sx={{ fontSize: 11 }}>
                {t("yes")}
              </Typography>
            </ParamRow>
          )}
          </Stack>
        </NodeParamsSection>

        {/* Error */}
        {nodeStatus === "failed" && data.error && (
          <Typography
            variant="caption"
            color="error.main"
            sx={{
              display: "block",
              mt: 0.5,
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
            title={data.error}>
            {data.error}
          </Typography>
        )}
      </NodeContainer>
    </>
  );
};

export default memo(ExportNode);
