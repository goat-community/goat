import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import { Checkbox, FormControlLabel, Stack, Tooltip, Typography } from "@mui/material";
import { useParams } from "next/navigation";
import { useCallback, useMemo } from "react";

import { ICON_NAME } from "@p4b/ui/components/Icon";

import { useTranslation } from "@/i18n/client";

import { formatNumber } from "@/lib/utils/format-number";
import { hasNestedSchemaPath } from "@/lib/utils/zod";
import {
  FormatNumberTypes,
  WidgetConfigSchema,
  formatNumberTypes,
  widgetSchemaMap,
} from "@/lib/validations/widget";

import type { SelectorItem } from "@/types/map/common";

import useLayerFields from "@/hooks/map/CommonHooks";
import { useLayerByGeomType, useLayerDatasetId } from "@/hooks/map/ToolsHooks";

import LayerFieldSelector from "@/components/map/common/LayerFieldSelector";
import SectionHeader from "@/components/map/panels/common/SectionHeader";
import SectionOptions from "@/components/map/panels/common/SectionOptions";
import Selector from "@/components/map/panels/common/Selector";
import TextFieldInput from "@/components/map/panels/common/TextFieldInput";

export interface WidgetConfigProps {
  active?: boolean;
  sectionLabel?: string;
  config: WidgetConfigSchema; // Assume WidgetConfigSchema handles 'options' access directly for now
  onChange: (widget: WidgetConfigSchema) => void;
}

export const NumberFormatSelector = ({
  numberFormat,
  onNumberFormatChange,
}: {
  numberFormat?: FormatNumberTypes;
  onNumberFormatChange?: (format: FormatNumberTypes) => void;
}) => {
  const { t, i18n } = useTranslation("common");

  const numberFormats = useMemo(() => {
    return formatNumberTypes.options.map((format) => {
      let label = format as string;
      switch (format) {
        case "none":
          label = t("none");
          break;
        case "decimal_max":
          label = t("decimal_max");
          break;
        case "integer":
        case "compact":
        case "grouping":
          label = `${formatNumber(1000, format, i18n.language)} - ${t(`formatTypes.${format}`)}`;
          break;
        case "grouping_2d":
        case "signed_2d":
        case "compact_1d":
        case "currency_usd":
        case "currency_eur":
          label = `${formatNumber(12345.678, format, i18n.language)} - ${t(`formatTypes.${format}`)}`;
          break;
        case "percent":
        case "percent_1d":
        case "percent_2d":
          label = `${formatNumber(0.01, "none", i18n.language)} ${t("is")} ${formatNumber(0.01, format, i18n.language)}`;
          break;
        case "decimal_2":
        case "decimal_3":
          label = `${formatNumber(1.234, format, i18n.language)} - ${t(`formatTypes.${format}`)}`;
          break;
        default:
          break;
      }
      return {
        label,
        value: format,
      };
    });
  }, []);

  const selectedFormat = useMemo(() => {
    return numberFormat ? numberFormats.find((item) => item.value === numberFormat) : undefined;
  }, [numberFormat, numberFormats]);

  return (
    <Selector
      selectedItems={selectedFormat}
      setSelectedItems={(item: SelectorItem) => {
        onNumberFormatChange?.(item.value as FormatNumberTypes);
      }}
      items={numberFormats}
      label={t("number_format")}
    />
  );
};

