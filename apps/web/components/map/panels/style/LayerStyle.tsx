import { Box, Button, CircularProgress, Divider, Stack, Tooltip, Typography } from "@mui/material";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { useMap } from "react-map-gl/maplibre";
import { toast } from "react-toastify";

import { ICON_NAME, Icon } from "@p4b/ui/components/Icon";

import { getLayerClassBreaks, getLayerUniqueValues, updateBaseLayerProperties } from "@/lib/api/layers";
import { updateProjectLayer } from "@/lib/api/projects";
import { setStyleClipboard } from "@/lib/store/layer/slice";
import { COLOR_RANGES } from "@/lib/constants/color";
import {
  type ClassBreaks,
  type ColorMap,
  type FeatureLayerPointProperties,
  type FeatureLayerProperties,
  type LayerUniqueValues,
  type MarkerMap,
  classBreaks,
} from "@/lib/validations/layer";
import type { ProjectLayer } from "@/lib/validations/project";

import useLayerFields from "@/hooks/map/CommonHooks";
import { useProjectLayerFeatureCount } from "@/hooks/map/useProjectLayerFeatureCount";

import { canSetDefaultStyle } from "@/lib/utils/layerPermissions";
import { useActiveLayer, useFilteredProjectLayers } from "@/hooks/map/LayerPanelHooks";
import { useAppDispatch, useAppSelector } from "@/hooks/store/ContextHooks";
import AccordionWrapper from "@/components/common/AccordionWrapper";
import FormLabelHelper from "@/components/common/FormLabelHelper";
import SectionHeader from "@/components/map/panels/common/SectionHeader";
import SliderInput from "@/components/map/panels/common/SliderInput";
import ClusteringSection from "@/components/map/panels/style/clustering/ClusteringSection";
import ColorOptions from "@/components/map/panels/style/color/ColorOptions";
import GeneralOptions from "@/components/map/panels/style/general/GeneralOptions";
import PopupSection from "@/components/map/panels/style/popup/PopupSection";
import LabelOptions from "@/components/map/panels/style/label/LabelOptions";
import { LegendOptions } from "@/components/map/panels/style/legend/LegendOptions";
import LineStyleSection from "@/components/map/panels/style/line/LineStyleSection";
import MarkerOptions from "@/components/map/panels/style/marker/MarkerOptions";
import Settings from "@/components/map/panels/style/settings/Settings";

enum LayerStylePanels {
  STYLE = "style",
  LABELS = "labels",
  POPUP = "popup",
  LEGEND = "legend",
}

