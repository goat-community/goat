import { Checkbox, FormControlLabel, Stack, Typography } from "@mui/material";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import type { FeatureLayerProperties, Layer, LayerFieldType } from "@/lib/validations/layer";
import type { ProjectLayer } from "@/lib/validations/project";

import FormLabelHelper from "@/components/common/FormLabelHelper";
import LayerFieldSelector from "@/components/map/common/LayerFieldSelector";
import SectionOptions from "@/components/map/panels/common/SectionOptions";
import SliderInput from "@/components/map/panels/common/SliderInput";
import SizeScaleSelector from "@/components/map/panels/style/classification/SizeScaleSelector";
import MarkerSettings from "@/components/map/panels/style/marker/MarkerSettings";

/** The size slider's upper bound (`SliderInput`'s default `max`). */
const SIZE_SLIDER_MAX = 100;

const Settings = ({
  type,
  layerStyle,
  active,
  collapsed,
  onStyleChange,
  selectedField,
  layerFields,
  activeLayer,
}: {
  type: "stroke_width" | "radius" | "marker_size";
  layerStyle?: FeatureLayerProperties;
  active: boolean;
  collapsed?: boolean;
  onStyleChange?: (newStyle: FeatureLayerProperties) => void | Promise<void>;
  selectedField?: LayerFieldType;
  layerFields: LayerFieldType[];
  activeLayer?: ProjectLayer | Layer;
}) => {
  const { t } = useTranslation("common");

  const initialValue = layerStyle?.[`${type}_field`]
    ? layerStyle?.[`${type}_range`] || [0, 50]
    : layerStyle?.[`${type}`] || 0;

  const [value, setValue] = useState(initialValue);

  // Resets value when activeLayer.id or layerStyle changes
  useEffect(() => {
    const newValue = layerStyle?.[`${type}_field`]
      ? layerStyle?.[`${type}_range`] || [0, 50]
      : layerStyle?.[`${type}`] || 0;
    setValue(newValue);
  }, [activeLayer?.id, layerStyle, type]);

  const isRange = useMemo(() => (layerStyle?.[`${type}_field`] ? true : false), [layerStyle, type]);

  const _onStyleChange = useCallback(
    (value: unknown, propType: string) => {
      const newStyle = JSON.parse(JSON.stringify(layerStyle)) || {};
      // Only apply range mode when the prop being changed is the primary size prop
      if (isRange && propType === type) {
        newStyle[`${propType}_range`] = value;
      } else {
        newStyle[`${propType}`] = value;
      }
      onStyleChange && onStyleChange(newStyle);
    },
    [isRange, layerStyle, onStyleChange, type]
  );

  return (
    <>
      <SectionOptions
        active={!!active}
        collapsed={collapsed}
        baseOptions={
          <Stack direction="column" spacing={4}>
            <Stack>
              <FormLabelHelper label={t("size")} color="inherit" />
              <SliderInput
                value={value}
                onChange={setValue}
                onChangeCommitted={(value) => _onStyleChange(value, type)}
                isRange={isRange}
                rootSx={{
                  pl: 3,
                  pr: 2,
                }}
              />
            </Stack>
            {type === "marker_size" && (
              <Stack>
                <Stack sx={{ mb: 4 }}>
                  {activeLayer && (
                    <MarkerSettings
                      layer={activeLayer}
                      onStyleChange={async (newStyle: FeatureLayerProperties) => {
                        onStyleChange && onStyleChange(newStyle);
                      }}
                    />
                  )}
                </Stack>
                <FormControlLabel
                  control={
                    <Checkbox
                      size="small"
                      color="primary"
                      checked={layerStyle?.["marker_allow_overlap"] || false}
                      onChange={(e) => {
                        const allowOverlap = e.target.checked;
                        _onStyleChange(allowOverlap, "marker_allow_overlap");
                      }}
                    />
                  }
                  label={<Typography variant="body2">{t("allow_overlap")}</Typography>}
                />
              </Stack>
            )}
          </Stack>
        }
        advancedOptions={
          <>
            <LayerFieldSelector
              fields={layerFields}
              selectedField={selectedField}
              setSelectedField={(field) => {
                const newStyle = JSON.parse(JSON.stringify(layerStyle)) || {};
                // The size range defaults to start at 0, which renders the smallest
                // features invisibly. On first use start it at the fixed size instead,
                // within what the size slider can show.
                const size = newStyle[type];
                const range = newStyle[`${type}_range`] ?? [0, 50];
                if (field && !newStyle[`${type}_field`] && range[0] === 0 && typeof size === "number" && size > 0) {
                  newStyle[`${type}_range`] = [size, Math.min(SIZE_SLIDER_MAX, Math.max(range[1], size * 2))];
                }
                newStyle[`${type}_field`] = field;
                if (onStyleChange) {
                  onStyleChange(newStyle);
                }
              }}
              label={t(`${type}_based_on`)}
              tooltip={t(`${type}_based_on_desc`)}
            />
            {isRange && layerStyle && (
              <SizeScaleSelector
                type={type}
                layerStyle={layerStyle}
                classBreaksValues={layerStyle[`${type}_scale_breaks`] as Parameters<typeof SizeScaleSelector>[0]["classBreaksValues"]}
                label={t("size_scale")}
                onStyleChange={(newStyle) => onStyleChange && onStyleChange(newStyle)}
              />
            )}
          </>
        }
      />
    </>
  );
};

export default Settings;
