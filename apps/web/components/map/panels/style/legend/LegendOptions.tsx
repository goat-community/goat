import { Checkbox, FormControlLabel, Stack, TextField, Typography } from "@mui/material";
import { useState } from "react";

import { useTranslation } from "@/i18n/client";

import type { FeatureLayerProperties } from "@/lib/validations/layer";
import type { ProjectLayer } from "@/lib/validations/project";

export const LegendOptions = ({
  layer,
  onStyleChange,
}: {
  layer: ProjectLayer;
  onStyleChange?: (newStyle: FeatureLayerProperties) => void;
}) => {
  const { t } = useTranslation("common");

  const [legendCaption, setLegendCaption] = useState<string>(layer.properties?.legend?.caption || "");

  return (
    <>
      <Stack spacing={4} sx={{ mb: 4 }}>
        <FormControlLabel
          control={
            <Checkbox
              size="small"
              color="primary"
              checked={!!layer.properties?.legend?.show}
              onChange={(e) => {
                const showInLegend = e.target.checked;
                const newStyle = JSON.parse(JSON.stringify(layer.properties)) || {};
                newStyle.legend = {
                  ...newStyle.legend,
                  show: showInLegend,
                };
                onStyleChange?.(newStyle as FeatureLayerProperties);
              }}
            />
          }
          label={<Typography variant="body2">{t("show")}</Typography>}
        />
        {layer.properties?.legend?.show && (
          <TextField
            value={legendCaption}
            inputProps={{ style: { fontSize: 13 } }}
            placeholder={t("caption")}
            onChange={(e) => {
              setLegendCaption(e.target.value);
            }}
            onBlur={() => {
              const newStyle = JSON.parse(JSON.stringify(layer.properties)) || {};
              newStyle.legend = {
                ...newStyle.legend,
                caption: legendCaption,
              };
              onStyleChange?.(newStyle as FeatureLayerProperties);
            }}
            fullWidth
            label={t("caption")}
            variant="outlined"
          />
        )}
      </Stack>
    </>
  );
};
