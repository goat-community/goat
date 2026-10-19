"use client";

import { Alert, Button, Stack, Typography, useTheme } from "@mui/material";
import { useState } from "react";
import { useTranslation } from "react-i18next";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { useLayerWriteAccess } from "@/lib/api/layers";
import type { ContentItem } from "@/lib/validations/content";
import type { ExportNodeData } from "@/lib/validations/workflow";

import DatasetPickerDialog from "@/components/addLayer/DatasetPickerDialog";

/** A dataset rows can go into: a feature layer or a table. Whether the user
 * may edit it is not judged from the list's role but by the write-access
 * check (the rule the run uses), which warns right after the pick. */
export const canAppendTo = (item: ContentItem): boolean =>
  item.type === "layer" && ((item as { layer_type?: string }).layer_type ?? "feature") !== "raster";

interface ExportExistingTargetSettingsProps {
  data: ExportNodeData;
  onChange: (changes: Partial<ExportNodeData>) => void;
}

/**
 * "Existing dataset" in the "Save as dataset" panel, laid out like the
 * "Dataset name *" field it replaces: which dataset the rows are added to.
 * The columns must match the dataset's; "Add to project" is the panel's own.
 */
export default function ExportExistingTargetSettings({ data, onChange }: ExportExistingTargetSettingsProps) {
  const { t } = useTranslation("common");
  const theme = useTheme();
  const [pickerOpen, setPickerOpen] = useState(false);
  const { canWrite } = useLayerWriteAccess(data.targetLayerId);

  return (
    <Stack spacing={1} sx={{ mb: 2 }}>
      <Typography variant="body2" color="text.secondary">
        {t("append_target_layer")} *
      </Typography>
      {data.targetLayerId && (
        <Stack direction="row" alignItems="center" spacing={1}>
          <Icon
            iconName={ICON_NAME.LAYERS}
            style={{ fontSize: 14 }}
            htmlColor={theme.palette.text.secondary}
          />
          <Typography
            variant="body2"
            fontWeight="bold"
            sx={{ flex: 1, minWidth: 0, overflowWrap: "anywhere" }}>
            {data.targetLayerName}
          </Typography>
        </Stack>
      )}
      <Button
        variant="outlined"
        size="small"
        fullWidth
        startIcon={
          <Icon
            iconName={data.targetLayerId ? ICON_NAME.LAYERS : ICON_NAME.PLUS}
            style={{ fontSize: data.targetLayerId ? 16 : 15 }}
          />
        }
        onClick={() => setPickerOpen(true)}
        sx={{ borderRadius: 4, textTransform: "none", fontWeight: "bold" }}>
        {data.targetLayerId ? t("change_dataset") : t("append_choose_target")}
      </Button>

      {data.targetLayerId && canWrite === false && (
        <Alert severity="warning" sx={{ py: 0 }}>
          {t("append_no_edit_rights_detail")}
        </Alert>
      )}

      <DatasetPickerDialog
        open={pickerOpen}
        onClose={() => setPickerOpen(false)}
        onPick={(item) => onChange({ targetLayerId: item.id, targetLayerName: item.name })}
        canPick={canAppendTo}
        cannotPickLabel={t("append_target_wrong_type")}
      />
    </Stack>
  );
}