const LayerStylePanel = ({ projectId }: { projectId: string }) => {
  const { t } = useTranslation("common");
  const { map } = useMap();
  const dispatch = useAppDispatch();
  const styleClipboard = useAppSelector((state) => state.layers.styleClipboard);

  const [expanded, setExpanded] = useState<LayerStylePanels | false>(LayerStylePanels.STYLE);
  const [isDefaultSaved, setIsDefaultSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleAccordionChange =
    (panel: LayerStylePanels) => (_event: React.SyntheticEvent, isExpanded: boolean) => {
      setExpanded(isExpanded ? panel : false);
    };

  const { activeLayer } = useActiveLayer(projectId);
  const { featureCount } = useProjectLayerFeatureCount({
    projectLayer: activeLayer,
    enabled: activeLayer?.feature_layer_geometry_type === "point",
  });

  const { layers: projectLayers, mutate: mutateProjectLayers } = useFilteredProjectLayers(projectId);
  const { layerFields } = useLayerFields(activeLayer?.layer_id || "");

  const layerProperties = activeLayer?.properties as FeatureLayerProperties;
  const updateLayerStyle = useCallback(
    async (newStyle: FeatureLayerProperties) => {
      if (!activeLayer) return;
      const layers = JSON.parse(JSON.stringify(projectLayers));
      const index = layers.findIndex((l) => l.id === activeLayer.id);
      const layerToUpdate = layers[index] as ProjectLayer;
      if (!layerToUpdate.properties) {
        layerToUpdate.properties = {} as FeatureLayerProperties;
      }

      layerToUpdate.properties = newStyle;
      await mutateProjectLayers(layers, false);
      await updateProjectLayer(projectId, activeLayer.id, layerToUpdate);
    },
    [activeLayer, projectLayers, mutateProjectLayers, projectId]
  );

  const createColorMapFromClassBreaks = useCallback((colors: string[], breakValues: string[]) => {
    const colorMap = [] as ColorMap;
    colors.forEach((color, index) => {
      const breakValue = breakValues[index] || "0";
      colorMap.push([[breakValue], color]);
    });
    return colorMap;
  }, []);

  const updateColorClassificationBreaks = useCallback(
    async (updateType: "color" | "stroke_color", newStyle: FeatureLayerProperties) => {
      if (!activeLayer) return;
      if (!newStyle[`${updateType}_field`]?.name) return;
      let classBreakType = newStyle[`${updateType}_scale`];
      const existingBreaks = layerProperties[`${updateType}_scale_breaks`];
      if (classBreakType === classBreaks.Enum.custom_breaks && existingBreaks) {
        const breakValues = [] as string[];
        if (classBreakType === layerProperties[`${updateType}_scale`]) {
          // A palette picked from the list carries colors only; keep the saved break values.
          const colorMap =
            newStyle[`${updateType}_range`]?.color_map ?? layerProperties[`${updateType}_range`]?.color_map;
          if (colorMap) {
            colorMap.forEach((colorMapItem) => {
              if (colorMapItem?.[0]?.[0] !== undefined) breakValues.push(colorMapItem[0][0]);
            });
          }
        } else {
          if (existingBreaks) {
            breakValues.push(existingBreaks.min.toString());
            existingBreaks.breaks.forEach((value) => {
              breakValues.push(value.toString());
            });
          }
        }
        newStyle[`${updateType}_range`]["color_map"] = createColorMapFromClassBreaks(
          newStyle[`${updateType}_range`]?.colors || [],
          breakValues
        );
        return;
      }
      if (
        newStyle[`${updateType}_scale`] !== layerProperties[`${updateType}_scale`] ||
        newStyle[`${updateType}_field`]?.name !== layerProperties[`${updateType}_field`]?.name ||
        newStyle[`${updateType}_range`]?.colors?.length !==
          layerProperties[`${updateType}_range`]?.colors?.length
      ) {
        if (classBreakType === classBreaks.Enum.custom_breaks) {
          classBreakType = classBreaks.Enum.equal_interval;
        }
        const breaks = await getLayerClassBreaks(
          activeLayer.layer_id,
          classBreakType,
          newStyle[`${updateType}_field`]?.name as string,
          newStyle[`${updateType}_range`]?.colors?.length - 1
        );
        if (breaks && breaks?.breaks?.length === newStyle[`${updateType}_range`]?.colors?.length - 1)
          newStyle[`${updateType}_scale_breaks`] = breaks;
      }
    },
    [activeLayer, createColorMapFromClassBreaks, layerProperties]
  );

  const updateSizeClassificationBreaks = useCallback(
    async (
      updateType: "radius" | "stroke_width" | "marker_size",
      newStyle: FeatureLayerProperties,
    ) => {
      if (!activeLayer) return;
      const fieldName = newStyle[`${updateType}_field`]?.name;
      if (!fieldName) {
        newStyle[`${updateType}_scale_breaks`] = undefined;
        newStyle[`${updateType}_ordinal_map`] = undefined;
        return;
      }
      const numSteps = (newStyle[`${updateType}_num_steps`] as number) ?? 5;
      const scale = (newStyle[`${updateType}_scale`] as ClassBreaks) ?? classBreaks.Enum.quantile;
      const oldFieldName = layerProperties[`${updateType}_field`]?.name;

      // Custom breaks: user edits break values directly — never auto-fetch
      if (scale === classBreaks.Enum.custom_breaks) {
        if (!newStyle[`${updateType}_scale_breaks`]) {
          // Initialize from existing breaks or fetch once with equal_interval
          const existing = layerProperties[`${updateType}_scale_breaks`];
          if (existing) {
            newStyle[`${updateType}_scale_breaks`] = existing;
          } else {
            try {
              const breaks = await getLayerClassBreaks(activeLayer.layer_id, classBreaks.Enum.equal_interval, fieldName, numSteps - 1);
              if (breaks) newStyle[`${updateType}_scale_breaks`] = breaks;
            } catch (e) {
              console.warn(`Failed to initialize custom size breaks:`, e);
            }
          }
        }
        return;
      }

      // Ordinal: categorical → fixed size per unique value
      if (scale === classBreaks.Enum.ordinal) {
        const hasMap = !!newStyle[`${updateType}_ordinal_map`];
        // If the map is already set and the field hasn't changed, keep user edits untouched
        if (hasMap && fieldName === oldFieldName) return;
        // Otherwise (re)initialize: first-time, field changed, or scale just switched to ordinal
        try {
          const uniqueValues = await getLayerUniqueValues(activeLayer.layer_id, fieldName, 20);
          const defaultSize = (newStyle[`${updateType}_range`] as number[] | undefined)?.[0] ?? 5;
          newStyle[`${updateType}_ordinal_map`] = uniqueValues.items.map(
            ({ value }: { value: string }) => [value, defaultSize] as [string, number]
          );
        } catch (e) {
          console.warn(`Failed to fetch unique values for ordinal size:`, e);
        }
        return;
      }

      // Standard classification (quantile / equal_interval / std_dev / heads_and_tails)
      // Clear stale ordinal map so re-selecting ordinal later fetches fresh values
      newStyle[`${updateType}_ordinal_map`] = undefined;
      const oldScale = layerProperties[`${updateType}_scale`];
      const oldNumSteps = layerProperties[`${updateType}_num_steps`];
      if (fieldName === oldFieldName && scale === oldScale && numSteps === oldNumSteps && newStyle[`${updateType}_scale_breaks`]) return;
      try {
        const breaks = await getLayerClassBreaks(activeLayer.layer_id, scale, fieldName, numSteps - 1);
        if (breaks) newStyle[`${updateType}_scale_breaks`] = breaks;
      } catch (e) {
        console.warn(`Failed to fetch size breaks for field "${fieldName}":`, e);
      }
    },
    [activeLayer, layerProperties],
  );

  const updateOrdinalValues = useCallback(
    async (updateType: "color" | "stroke_color" | "marker", newStyle: FeatureLayerProperties) => {
      if (!activeLayer) return;
      if (!newStyle[`${updateType}_field`]?.name) return;
      const oldFieldName = layerProperties[`${updateType}_field`]?.name;
      const newFieldName = newStyle[`${updateType}_field`]?.name;
      if (updateType === "marker" && oldFieldName !== newFieldName) {
        // For markers, use existing mapping length or default to reasonable limit
        const existingMapping = newStyle[`${updateType}_mapping`];
        const limit = existingMapping?.length || 10;
        const uniqueValues = await getLayerUniqueValues(
          activeLayer.layer_id,
          newStyle[`${updateType}_field`]?.name as string,
          limit
        );
        const markerMap = [] as MarkerMap;
        const emptyMarker = {
          name: "",
          url: "",
          source: "custom" as const,
          category: "",
          id: "",
        };
        uniqueValues.items.forEach((item: LayerUniqueValues) => {
          markerMap.push([[item.value], emptyMarker]);
        });
        newStyle[`${updateType}_mapping`] = markerMap;
      } else if (updateType !== "marker") {
        const existingColorMap = layerProperties[`${updateType}_range`]?.color_map;
        const fieldChanged = oldFieldName !== newFieldName;
        const currentRange = newStyle[`${updateType}_range`];

        if (!existingColorMap?.length || fieldChanged) {
          // Fetch unique values: first time setup or the attribute field changed
          const uniqueValues = await getLayerUniqueValues(
            activeLayer.layer_id,
            newStyle[`${updateType}_field`]?.name as string,
            100
          );

          const actualCount = Math.min(uniqueValues.items.length, 12);

          let matchingPalette = COLOR_RANGES.find(
            (range) =>
              range.colors.length === actualCount &&
              range.category === currentRange?.category &&
              range.type === currentRange?.type
          );

          if (!matchingPalette && currentRange?.type) {
            matchingPalette = COLOR_RANGES.find(
              (range) => range.colors.length === actualCount && range.type === currentRange.type
            );
          }

          if (!matchingPalette && !currentRange?.type) {
            matchingPalette = COLOR_RANGES.find((range) => range.colors.length === actualCount);
          }

          const colors = matchingPalette?.colors || currentRange?.colors?.slice(0, actualCount) || [];

          const colorMap = [] as ColorMap;
          uniqueValues.items.slice(0, actualCount).forEach((item: LayerUniqueValues, index: number) => {
            // Boolean columns come back as true/false; the color map and the match expression compare strings.
            colorMap.push([[typeof item.value === "boolean" ? String(item.value) : item.value], colors[index]]);
          });
          newStyle[`${updateType}_range`].color_map = colorMap;
          newStyle[`${updateType}_range`].colors = colors;
          if (matchingPalette) {
            newStyle[`${updateType}_range`].name = matchingPalette.name;
            newStyle[`${updateType}_range`].category = matchingPalette.category;
            newStyle[`${updateType}_range`].type = matchingPalette.type;
          }
        } else if (currentRange?.type !== "custom") {
          // Preset → preset (or preset → custom by palette swap): the
          // user just picked a different palette. The field and its
          // values are unchanged, so remap the new palette's colors
          // onto the existing value assignments without hitting the
          // API.
          //
          // We deliberately skip this branch when the incoming range
          // is `type: "custom"` — that flag means the user just
          // applied edits via the CustomColorScale popper (added a
          // row, multi-valued a row, recolored, etc.). Their edits
          // already live on `newStyle.color_range.color_map`; rebuilding
          // from `existingColorMap` would erase rows the user added
          // and revert multi-value selections to the snapshot from
          // before they opened the popper.
          const newColors = currentRange?.colors ?? [];
          const entryCount = Math.min(existingColorMap.length, newColors.length);
          if (entryCount > 0) {
            newStyle[`${updateType}_range`].color_map = existingColorMap
              .slice(0, entryCount)
              .map(([values], index) => [values, newColors[index]] as ColorMap[number]);
            newStyle[`${updateType}_range`].colors = newColors.slice(0, entryCount);
          }
        }
      }
      updateLayerStyle(newStyle);
    },
    [activeLayer, updateLayerStyle, layerProperties]
  );

  const onToggleChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>, property: string) => {
      const newStyle = JSON.parse(JSON.stringify(layerProperties)) || {};
      newStyle[property] = event.target.checked;
      if (property === "stroked" && layerProperties?.["custom_marker"]) {
        newStyle["custom_marker"] = false;
      }
      if (property === "custom_marker" && layerProperties?.["stroked"]) {
        newStyle["stroked"] = false;
      }

      updateLayerStyle(newStyle);
    },
    [updateLayerStyle, layerProperties]
  );

  const markerExists = useMemo(() => {
    if (!layerProperties) return false;
    return (
      layerProperties["custom_marker"] &&
      (layerProperties["marker"]?.name ||
        (layerProperties["marker_field"] && layerProperties["marker_mapping"]?.length > 0))
    );
  }, [layerProperties]);

  const [collapseFillOptions, setCollapseFillOptions] = useState(true);
  const [collapseStrokeColorOptions, setCollapseStrokeColorOptions] = useState(true);
  const [collapseStrokeWidthOptions, setCollapseStrokeWidthOptions] = useState(true);
  const [collapsedMarkerIconOptions, setCollapsedMarkerIconOptions] = useState(true);
  const [collapseRadiusOptions, setCollapseRadiusOptions] = useState(true);
  const [rasterOpacity, setRasterOpacity] = useState(layerProperties?.opacity ?? 1);

  useEffect(() => {
    setRasterOpacity(layerProperties?.opacity ?? 1);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeLayer?.id]);

  useEffect(() => {
    setIsDefaultSaved(false);
  }, [activeLayer?.id]);

  const handleCopyStyle = () => {
    if (!activeLayer || !activeLayer.properties) return;
    dispatch(setStyleClipboard({
      sourceLayerName: activeLayer.name,
      properties: activeLayer.properties as FeatureLayerProperties,
    }));
  };

  const handlePasteStyle = async () => {
    if (!activeLayer || !styleClipboard) return;
    await updateLayerStyle(styleClipboard.properties);
  };

  const handleSetDefault = async () => {
    if (!activeLayer || !activeLayer.properties || !activeLayer.layer_id) return;
    setIsSaving(true);
    try {
      await updateBaseLayerProperties(
        activeLayer.layer_id,
        activeLayer.properties as Record<string, unknown>
      );
      setIsDefaultSaved(true);
      toast.success(t("style_saved_as_dataset_default_success"));
    } catch (e) {
      console.error("Failed to set default style:", e);
      toast.error(t("style_saved_as_dataset_default_error"));
    } finally {
      setIsSaving(false);
    }
  };

  if (!activeLayer || !layerProperties) return null;

  return (
    <>
      <Stack direction="row" spacing={1} sx={{ px: 2, py: 2, borderBottom: "1px solid", borderColor: "divider" }}>
        <Tooltip title={t("copy_style")} placement="bottom">
          <span style={{ display: "flex" }}>
            <Button variant="outlined" size="small" sx={{ minWidth: 36, width: 36, height: 36, px: 0 }} onClick={handleCopyStyle}>
              <Icon iconName={ICON_NAME.COPY} style={{ fontSize: 16 }} />
            </Button>
          </span>
        </Tooltip>
        <Tooltip title={styleClipboard ? `${t("paste_style")} (${styleClipboard.sourceLayerName})` : t("paste_style")} placement="bottom">
          <span style={{ display: "flex" }}>
            <Button variant="outlined" size="small" sx={{ minWidth: 36, width: 36, height: 36, px: 0 }} disabled={!styleClipboard} onClick={handlePasteStyle}>
              <Icon iconName={ICON_NAME.SLIDERS} style={{ fontSize: 16 }} />
            </Button>
          </span>
        </Tooltip>
        {canSetDefaultStyle(activeLayer) && (
        <Tooltip title={t("set_as_default_style")} placement="bottom">
          <span style={{ display: "flex" }}>
            <Button
              variant={isDefaultSaved ? "contained" : "outlined"}
              size="small"
              sx={{ minWidth: 36, width: 36, height: 36, px: 0 }}
              disabled={isSaving}
              onClick={handleSetDefault}>
              {isSaving ? <CircularProgress size={16} color="inherit" /> : <Icon iconName={ICON_NAME.STAR} style={{ fontSize: 16 }} />}
            </Button>
          </span>
        </Tooltip>
        )}
      </Stack>
      <Box
        sx={{
          display: "flex",
          p: 2,
          flexDirection: "column",
        }}>
        {activeLayer && (
          <GeneralOptions
            key={activeLayer.id}
            layer={activeLayer}
            onStyleChange={async (newStyle) => {
              updateLayerStyle(newStyle);
            }}
          />
        )}
      </Box>
      <Divider sx={{ mb: 0 }} />
      {activeLayer?.type === "raster" && (
        <Box sx={{ p: 2 }}>
          <FormLabelHelper label={t("opacity")} color="inherit" />
          <Box sx={{ px: 1 }}>
            <SliderInput
              value={rasterOpacity}
              isRange={false}
              min={0}
              max={1}
              step={0.01}
              onChange={(value) => setRasterOpacity(value as number)}
              onChangeCommitted={(value) => {
                const newStyle = JSON.parse(JSON.stringify(layerProperties)) || {};
                newStyle.opacity = value as number;
                updateLayerStyle(newStyle);
              }}
            />
          </Box>
        </Box>
      )}
      {activeLayer?.type === "feature" && (
        <>
          <AccordionWrapper
            boxShadow="none"
            backgroundColor="transparent"
            disableGutters
            expanded={expanded === LayerStylePanels.STYLE}
            onChange={handleAccordionChange(LayerStylePanels.STYLE)}
            header={
              <>
                <Typography variant="body2" fontWeight="bold">
                  {t("style")}
                </Typography>
              </>
            }
            accordionSxProps={{
              "&:before": {
                display: "none",
              },
            }}
            body={
              <>
                <Box
                  sx={{
                    display: "flex",
                    px: 4,
                    flexDirection: "column",
                  }}>
                  {activeLayer && (
                    <Stack>
                      {/* {FILL COLOR} */}
                      {activeLayer.feature_layer_geometry_type &&
                        ["polygon", "point"].includes(activeLayer.feature_layer_geometry_type) && (
                          <>
                            <SectionHeader
                              active={layerProperties.filled}
                              onToggleChange={(event) => {
                                onToggleChange(event, "filled");
                              }}
                              label={
                                activeLayer?.feature_layer_geometry_type === "line"
                                  ? t("color")
                                  : t("fill_color")
                              }
                              collapsed={collapseFillOptions}
                              setCollapsed={setCollapseFillOptions}
                            />
                            <ColorOptions
                              type="color"
                              layerStyle={layerProperties}
                              active={!!layerProperties.filled}
                              layerFields={layerFields}
                              collapsed={collapseFillOptions}
                              selectedField={layerProperties.color_field}
                              onStyleChange={async (newStyle: FeatureLayerProperties) => {
                                if (
                                  newStyle.color_field?.type === "number" &&
                                  newStyle.color_scale !== "ordinal"
                                ) {
                                  await updateColorClassificationBreaks("color", newStyle);
                                } else if (newStyle.color_scale === "ordinal") {
                                  await updateOrdinalValues("color", newStyle);
                                }

                                updateLayerStyle(newStyle);
                              }}
                              layerId={activeLayer?.layer_id}
                            />
                          </>
                        )}

                      {/* {STROKE} */}
                      <SectionHeader
                        active={!!layerProperties.stroked}
                        onToggleChange={(event) => {
                          onToggleChange(event, "stroked");
                        }}
                        alwaysActive={activeLayer?.feature_layer_geometry_type === "line"}
                        label={
                          activeLayer?.feature_layer_geometry_type === "line" ? t("color") : t("stroke_color")
                        }
                        collapsed={collapseStrokeColorOptions}
                        setCollapsed={setCollapseStrokeColorOptions}
                      />

                      <ColorOptions
                        type="stroke_color"
                        showOpacity={activeLayer?.feature_layer_geometry_type === "line"}
                        layerStyle={layerProperties}
                        active={!!layerProperties.stroked}
                        layerFields={layerFields}
                        collapsed={collapseStrokeColorOptions}
                        selectedField={layerProperties.stroke_color_field}
                        onStyleChange={async (newStyle: FeatureLayerProperties) => {
                          if (
                            newStyle.stroke_color_field?.type === "number" &&
                            newStyle.stroke_color_scale !== "ordinal"
                          ) {
                            await updateColorClassificationBreaks("stroke_color", newStyle);
                          } else if (newStyle.stroke_color_scale === "ordinal") {
                            await updateOrdinalValues("stroke_color", newStyle);
                          }
                          updateLayerStyle(newStyle);
                        }}
                        layerId={activeLayer?.layer_id}
                      />

                      {/* {LINE STROKE} */}
                      {activeLayer.feature_layer_geometry_type &&
                        ["line", "polygon", "point"].includes(activeLayer.feature_layer_geometry_type) && (
                          <>
                            <SectionHeader
                              active={!!layerProperties.stroked}
                              onToggleChange={(event) => {
                                onToggleChange(event, "stroked");
                              }}
                              alwaysActive={activeLayer?.feature_layer_geometry_type === "line"}
                              label={t("stroke_width")}
                              collapsed={collapseStrokeWidthOptions}
                              setCollapsed={setCollapseStrokeWidthOptions}
                            />

                            <Settings
                              type="stroke_width"
                              layerStyle={layerProperties}
                              active={!!layerProperties.stroked}
                              collapsed={collapseStrokeWidthOptions}
                              onStyleChange={async (newStyle: FeatureLayerProperties) => {
                                await updateSizeClassificationBreaks("stroke_width", newStyle);
                                updateLayerStyle(newStyle);
                              }}
                              layerFields={layerFields}
                              selectedField={layerProperties["stroke_width_field"]}
                            />
                          </>
                        )}

                      {activeLayer.feature_layer_geometry_type === "line" && (
                        <LineStyleSection
                          layerProperties={layerProperties}
                          onStyleChange={(newStyle) => updateLayerStyle(newStyle)}
                        />
                      )}

                      {/* {CLUSTERING}
                          Only available for point layers ≤ 100k features
                          (the cap on the bulk-features endpoint used by the
                          GeoJSON cluster source). Layers that already have
                          clustering enabled keep the section visible so users
                          can still toggle it off if the layer has grown. */}
                      {activeLayer.feature_layer_geometry_type === "point" &&
                        (featureCount === undefined ||
                          featureCount <= 100_000 ||
                          !!(layerProperties as FeatureLayerPointProperties)?.cluster?.enabled) && (
                          <ClusteringSection
                            layerProperties={layerProperties}
                            onStyleChange={(newStyle) => updateLayerStyle(newStyle)}
                          />
                        )}

                      {/* {MARKER ICON} */}
                      {activeLayer.feature_layer_geometry_type &&
                        activeLayer.feature_layer_geometry_type === "point" && (
                          <>
                            <SectionHeader
                              active={layerProperties["custom_marker"]}
                              alwaysActive={false}
                              onToggleChange={(event) => {
                                onToggleChange(event, "custom_marker");
                              }}
                              label={t("custom_marker")}
                              collapsed={collapsedMarkerIconOptions}
                              setCollapsed={setCollapsedMarkerIconOptions}
                            />

                            <MarkerOptions
                              type="marker"
                              layerStyle={layerProperties}
                              layerId={activeLayer?.layer_id}
                              active={!!layerProperties["custom_marker"]}
                              collapsed={collapsedMarkerIconOptions}
                              onStyleChange={async (newStyle: FeatureLayerProperties) => {
                                if (!map) return;
                                await updateOrdinalValues("marker", newStyle);
                                updateLayerStyle(newStyle);
                              }}
                              layerFields={layerFields}
                              selectedField={layerProperties["marker_field"]}
                            />
                          </>
                        )}

                      {/* {RADIUS/SIZE} */}
                      {activeLayer?.feature_layer_geometry_type &&
                        activeLayer.feature_layer_geometry_type === "point" && (
                          <>
                            {layerProperties["custom_marker"] && (
                              <>
                                <SectionHeader
                                  active={markerExists}
                                  alwaysActive={true}
                                  label={t("marker_settings")}
                                  collapsed={collapseRadiusOptions}
                                  setCollapsed={setCollapseRadiusOptions}
                                />
                                <Settings
                                  type="marker_size"
                                  layerStyle={layerProperties}
                                  active={markerExists}
                                  collapsed={collapseRadiusOptions}
                                  onStyleChange={async (newStyle: FeatureLayerProperties) => {
                                    if (!map) return;
                                    await updateSizeClassificationBreaks("marker_size", newStyle);
                                    updateLayerStyle(newStyle);
                                  }}
                                  layerFields={layerFields}
                                  selectedField={layerProperties["marker_size_field"]}
                                  activeLayer={activeLayer}
                                />
                              </>
                            )}

                            {!layerProperties["custom_marker"] && (
                              <>
                                <SectionHeader
                                  active={true}
                                  alwaysActive={true}
                                  label={t("point_settings")}
                                  collapsed={collapseRadiusOptions}
                                  setCollapsed={setCollapseRadiusOptions}
                                />

                                <Settings
                                  type="radius"
                                  layerStyle={layerProperties}
                                  active={true}
                                  collapsed={collapseRadiusOptions}
                                  onStyleChange={async (newStyle: FeatureLayerProperties) => {
                                    await updateSizeClassificationBreaks("radius", newStyle);
                                    updateLayerStyle(newStyle);
                                  }}
                                  layerFields={layerFields}
                                  selectedField={layerProperties["radius_field"]}
                                />
                              </>
                            )}
                          </>
                        )}
                    </Stack>
                  )}
                </Box>
              </>
            }
          />
          <Divider sx={{ m: 0 }} />
          <AccordionWrapper
            boxShadow="none"
            backgroundColor="transparent"
            disableGutters
            expanded={expanded === LayerStylePanels.LABELS}
            onChange={handleAccordionChange(LayerStylePanels.LABELS)}
            accordionSxProps={{
              "&:before": {
                display: "none",
              },
            }}
            header={
              <>
                <Typography variant="body2" fontWeight="bold">
                  {t("labels")}
                </Typography>
              </>
            }
            body={
              <Box
                sx={{
                  display: "flex",
                  px: 4,
                  flexDirection: "column",
                }}>
                {activeLayer && (
                  <LabelOptions
                    layer={activeLayer}
                    onStyleChange={async (newStyle) => {
                      updateLayerStyle(newStyle);
                    }}
                    key={activeLayer.id}
                  />
                )}
              </Box>
            }
          />
          <Divider sx={{ m: 0 }} />
          <AccordionWrapper
            boxShadow="none"
            backgroundColor="transparent"
            disableGutters
            expanded={expanded === LayerStylePanels.POPUP}
            onChange={handleAccordionChange(LayerStylePanels.POPUP)}
            header={
              <Typography variant="body2" fontWeight="bold">
                {t("popup")}
              </Typography>
            }
            accordionSxProps={{
              "&:before": {
                display: "none",
              },
            }}
            body={
              <Box
                sx={{
                  display: "flex",
                  px: 4,
                  flexDirection: "column",
                }}>
                {activeLayer && (
                  <PopupSection
                    layer={activeLayer}
                    onStyleChange={async (newStyle) => {
                      updateLayerStyle(newStyle);
                    }}
                    key={activeLayer.id}
                  />
                )}
              </Box>
            }
          />
        </>
      )}

      <Divider sx={{ m: 0 }} />
      <AccordionWrapper
        boxShadow="none"
        backgroundColor="transparent"
        disableGutters
        expanded={expanded === LayerStylePanels.LEGEND}
        onChange={handleAccordionChange(LayerStylePanels.LEGEND)}
        header={
          <Typography variant="body2" fontWeight="bold">
            {t("legend")}
          </Typography>
        }
        accordionSxProps={{
          "&:before": {
            display: "none",
          },
        }}
        body={
          <Box
            sx={{
              display: "flex",
              px: 4,
              flexDirection: "column",
            }}>
            {activeLayer && (
              <LegendOptions
                layer={activeLayer}
                onStyleChange={async (newStyle) => {
                  updateLayerStyle(newStyle);
                }}
              />
            )}
          </Box>
        }
      />
      <Divider sx={{ mt: 0 }} />
    </>
  );
};

export default LayerStylePanel;
