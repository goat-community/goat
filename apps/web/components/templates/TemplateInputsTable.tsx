"use client";

import { Box, Chip, MenuItem, Select, Switch, Typography, alpha, useTheme } from "@mui/material";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { INPUT_CHOICE_LABEL_KEY, type TemplateInputChoice, canCopyInput } from "@/lib/utils/templates";
import type { TemplateInput } from "@/lib/validations/template";

/** A declared input's state, as edited in the save dialog before it is
 * written back as `TemplateInput.mode` (+ `copy_content` for a copy). */
export type TemplateInputMode = TemplateInputChoice;

/** The choices for a dataset the template keeps, in the order offered. */
const DATASET_CHOICES: TemplateInputMode[] = ["ship", "copy", "copy_empty"];

interface TemplateInputsTableProps {
  inputs: TemplateInput[];
  modeFor: (key: string) => TemplateInputMode;
  onModeChange: (key: string, mode: TemplateInputMode) => void;
  /** False for a project payload: there is no ask option for one in v1
   * (the frozen copy already holds a real project layer for each dataset),
   * so the row offers only ship or copy, with no ship/ask switch. */
  allowAsk: boolean;
  /** A frozen snapshot's inputs: shown, not switchable. */
  disabled?: boolean;
}

/** T5/T8's inputs table: one row per layer reference the save preview
 * detected, each showing its type/geometry, a "Sample data" badge for a
 * catalog-origin dataset, and — for a workflow payload — the ship/ask
 * switch defaulted from the preview's `detected_inputs`. A dataset the
 * template keeps (switch on, and every project dataset) also says how it
 * reaches a user: linked read-only, or copied for each user with its rows
 * or empty (a raster cannot be copied, so it only ships). Rendered only
 * for workflow/project payloads — a layout payload carries no inputs at
 * all (T5). */
const TemplateInputsTable = ({
  inputs,
  modeFor,
  onModeChange,
  allowAsk,
  disabled,
}: TemplateInputsTableProps) => {
  const { t } = useTranslation("common");
  const theme = useTheme();

  const typeLabel = (input: TemplateInput): string => {
    if (!input.layer_type) return "";
    const kind = t(input.layer_type);
    return input.geometry_type ? `${kind} · ${t(input.geometry_type)}` : kind;
  };

  const datasetChoice = (input: TemplateInput, mode: TemplateInputMode) => {
    if (disabled || !canCopyInput(input)) {
      return (
        <Typography sx={{ fontSize: 11.5, color: "text.secondary", whiteSpace: "nowrap" }}>
          {mode === "ship" && !allowAsk ? t("ships_with_template") : t(INPUT_CHOICE_LABEL_KEY[mode])}
        </Typography>
      );
    }
    return (
      <Select
        size="small"
        variant="standard"
        disableUnderline
        value={mode}
        onChange={(event) => onModeChange(input.key, event.target.value as TemplateInputMode)}
        inputProps={{ "aria-label": `${input.label} — ${t("template_dataset_handling")}` }}
        sx={{ fontSize: 11.5, color: "text.secondary", maxWidth: 200 }}>
        {DATASET_CHOICES.map((choice) => (
          <MenuItem key={choice} value={choice} sx={{ fontSize: 12.5 }}>
            {t(INPUT_CHOICE_LABEL_KEY[choice])}
          </MenuItem>
        ))}
      </Select>
    );
  };

  return (
    <Box sx={{ border: `1px solid ${theme.palette.divider}`, borderRadius: "10px", overflow: "hidden" }}>
      {inputs.map((input, index) => {
        const mode = modeFor(input.key);
        return (
          <Box
            key={input.key}
            data-testid={`template-input-row-${input.key}`}
            sx={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              padding: "7px 12px",
              borderTop: index > 0 ? `1px solid ${theme.palette.divider}` : undefined,
            }}>
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography component="div" noWrap sx={{ fontSize: 13, fontWeight: 600 }}>
                {input.label}
              </Typography>
              <Typography component="div" sx={{ fontSize: 11.5, color: "text.secondary" }}>
                {typeLabel(input)}
              </Typography>
            </Box>
            {(input.from_catalog || input.public_read) && (
              <Chip
                size="small"
                icon={<Icon iconName={ICON_NAME.DATABASE} style={{ fontSize: 12 }} />}
                label={t(input.from_catalog ? "catalog" : "public")}
                sx={{ height: 22, fontSize: 11, backgroundColor: alpha(theme.palette.info.main, 0.12) }}
              />
            )}
            <Box sx={{ display: "flex", alignItems: "center", gap: "6px", flexShrink: 0 }}>
              {allowAsk && (
                <Switch
                  size="small"
                  checked={mode !== "ask"}
                  disabled={disabled}
                  onChange={(_event, checked) => onModeChange(input.key, checked ? "ship" : "ask")}
                  inputProps={{ "aria-label": `${input.label} — ${t("ship_dataset")}` }}
                />
              )}
              {mode === "ask" ? (
                <Typography sx={{ fontSize: 11.5, color: "text.secondary", whiteSpace: "nowrap" }}>
                  {t("ask_on_use")}
                </Typography>
              ) : (
                datasetChoice(input, mode)
              )}
            </Box>
          </Box>
        );
      })}
    </Box>
  );
};

export default TemplateInputsTable;
