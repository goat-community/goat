import { useDraggable } from "@dnd-kit/core";
import { Box, Typography, styled } from "@mui/material";
import React from "react";

import { useTranslation } from "@/i18n/client";

import type { WidgetTypes } from "@/lib/validations/widget";

import { iconMap } from "@/components/builder/widgets/common/WidgetIconMap";

export interface DraggableItemProps {
  widgetType: WidgetTypes;
  isDragging?: boolean;
}

const SquareItem = styled(Box)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  height: 64,
  width: 64,
  borderRadius: 8,
  border: `1px solid ${theme.palette.divider}`,
  "&:hover": {
    borderColor: theme.palette.primary.main,
    backgroundColor: theme.palette.action.hover,
  },
}));

const CardTile = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  justifyContent: "flex-start",
  height: 64,
  width: 160,
  borderRadius: 8,
  border: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[4], // Add elevation (shadow)
  padding: theme.spacing(3), // Add some padding
}));

const Label = styled(Typography)(({ theme }) => ({
  marginTop: theme.spacing(0.5),
  textAlign: "center",
  maxWidth: 64,
  wordWrap: "break-word",
  overflowWrap: "break-word",
  whiteSpace: "normal",
}));

const CardTileLabel = styled(Typography)(({ theme }) => ({
  marginLeft: theme.spacing(1.5), // Add spacing between icon and label
  textAlign: "left",
  whiteSpace: "nowrap", // Prevent label from wrapping
  overflow: "hidden",
  textOverflow: "ellipsis", // Add ellipsis for long labels
}));

export function Draggable(props) {
  const Element = props.element || "div";
  const { attributes, listeners, setNodeRef } = useDraggable({
    id: props.id,
  });

  return (
    <Element ref={setNodeRef} {...listeners} {...attributes}>
      {props.children}
    </Element>
  );
}

export const DraggableItem = ({ widgetType, isDragging = false }: DraggableItemProps) => {
  const { t } = useTranslation("common");
  return (
    <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", cursor: "grab" }}>
      {isDragging ? (
        <CardTile>
          {iconMap[widgetType] && React.createElement(iconMap[widgetType], { fontSize: "medium" })}
          <CardTileLabel variant="body2">{t(widgetType)}</CardTileLabel>
        </CardTile>
      ) : (
        <>
          <SquareItem>
            {iconMap[widgetType] && React.createElement(iconMap[widgetType], { fontSize: "medium" })}
          </SquareItem>
          <Label variant="caption">{t(widgetType)}</Label>
        </>
      )}
    </Box>
  );
};
