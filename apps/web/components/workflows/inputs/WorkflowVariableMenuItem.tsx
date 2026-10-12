"use client";

/**
 * One workflow variable in a pick list (the variable menus of tool inputs and
 * the if node). Shows what users know the variable by — its label, falling
 * back to its name — with the technical `{{@name}}` alongside, since that is
 * what an expression or SQL needs typed, and its description on hover.
 */
import VariableIcon from "@mui/icons-material/DataObject";
import { Box, MenuItem, type MenuItemProps, Tooltip, Typography } from "@mui/material";
import React from "react";

import {
  type WorkflowVariable,
  getVariableDescription,
  getVariableDisplayName,
  hasVariableLabel,
} from "@/lib/validations/workflow";

interface WorkflowVariableMenuItemProps
  extends Omit<MenuItemProps, "onClick" | "onSelect" | "children" | "sx"> {
  variable: WorkflowVariable;
  onSelect: (variable: WorkflowVariable) => void;
  /** Lead with the variable icon (the tool-input menus do). */
  showIcon?: boolean;
}

const WorkflowVariableMenuItem = React.forwardRef<HTMLLIElement, WorkflowVariableMenuItemProps>(
  ({ variable, onSelect, showIcon = false, ...menuItemProps }, ref) => {
    const displayName = getVariableDisplayName(variable);
    const description = getVariableDescription(variable);
    const labelled = hasVariableLabel(variable);

    return (
      <Tooltip title={description ?? ""} placement="right" arrow describeChild>
        <MenuItem
          {...menuItemProps}
          ref={ref}
          onClick={() => onSelect(variable)}
          data-variable-name={variable.name}
          sx={{ px: 2, py: 1.5, gap: 1.5 }}>
          {showIcon && <VariableIcon sx={{ fontSize: 16, color: "primary.main" }} />}
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography
              variant="body2"
              noWrap
              fontFamily={labelled ? undefined : "monospace"}
              title={displayName}>
              {displayName}
            </Typography>
            {labelled && (
              <Typography
                variant="caption"
                color="text.secondary"
                fontFamily="monospace"
                noWrap
                component="div">
                {`{{@${variable.name}}}`}
              </Typography>
            )}
          </Box>
          <Typography
            variant="caption"
            sx={{
              px: 0.75,
              py: 0.125,
              borderRadius: 0.5,
              bgcolor: "action.hover",
              textTransform: "capitalize",
              flexShrink: 0,
            }}>
            {variable.type}
          </Typography>
        </MenuItem>
      </Tooltip>
    );
  }
);

WorkflowVariableMenuItem.displayName = "WorkflowVariableMenuItem";

export default WorkflowVariableMenuItem;
