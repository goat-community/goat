import { Stack } from "@mui/material";
import { useMemo, useState } from "react";

import { useTranslation } from "@/i18n/client";

import { type FeatureLayerProperties, type LayerFieldType, TextLabel } from "@/lib/validations/layer";
import type { ProjectLayer } from "@/lib/validations/project";

import useLayerFields from "@/hooks/map/CommonHooks";

import FormLabelHelper from "@/components/common/FormLabelHelper";
import LayerFieldSelector from "@/components/map/common/LayerFieldSelector";
import SectionHeader from "@/components/map/panels/common/SectionHeader";
import SectionOptions from "@/components/map/panels/common/SectionOptions";
import SliderInput from "@/components/map/panels/common/SliderInput";

const LabelOptions = ({
  layer,
  onStyleChange,
}: {
  layer: ProjectLayer;
  onStyleChange?: (newStyle: FeatureLayerProperties) => void;
}) => {
  const { t } = useTranslation("common");
  const { layerFields } = useLayerFields(layer?.layer_id || "");

  // For now we are only supporting one text label, however, in the future we might support multiple text labels
  const textLabelOptions = useMemo(() => {
    const textLabelProperties = TextLabel.safeParse(layer?.properties?.text_label);
    if (textLabelProperties.success) {
      if (Array.isArray(textLabelProperties.data) && textLabelProperties.data.length > 0) {
        return textLabelProperties.data[0];
      }
    }
    return undefined;
  }, [layer?.properties?.text_label]);

  const [selectedField, setSelectedField] = useState<LayerFieldType | undefined>(
    layerFields.find((field) => field.name === textLabelOptions?.field)
  );

  const [textLabelSize, setTextLabelSize] = useState<number | undefined>(textLabelOptions?.size);

  return (
    <>
      <SectionHeader active alwaysActive label={t("label_by")} disableAdvanceOptions />
      <SectionOptions
        active={true}
        baseOptions={
          <LayerFieldSelector
            fields={layerFields}
            selectedField={selectedField}
            setSelectedField={(field) => {
              setSelectedField(field);
              const newStyle = JSON.parse(JSON.stringify(layer.properties)) || {};
              if (!field) {
                newStyle.text_label = undefined;
              } else {
                const textLabels = TextLabel.safeParse({
                  ...textLabelOptions,
                  field: field.name,
                });
                if (textLabels.success) {
                  newStyle.text_label = [textLabels.data];
                }
              }
              onStyleChange?.(newStyle);
            }}
            label={t("label_by")}
          />
        }
        advancedOptions={<></>}
        collapsed={false}
      />

      <SectionHeader
        active={!!selectedField}
        alwaysActive
        label={t("label_settings")}
        disableAdvanceOptions
      />
      <SectionOptions
        active={!!selectedField}
        baseOptions={
          <Stack>
            <FormLabelHelper label={t("size")} color="inherit" />
            <SliderInput
              value={textLabelSize || textLabelOptions?.size || 0}
              onChange={(value) => {
                setTextLabelSize(value as number);
              }}
              onChangeCommitted={(value) => {
                const newStyle = JSON.parse(JSON.stringify(layer.properties)) || {};
                newStyle.text_label = [
                  {
                    ...textLabelOptions,
                    size: value,
                  },
                ];
                onStyleChange?.(newStyle);
              }}
              isRange={false}
              rootSx={{
                pl: 3,
                pr: 2,
              }}
            />
          </Stack>
        }
        collapsed={false}
      />
    </>
  );
};

export default LabelOptions;
