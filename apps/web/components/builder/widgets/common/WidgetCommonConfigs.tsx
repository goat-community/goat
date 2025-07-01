import { Checkbox, FormControlLabel, Stack, Typography } from "@mui/material";
import { useParams } from "next/navigation";
import { useMemo } from "react";

import { ICON_NAME } from "@p4b/ui/components/Icon";

import { useTranslation } from "@/i18n/client";

import { SelectorItem } from "@/types/map/common";

import useLayerFields from "@/hooks/map/CommonHooks";
import { useLayerByGeomType, useLayerDatasetId } from "@/hooks/map/ToolsHooks";

import LayerFieldSelector from "@/components/map/common/LayerFieldSelector";
import SectionHeader from "@/components/map/panels/common/SectionHeader";
import SectionOptions from "@/components/map/panels/common/SectionOptions";
import Selector from "@/components/map/panels/common/Selector";
import TextFieldInput from "@/components/map/panels/common/TextFieldInput";

export interface WidgetInfoProps {
  sectionLabel?: string;
  titleLabel?: string;
  titlePlaceholder?: string;
  titleValue: string;
  hasDescription?: boolean;
  descriptionLabel?: string;
  descriptionPlaceholder?: string;
  descriptionValue?: string;
  onTitleChange: (value: string) => void;
  onDescriptionChange?: (value: string) => void;
  disableAdvanceOptions?: boolean;
}

export const WidgetInfo = ({
  sectionLabel,
  titleLabel,
  titlePlaceholder,
  titleValue,
  hasDescription = false,
  descriptionLabel,
  descriptionPlaceholder,
  descriptionValue,
  onDescriptionChange,
  onTitleChange,
}: WidgetInfoProps) => {
  const { t } = useTranslation("common");
  return (
    <>
      <SectionHeader active alwaysActive label={sectionLabel ?? t("info")} disableAdvanceOptions />
      <SectionOptions
        active
        baseOptions={
          <>
            <TextFieldInput
              type="text"
              label={titleLabel ?? t("title")}
              placeholder={titlePlaceholder ?? t("add_widget_title")}
              clearable={false}
              value={titleValue}
              onChange={onTitleChange}
            />
            {hasDescription && (
              <TextFieldInput
                type="text"
                label={descriptionLabel ?? t("description")}
                placeholder={descriptionPlaceholder ?? t("add_widget_description")}
                multiline
                clearable={false}
                value={descriptionValue || ""}
                onChange={(value: string) => {
                  if (onDescriptionChange) {
                    onDescriptionChange(value);
                  }
                }}
              />
            )}
          </>
        }
      />
    </>
  );
};

export interface WidgetDataSelectorProps {
  sectionLabel?: string;
  projectLayerId?: number | undefined;
  hasColumnName?: boolean;
  columnName?: string | undefined;
  onProjectLayerIdChange?: (layerId: number | undefined) => void;
  onColumnNameChange?: (columnName: string | undefined) => void;
}

export const WidgetDataSelector = ({
  sectionLabel,
  projectLayerId,
  hasColumnName = true,
  columnName,
  onProjectLayerIdChange,
  onColumnNameChange,
}: WidgetDataSelectorProps) => {
  const { t } = useTranslation("common");
  const { projectId } = useParams();
  const { filteredLayers } = useLayerByGeomType(["feature", "table"], undefined, projectId as string);

  const selectedLayer = useMemo(() => {
    return filteredLayers.find((layer) => layer.value === projectLayerId);
  }, [filteredLayers, projectLayerId]);

  const selectedLayerDatasetId = useLayerDatasetId(
    selectedLayer?.value as number | undefined,
    projectId as string
  );

  const { layerFields } = useLayerFields(selectedLayerDatasetId || "");

  const selectedColumnName = useMemo(() => {
    if (!hasColumnName || !columnName) return undefined;
    return layerFields.find((field) => field.name === columnName);
  }, [layerFields, columnName]);

  return (
    <>
      <SectionHeader active alwaysActive label={sectionLabel ?? t("data")} disableAdvanceOptions />
      <SectionOptions
        active
        baseOptions={
          <>
            <Selector
              selectedItems={selectedLayer}
              setSelectedItems={(item: SelectorItem | undefined) => {
                onProjectLayerIdChange?.(item?.value as number | undefined);
              }}
              items={filteredLayers}
              emptyMessage={t("no_layers_found")}
              emptyMessageIcon={ICON_NAME.LAYERS}
              label={t("select_layer")}
              placeholder={t("select_layer")}
            />

            {selectedLayer && hasColumnName && (
              <LayerFieldSelector
                fields={layerFields}
                selectedField={selectedColumnName}
                disabled={!selectedLayer}
                setSelectedField={(field) => {
                  onColumnNameChange?.(field?.name);
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

export interface WidgetOptionsProps {
  sectionLabel?: string;
  hasCrossFilter?: boolean;
  crossFilter?: boolean;
  onCrossFilterChange?: (crossFilter: boolean) => void;
  hasFilterViewPort?: boolean;
  filterViewPort?: boolean;
  onFilterViewPortChange?: (filterViewPort: boolean) => void;
  hasZoomToSelection?: boolean;
  zoomToSelection?: boolean;
  onZoomToSelectionChange?: (zoomToSelection: boolean) => void;
}

export const WidgetOptions = ({
  sectionLabel,
  hasCrossFilter = false,
  crossFilter = false,
  onCrossFilterChange,
  hasFilterViewPort = false,
  filterViewPort = false,
  onFilterViewPortChange,
  hasZoomToSelection = false,
  zoomToSelection = false,
  onZoomToSelectionChange,
}: WidgetOptionsProps) => {
  const { t } = useTranslation("common");

  return (
    <>
      <SectionHeader active alwaysActive label={sectionLabel ?? t("options")} disableAdvanceOptions />
      <SectionOptions
        active
        baseOptions={
          <Stack>
            {hasCrossFilter && (
              <FormControlLabel
                control={
                  <Checkbox
                    size="small"
                    color="primary"
                    checked={!!crossFilter}
                    onChange={(e) => {
                      const isChecked = e.target.checked;
                      onCrossFilterChange?.(isChecked);
                    }}
                  />
                }
                label={<Typography variant="body2">{t("cross_filter")}</Typography>}
              />
            )}
            {hasFilterViewPort && (
              <FormControlLabel
                control={
                  <Checkbox
                    size="small"
                    color="primary"
                    checked={!!filterViewPort}
                    onChange={(e) => {
                      const isChecked = e.target.checked;
                      onFilterViewPortChange?.(isChecked);
                    }}
                  />
                }
                label={<Typography variant="body2">{t("filter_viewport")}</Typography>}
              />
            )}
            {hasZoomToSelection && (
              <FormControlLabel
                control={
                  <Checkbox
                    size="small"
                    color="primary"
                    checked={!!zoomToSelection}
                    onChange={(e) => {
                      const isChecked = e.target.checked;
                      onZoomToSelectionChange?.(isChecked);
                    }}
                  />
                }
                label={<Typography variant="body2">{t("zoom_to_selection")}</Typography>}
              />
            )}
          </Stack>
        }
      />
    </>
  );
};