export const WidgetInfo = ({ sectionLabel, config, onChange }: WidgetConfigProps) => {
  const { t } = useTranslation("common");
  const schema = widgetSchemaMap[config.type];
  const hasTitleDef = useMemo(() => {
    return hasNestedSchemaPath(schema, "setup.title");
  }, [schema]);

  const hasDescriptionDef = useMemo(() => {
    return hasNestedSchemaPath(schema, "options.description");
  }, [schema]);

  /**
   * Handles changes for properties nested under 'setup' or 'options' in the config.
   * @param parentKey The top-level key ('setup' or 'options').
   * @param propertyKey The nested key (e.g., 'title', 'description').
   * @param value The new value for the property.
   */
  const handleConfigChange = useCallback(
    (parentKey: "setup" | "options", propertyKey: string, value: string) => {
      const currentParent = (config as any)[parentKey] || {};

      const updatedParent = {
        ...currentParent,
        [propertyKey]: value,
      };

      onChange({
        ...config,
        [parentKey]: updatedParent,
      } as WidgetConfigSchema);
    },
    [config, onChange]
  );

  return (
    <>
      <SectionHeader
        active
        alwaysActive
        label={sectionLabel ?? t("info")}
        icon={ICON_NAME.CIRCLEINFO}
        disableAdvanceOptions
      />
      <SectionOptions
        active
        baseOptions={
          <>
            {hasTitleDef && (
              <TextFieldInput
                type="text"
                label={t("title")}
                placeholder={t("add_widget_title")}
                clearable={false}
                // Safely access title, using 'as any' for now to match context
                value={(config.setup as any)?.title || ""}
                onChange={(value: string) => {
                  handleConfigChange("setup", "title", value);
                }}
              />
            )}
            {hasDescriptionDef && (
              <TextFieldInput
                type="text"
                label={t("description")}
                placeholder={t("add_widget_description")}
                multiline
                clearable={false}
                // Safely access description, using 'as any' for now to match context
                value={(config as any)?.options?.description || ""}
                onChange={(value: string) => {
                  handleConfigChange("options", "description", value);
                }}
              />
            )}
          </>
        }
      />
    </>
  );
};

export const WidgetData = ({ sectionLabel, config, onChange }: WidgetConfigProps) => {
  const { t } = useTranslation("common");
  const schema = widgetSchemaMap[config.type];
  const { projectId } = useParams();
  const { filteredLayers } = useLayerByGeomType(["feature", "table"], undefined, projectId as string);

  const hasLayerProjectIdDef = useMemo(() => {
    return hasNestedSchemaPath(schema, "setup.layer_project_id");
  }, [schema]);

  const hasColumnNameDef = useMemo(() => {
    return hasNestedSchemaPath(schema, "setup.column_name");
  }, [schema]);

  const selectedLayer = useMemo(() => {
    return filteredLayers.find((layer) => layer.value === (config?.setup as any)?.layer_project_id);
  }, [filteredLayers, (config?.setup as any)?.layer_project_id]);

  const selectedLayerDatasetId = useLayerDatasetId(
    selectedLayer?.value as number | undefined,
    projectId as string
  );

  const { layerFields } = useLayerFields(selectedLayerDatasetId || "");

  const selectedColumnName = useMemo(() => {
    if (!hasColumnNameDef || !selectedLayer) return undefined;
    return layerFields.find((field) => field.name === (config?.setup as any)?.column_name);
  }, [hasColumnNameDef, selectedLayer, (config?.setup as any)?.column_name, layerFields]);

  const handleConfigChange = useCallback(
    (propertyKey: string, value: any) => {
      const updatedSetup = {
        ...(config.setup as any),
        [propertyKey]: value,
      };
      onChange({
        ...config,
        setup: updatedSetup,
      } as WidgetConfigSchema);
    },
    [config, onChange]
  );

  return (
    <>
      <SectionHeader
        active
        alwaysActive
        label={sectionLabel ?? t("data")}
        disableAdvanceOptions
        icon={ICON_NAME.LAYERS}
      />
      <SectionOptions
        active
        baseOptions={
          <>
            {hasLayerProjectIdDef && (
              <Selector
                selectedItems={selectedLayer}
                setSelectedItems={(item: SelectorItem | undefined) => {
                  handleConfigChange("layer_project_id", item?.value);
                }}
                items={filteredLayers}
                emptyMessage={t("no_layers_found")}
                emptyMessageIcon={ICON_NAME.LAYERS}
                label={t("select_layer")}
                placeholder={t("select_layer")}
              />
            )}

            {selectedLayer && hasColumnNameDef && (
              <LayerFieldSelector
                fields={layerFields}
                selectedField={selectedColumnName}
                disabled={!selectedLayer}
                setSelectedField={(field) => {
                  handleConfigChange("column_name", field?.name);
                }}
                label={t("select_field")}
              />
            )}
          </>
        }
      />
    </>
  );
};

