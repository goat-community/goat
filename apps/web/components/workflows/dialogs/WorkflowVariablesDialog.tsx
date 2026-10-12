"use client";

import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/DeleteOutline";
import {
  Box,
  Button,
  Divider,
  IconButton,
  MenuItem,
  Select,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import React, { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useDispatch, useSelector } from "react-redux";
import { v4 as uuidv4 } from "uuid";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import type { AppDispatch } from "@/lib/store";
import { selectVariables } from "@/lib/store/workflow/selectors";
import { setVariables } from "@/lib/store/workflow/slice";
import {
  WORKFLOW_VARIABLE_DESCRIPTION_MAX,
  WORKFLOW_VARIABLE_LABEL_MAX,
  type WorkflowVariable,
} from "@/lib/validations/workflow";

import AppDialog, { AppDialogFooter } from "@/components/common/AppDialog";
import VariableDescriptionButton from "@/components/workflows/dialogs/VariableDescriptionButton";

const VARIABLE_NAME_REGEX = /^[a-zA-Z_][a-zA-Z0-9_]*$/;

type VariableErrors = Partial<Record<"name" | "label" | "description", string>>;

// Column widths, shared by the header and every row. Name and label share
// what is left after the fixed columns; the name gets a little more, so a
// 32-character identifier stays fully visible at the dialog's full width.
const COLUMN_SX = {
  name: { flex: 1.1, minWidth: 0 },
  label: { flex: 1, minWidth: 0 },
  type: { width: 100, flexShrink: 0 },
  default: { width: 100, flexShrink: 0 },
  // The description and delete buttons.
  actions: { width: 76, flexShrink: 0 },
} as const;

/**
 * The variable as it is saved: order recomputed, a number default coerced,
 * label and description trimmed, and either dropped when left empty, so a
 * variable nobody labelled keeps the shape it always had. Only the schema's
 * keys are kept.
 */
export function normalizeVariable(variable: WorkflowVariable, index: number): WorkflowVariable {
  const { id, name, type, defaultValue } = variable;
  const label = variable.label?.trim();
  const description = variable.description?.trim();
  return {
    id,
    name,
    ...(label && { label }),
    ...(description && { description }),
    type,
    ...(defaultValue !== undefined && {
      defaultValue: type === "number" && defaultValue !== "" ? Number(defaultValue) : defaultValue,
    }),
    order: index,
  };
}

interface WorkflowVariablesDialogProps {
  open: boolean;
  onClose: () => void;
}

const WorkflowVariablesDialog: React.FC<WorkflowVariablesDialogProps> = ({ open, onClose }) => {
  const { t } = useTranslation("common");
  const dispatch = useDispatch<AppDispatch>();
  const reduxVariables = useSelector(selectVariables);

  // Local editable copy
  const [localVars, setLocalVars] = useState<WorkflowVariable[]>([]);
  const [errors, setErrors] = useState<Record<string, VariableErrors>>({});

  // Sync from Redux when dialog opens
  useEffect(() => {
    if (open) {
      setLocalVars(reduxVariables.map((v) => ({ ...v })));
      setErrors({});
    }
  }, [open, reduxVariables]);

  const validate = useCallback(
    (vars: WorkflowVariable[]): Record<string, VariableErrors> => {
      const errs: Record<string, VariableErrors> = {};
      const names = new Set<string>();
      for (const v of vars) {
        const err: VariableErrors = {};
        if (!v.name.trim()) {
          err.name = t("workflow_variable_name_required");
        } else if (!VARIABLE_NAME_REGEX.test(v.name)) {
          err.name = t("workflow_variable_name_invalid");
        } else if (names.has(v.name)) {
          err.name = t("workflow_variable_name_duplicate");
        } else if (
          v.type === "number" &&
          v.defaultValue !== undefined &&
          v.defaultValue !== "" &&
          isNaN(Number(v.defaultValue))
        ) {
          err.name = t("workflow_variable_invalid_number");
        }
        if ((v.label?.trim().length ?? 0) > WORKFLOW_VARIABLE_LABEL_MAX) {
          err.label = t("workflow_variable_label_too_long", { max: WORKFLOW_VARIABLE_LABEL_MAX });
        }
        if ((v.description?.trim().length ?? 0) > WORKFLOW_VARIABLE_DESCRIPTION_MAX) {
          err.description = t("workflow_variable_description_too_long", {
            max: WORKFLOW_VARIABLE_DESCRIPTION_MAX,
          });
        }
        if (Object.keys(err).length > 0) errs[v.id] = err;
        names.add(v.name);
      }
      return errs;
    },
    [t]
  );

  const handleAdd = useCallback(() => {
    const newVar: WorkflowVariable = {
      id: `var-${uuidv4()}`,
      name: "",
      type: "number",
      defaultValue: "",
      order: localVars.length,
    };
    setLocalVars((prev) => [...prev, newVar]);
  }, [localVars.length]);

  const handleUpdate = useCallback((id: string, changes: Partial<WorkflowVariable>) => {
    setLocalVars((prev) => prev.map((v) => (v.id === id ? { ...v, ...changes } : v)));
    setErrors((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
  }, []);

  const handleRemove = useCallback((id: string) => {
    setLocalVars((prev) => prev.filter((v) => v.id !== id));
    setErrors((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
  }, []);

  const handleDone = useCallback(() => {
    const errs = validate(localVars);
    if (Object.keys(errs).length > 0) {
      setErrors(errs);
      return;
    }
    dispatch(setVariables(localVars.map(normalizeVariable)));
    onClose();
  }, [localVars, validate, dispatch, onClose]);

  return (
    <AppDialog
      open={open}
      onClose={onClose}
      icon={ICON_NAME.VARIABLE}
      title={t("workflow_variables")}
      maxWidth={900}
      // The rows between the variables run to the frame's edges; only the
      // vertical padding a dialog body has is kept.
      bleed
      bodySx={{ py: 5 }}
      footer={<AppDialogFooter onCancel={onClose} primaryLabel={t("done")} onPrimary={handleDone} />}>
      {localVars.length === 0 ? (
        <Stack alignItems="center" spacing={1} sx={{ py: 4 }}>
          <Icon iconName={ICON_NAME.VARIABLE} fontSize="small" htmlColor="text.secondary" />
          <Typography variant="body2" color="text.secondary" textAlign="center">
            {t("workflow_variable_none_defined")}
          </Typography>
        </Stack>
      ) : (
        <Stack spacing={0} sx={{ mt: 1 }}>
          {/* Header row */}
          <Box data-testid="workflow-variable-header" sx={{ display: "flex", gap: 1, px: 3, mb: 1 }}>
            {(
              [
                ["name", "workflow_variable_name"],
                ["label", "workflow_variable_label"],
                ["type", "workflow_variable_type"],
                ["default", "workflow_variable_default"],
              ] as const
            ).map(([column, key]) => (
              <Typography
                key={column}
                variant="caption"
                color="text.secondary"
                fontWeight="bold"
                noWrap
                sx={COLUMN_SX[column]}>
                {t(key)}
              </Typography>
            ))}
            <Box sx={COLUMN_SX.actions} />
          </Box>

          <Divider />

          {/* Variable rows */}
          {localVars.map((variable, index) => (
            <React.Fragment key={variable.id}>
              <Box
                data-testid="workflow-variable-row"
                sx={{ display: "flex", gap: 1, alignItems: "flex-start", px: 3, py: 1.5 }}>
                <TextField
                  size="small"
                  placeholder={t("workflow_variable_name_placeholder")}
                  value={variable.name}
                  onChange={(e) => handleUpdate(variable.id, { name: e.target.value.replace(/\s/g, "_") })}
                  error={!!errors[variable.id]?.name}
                  helperText={errors[variable.id]?.name}
                  sx={COLUMN_SX.name}
                  inputProps={{
                    "aria-label": t("workflow_variable_name"),
                    title: variable.name || undefined,
                    style: { fontSize: "0.8125rem", fontFamily: "monospace" },
                  }}
                />
                <TextField
                  size="small"
                  placeholder={t("workflow_variable_label_placeholder")}
                  value={variable.label ?? ""}
                  onChange={(e) => handleUpdate(variable.id, { label: e.target.value })}
                  error={!!errors[variable.id]?.label}
                  helperText={errors[variable.id]?.label}
                  sx={COLUMN_SX.label}
                  inputProps={{
                    "aria-label": t("workflow_variable_label"),
                    title: variable.label || undefined,
                    maxLength: WORKFLOW_VARIABLE_LABEL_MAX,
                    style: { fontSize: "0.8125rem" },
                  }}
                />
                <Select
                  size="small"
                  value={variable.type}
                  onChange={(e) =>
                    handleUpdate(variable.id, {
                      type: e.target.value as "string" | "number",
                      defaultValue: "",
                    })
                  }
                  inputProps={{ "aria-label": t("workflow_variable_type") }}
                  sx={{ ...COLUMN_SX.type, fontSize: "0.8125rem" }}>
                  <MenuItem value="string">{t("workflow_variable_type_string")}</MenuItem>
                  <MenuItem value="number">{t("workflow_variable_type_number")}</MenuItem>
                </Select>
                <TextField
                  size="small"
                  placeholder={variable.type === "number" ? "0" : t("workflow_variable_value_placeholder")}
                  type={variable.type === "number" ? "number" : "text"}
                  value={variable.defaultValue ?? ""}
                  onChange={(e) => handleUpdate(variable.id, { defaultValue: e.target.value })}
                  sx={COLUMN_SX.default}
                  inputProps={{
                    "aria-label": t("workflow_variable_default"),
                    style: { fontSize: "0.8125rem" },
                  }}
                />
                <Box sx={{ ...COLUMN_SX.actions, display: "flex", gap: 0.5 }}>
                  <VariableDescriptionButton
                    value={variable.description}
                    onChange={(description) => handleUpdate(variable.id, { description })}
                    error={errors[variable.id]?.description}
                  />
                  <Tooltip title={t("delete")}>
                    <IconButton
                      size="small"
                      onClick={() => handleRemove(variable.id)}
                      color="error"
                      sx={{ mt: 0.75 }}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              {index < localVars.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </Stack>
      )}

      {/* Add button */}
      {localVars.length > 0 && <Divider />}
      <Stack alignItems="center" sx={{ mt: 2 }}>
        <Button
          startIcon={<AddIcon />}
          onClick={handleAdd}
          size="small"
          variant="text"
          sx={{ textTransform: "none" }}>
          {t("workflow_variable_add")}
        </Button>
      </Stack>
    </AppDialog>
  );
};

export default WorkflowVariablesDialog;