export const WidgetOptions = ({ active = true, sectionLabel, config, onChange }: WidgetConfigProps) => {
  const { t } = useTranslation("common");
  const schema = widgetSchemaMap[config.type];

  const hasCrossFilterDef = useMemo(() => {
    return hasNestedSchemaPath(schema, "options.cross_filter");
  }, [schema]);

  const hasFilterViewPortDef = useMemo(() => {
    return hasNestedSchemaPath(schema, "options.filter_by_viewport");
  }, [schema]);

  const hasZoomToSelectionDef = useMemo(() => {
    return hasNestedSchemaPath(schema, "options.zoom_to_selection");
  }, [schema]);

  const hasNumberFormatDef = useMemo(() => {
    return hasNestedSchemaPath(schema, "options.format");
  }, [schema]);

  const handleOptionChange = useCallback(
    (key: string, value: any) => {
      const updatedOptions = {
        ...((config as any).options || {}),
        [key]: value, // Dynamically set the property based on the 'key' argument.
      };
      onChange({
        ...config,
        options: updatedOptions,
      } as WidgetConfigSchema); // Assert the type for the onChange callback.
    },
    [config, onChange]
  );

  return (
    <>
      <SectionHeader
        active={active}
        alwaysActive
        label={sectionLabel ?? t("options")}
        disableAdvanceOptions
        icon={ICON_NAME.SLIDERS}
      />
      <SectionOptions
        active={active}
        baseOptions={
          <Stack>
            {hasCrossFilterDef && (
              <FormControlLabel
                control={
                  <Checkbox
                    size="small"
                    color="primary"
                    // Access config.options safely, using 'as any' for now to match context.
                    checked={!!(config as any)?.options?.cross_filter}
                    onChange={(e) => {
                      handleOptionChange("cross_filter", e.target.checked);
                    }}
                  />
                }
                label={
                  <Stack direction="row" alignItems="center" spacing={2}>
                    <Typography variant="body2">{t("cross_filter")}</Typography>
                    <Tooltip title={t("cross_filter_tooltip")} placement="top" arrow>
                      <HelpOutlineIcon
                        style={{
                          fontSize: "12px",
                        }}
                      />
                    </Tooltip>
                  </Stack>
                }
              />
            )}

            {hasFilterViewPortDef && (
              <FormControlLabel
                control={
                  <Checkbox
                    size="small"
                    color="primary"
                    checked={!!(config as any)?.options?.filter_by_viewport}
                    onChange={(e) => {
                      handleOptionChange("filter_by_viewport", e.target.checked);
                    }}
                  />
                }
                label={<Typography variant="body2">{t("filter_viewport")}</Typography>}
              />
            )}

            {hasZoomToSelectionDef && (
              <FormControlLabel
                control={
                  <Checkbox
                    size="small"
                    color="primary"
                    checked={!!(config as any)?.options?.zoom_to_selection}
                    onChange={(e) => {
                      handleOptionChange("zoom_to_selection", e.target.checked);
                    }}
                  />
                }
                label={<Typography variant="body2">{t("zoom_to_selection")}</Typography>}
              />
            )}

            {hasNumberFormatDef && (
              <Stack sx={{ mt: 2 }}>
                <NumberFormatSelector
                  numberFormat={(config as any)?.options?.format}
                  onNumberFormatChange={(format) => handleOptionChange("format", format)}
                />
              </Stack>
            )}
          </Stack>
        }
      />
    </>
  );
};
