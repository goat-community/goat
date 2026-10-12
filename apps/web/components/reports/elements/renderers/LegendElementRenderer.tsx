"use client";

import { Box, Stack, Typography } from "@mui/material";
import React, { useCallback, useEffect, useMemo, useRef } from "react";
import { useTranslation } from "react-i18next";
import type { TypographyStyle } from "@/lib/constants/typography";
import { DEFAULT_FONT_FAMILY, LEGEND_TYPOGRAPHY_DEFAULTS } from "@/lib/constants/typography";
import { cleanEditedText } from "@/lib/utils/editableText";
import { rgbToHex } from "@/lib/utils/helpers";
import type { RGBColor } from "@/types/map/color";
import type { ProjectLayer } from "@/lib/validations/project";
import type { ReportElement } from "@/lib/validations/reportLayout";

import { LayerIcon } from "@/components/map/panels/layer/legend/LayerIcon";
import { LayerLegendPanel } from "@/components/map/panels/layer/legend/LayerLegend";

/**
 * Convert TypographyStyle to MUI sx props
 */
function typographyToSx(style?: TypographyStyle, role?: string): Record<string, unknown> {
  const defaults = role ? LEGEND_TYPOGRAPHY_DEFAULTS[role] : undefined;
  const sx: Record<string, unknown> = {};
  sx.fontFamily = style?.fontFamily || defaults?.fontFamily || DEFAULT_FONT_FAMILY;
  sx.fontSize = style?.fontSize || defaults?.fontSize;
  sx.fontWeight = style?.fontWeight || defaults?.fontWeight;
  if (style?.fontColor) sx.color = style.fontColor;
  return sx;
}

/**
 * Extract overrides with a given prefix, stripping the prefix from keys.
 * e.g. prefix="legenditem_5_" extracts "legenditem_5_item_0" -> "item_0"
 */
function extractPrefixedOverrides(
  overrides: Record<string, string> | undefined,
  prefix: string
): Record<string, string> | undefined {
  if (!overrides) return undefined;
  const result: Record<string, string> = {};
  let found = false;
  for (const [key, val] of Object.entries(overrides)) {
    if (key.startsWith(prefix)) {
      result[key.slice(prefix.length)] = val;
      found = true;
    }
  }
  return found ? result : undefined;
}

/**
 * Legend typography configuration (per text role)
 */
interface LegendTypographyConfig {
  title?: TypographyStyle;
  layerName?: TypographyStyle;
  legendItem?: TypographyStyle;
  caption?: TypographyStyle;
  heading?: TypographyStyle;
}

/**
 * Legend element configuration interface
 */
export interface LegendElementConfig {
  /** Title configuration */
  title?: {
    text?: string;
  };
  /** Map element ID to bind to (null = show all layers) */
  mapElementId?: string | null;
  /** Auto-update legend from connected map (default true) */
  auto_update?: boolean;
  /** Layout options */
  layout?: {
    columns?: number;
    showLayerNames?: boolean;
  };
  /** Typography settings for different text roles */
  typography?: LegendTypographyConfig;
  /** Text overrides when auto_update is off (keyed by "title" or "layer_{id}" or "caption_{id}") */
  textOverrides?: Record<string, string>;
}

/**
 * Inline-editable text component. When editable=true, renders a contentEditable span.
 * On blur, calls onSave with the new text content.
 */
const EditableText: React.FC<{
  text: string;
  editable: boolean;
  onSave: (text: string) => void;
  sx?: Record<string, unknown>;
  variant?: "caption" | "subtitle2" | "body2";
  children?: React.ReactNode;
}> = ({ text, editable, onSave, sx, variant = "caption", children }) => {
  const shownText = cleanEditedText(text);
  const handleBlur = (e: React.FocusEvent<HTMLSpanElement>) => {
    const newText = cleanEditedText(e.currentTarget.textContent ?? "");
    if (newText !== shownText) {
      onSave(newText);
    }
  };

  return (
    <Typography
      variant={variant}
      className={editable ? "legend-editable-text" : undefined}
      sx={{
        ...sx,
        ...(editable && {
          cursor: "text",
          outline: "none",
          "&:hover": { backgroundColor: "rgba(0,0,0,0.04)" },
          "&:focus": { backgroundColor: "rgba(0,0,0,0.08)" },
        }),
      }}
      contentEditable={editable}
      suppressContentEditableWarning
      onBlur={editable ? handleBlur : undefined}>
      {children ?? shownText}
    </Typography>
  );
};

interface LegendElementRendererProps {
  element: ReportElement;
  projectLayers?: ProjectLayer[];
  mapElements?: ReportElement[];
  viewOnly?: boolean;
  /** Zoom level to scale content */
  zoom?: number;
  /** Callback for updating element config (needed for inline text editing) */
  onElementUpdate?: (elementId: string, config: Record<string, unknown>) => void;
}

/**
 * Legend Element Renderer for print reports
 *
 * Displays layer legends in a configurable multi-column layout.
 * Uses the same legend logic as ProjectLayerTree for consistent rendering.
 */
const LegendElementRenderer: React.FC<LegendElementRendererProps> = ({
  element,
  projectLayers = [],
  mapElements = [],
  viewOnly: _viewOnly = true,
  zoom = 1,
  onElementUpdate,
}) => {
  const { t } = useTranslation("common");
  // Extract legend config
  const config = element.config as LegendElementConfig;
  const titleText = config?.title?.text ?? "";
  const layoutConfig = config?.layout ?? { columns: 1, showLayerNames: true };
  const typography = config?.typography;
  const textOverrides = config?.textOverrides;

  // Auto-update: default true. When false, legend freezes at its current content.
  const autoUpdate = config?.auto_update !== false;

  // Whether inline editing is allowed (only when auto_update is off)
  const isEditable = !autoUpdate;

  // Save a text override
  const saveTextOverride = useCallback(
    (key: string, text: string) => {
      if (!onElementUpdate) return;
      const currentOverrides = config?.textOverrides ?? {};
      onElementUpdate(element.id, {
        ...element.config,
        textOverrides: {
          ...currentOverrides,
          [key]: text,
        },
      } as Record<string, unknown>);
    },
    [onElementUpdate, element.id, element.config, config?.textOverrides]
  );

  // Resolve layers dynamically based on map element binding and lock state
  const resolvedLayers = useMemo(() => {
    // Find connected map element (if any)
    const connectedMap = config?.mapElementId && mapElements.length > 0
      ? mapElements.find((m) => m.id === config.mapElementId)
      : null;

    // Determine which layer IDs to show
    let layerIds: number[] | null = null;
    let styleOverrides: Record<string, Record<string, unknown>> | null = null;

    if (connectedMap) {
      const mapConfig = connectedMap.config as Record<string, unknown> | undefined;
      const mapLockLayers = mapConfig?.lock_layers === true;
      const mapLockStyles = mapConfig?.lock_styles === true;
      const mapLockedIds = mapConfig?.locked_layer_ids as number[] | undefined;
      const mapLockedStyles = mapConfig?.locked_layer_styles as Record<string, Record<string, unknown>> | undefined;

      if (mapLockLayers && mapLockedIds) {
        // Map has locked layers - use those IDs
        layerIds = mapLockedIds;
        if (mapLockStyles && mapLockedStyles) {
          // Map also has locked styles - use frozen properties
          styleOverrides = mapLockedStyles;
        }
      } else if (connectedMap.map_config?.layers) {
        // Fallback to map_config.layers if available
        layerIds = connectedMap.map_config.layers;
      }
    }

    // Filter project layers
    let result: ProjectLayer[];
    if (layerIds) {
      result = projectLayers.filter((l) => layerIds!.includes(l.id));
    } else {
      // Show all visible layers with legend enabled
      result = projectLayers.filter((layer) => {
        const props = layer.properties as Record<string, unknown>;
        const isVisible = props.visibility !== false;
        const legendShow = (props.legend as { show?: boolean })?.show !== false;
        return isVisible && legendShow;
      });
    }

    // Apply style overrides if the connected map has locked styles
    if (styleOverrides) {
      result = result.map((layer) => {
        const frozenProps = styleOverrides![String(layer.id)];
        if (frozenProps) {
          return { ...layer, properties: frozenProps };
        }
        return layer;
      });
    }

    return result;
  }, [projectLayers, mapElements, config?.mapElementId]);

  // Freeze mechanism: when auto_update is off, keep showing the last resolved layers
  const frozenLayersRef = useRef<ProjectLayer[]>(resolvedLayers);
  useEffect(() => {
    if (autoUpdate) {
      // Auto-update is on: always keep frozen ref in sync
      frozenLayersRef.current = resolvedLayers;
    }
  }, [autoUpdate, resolvedLayers]);

  const filteredLayers = autoUpdate ? resolvedLayers : frozenLayersRef.current;

  // Limit columns to number of layers (no empty columns)
  const columns = Math.min(layoutConfig.columns || 1, filteredLayers.length || 1);

  return (
    <Box
      sx={{
        width: `${100 / zoom}%`,
        height: `${100 / zoom}%`,
        overflow: "hidden",
        p: 1,
        boxSizing: "border-box",
        transform: `scale(${zoom})`,
        transformOrigin: "top left",
      }}>
      {/* Title - only show if text is not empty */}
      {titleText && (
        <EditableText
          text={isEditable && textOverrides?.title ? textOverrides.title : titleText}
          editable={isEditable}
          onSave={(text) => saveTextOverride("title", text)}
          variant="subtitle2"
          sx={{
            mb: 1,
            ...typographyToSx(typography?.title, "title"),
          }}
        />
      )}

      {/* Legend content */}
      {filteredLayers.length === 0 ? (
        <Typography variant="caption" color="text.secondary">
          {t("no_layers_to_display")}
        </Typography>
      ) : (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: `repeat(${columns}, 1fr)`,
            gap: 1,
            overflow: "hidden",
          }}>
          {filteredLayers.map((layer) => (
            <LayerLegendItem
              key={layer.id}
              layer={layer}
              showLayerName={layoutConfig.showLayerNames !== false}
              typography={typography}
              editable={isEditable}
              textOverrides={textOverrides}
              onTextSave={saveTextOverride}
            />
          ))}
        </Box>
      )}
    </Box>
  );
};

/**
 * Individual layer legend item.
 * Mirrors the logic from ProjectLayerTree for deciding between
 * simple icon vs expanded LayerLegendPanel.
 */
interface LayerLegendItemProps {
  layer: ProjectLayer;
  showLayerName?: boolean;
  typography?: LegendTypographyConfig;
  editable?: boolean;
  textOverrides?: Record<string, string>;
  onTextSave?: (key: string, text: string) => void;
}


const LayerLegendItem: React.FC<LayerLegendItemProps> = ({
  layer,
  showLayerName = true,
  typography,
  editable = false,
  textOverrides,
  onTextSave,
}) => {
  const props = layer.properties as Record<string, unknown>;
  const geomType = layer.type === "feature"
    ? (layer.feature_layer_geometry_type || "polygon")
    : layer.type === "raster"
      ? "raster"
      : "polygon";

  // Same check as ProjectLayerTree line 756
  const hasComplexLegend = !!(
    (props.filled !== false && props.color_field) ||
    (props.stroked !== false && props.stroke_color_field) ||
    props.marker_field
  );

  // Raster legend check
  const rasterStyle = props.style as { style_type?: string; categories?: unknown[]; color_map?: unknown[] } | undefined;
  const hasRasterLegend =
    layer.type === "raster" &&
    rasterStyle &&
    ((rasterStyle.style_type === "categories" && Array.isArray(rasterStyle.categories) && rasterStyle.categories.length > 0) ||
      (rasterStyle.style_type === "color_range" && Array.isArray(rasterStyle.color_map) && rasterStyle.color_map.length > 0));

  // Simple icon props (same logic as ProjectLayerTree lines 813-842)
  const baseColor: string = props.color
    ? Array.isArray(props.color) && (props.color as number[]).length >= 3
      ? rgbToHex(props.color as RGBColor)
      : Array.isArray(props.color)
        ? `rgb(${(props.color as number[]).join(",")})`
        : String(props.color)
    : "#ccc";
  const stroked = props.stroked !== false;
  const strokeColor: string | undefined = stroked && props.stroke_color
    ? Array.isArray(props.stroke_color) && (props.stroke_color as number[]).length >= 3
      ? rgbToHex(props.stroke_color as RGBColor)
      : Array.isArray(props.stroke_color)
        ? `rgb(${(props.stroke_color as number[]).join(",")})`
        : String(props.stroke_color)
    : undefined;

  return (
    <Box sx={{ minWidth: 0 }}>
      {/* Layer name with icon */}
      {showLayerName && (() => {
        const isComplex = hasComplexLegend || hasRasterLegend;
        const layerNameKey = `layer_${layer.id}`;
        const layerNameCleared = editable && textOverrides?.[layerNameKey] != null && !textOverrides[layerNameKey].trim();
        // Hide the layer name row entirely when user has cleared the text
        if (layerNameCleared) return null;
        return (
        <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mb: 0.5 }}>
          {!isComplex && (
            <Box sx={{ flexShrink: 0 }}>
              <LayerIcon
                type={geomType}
                color={baseColor}
                strokeColor={strokeColor}
                filled={props.filled !== false}
                iconUrl={
                  !props.marker_field && props.custom_marker && (props.marker as Record<string, unknown>)?.url
                    ? ((props.marker as Record<string, unknown>).url as string)
                    : undefined
                }
                iconSource={
                  !props.marker_field && props.custom_marker && (props.marker as Record<string, unknown>)?.source
                    ? ((props.marker as Record<string, unknown>).source as "custom" | "library")
                    : "library"
                }
              />
            </Box>
          )}
          <EditableText
            text={editable && textOverrides?.[`layer_${layer.id}`] ? textOverrides[`layer_${layer.id}`] : layer.name}
            editable={editable}
            onSave={(text) => onTextSave?.(`layer_${layer.id}`, text)}
            variant="caption"
            sx={{
              wordBreak: "break-word",
              ...typographyToSx(typography?.layerName, "layerName"),
            }}
          />
        </Stack>
        );
      })()}

      {/* Legend caption */}
      {!!(props.legend && (props.legend as Record<string, unknown>).caption) && (
        <EditableText
          text={
            editable && textOverrides?.[`caption_${layer.id}`]
              ? textOverrides[`caption_${layer.id}`]
              : String((props.legend as Record<string, unknown>).caption)
          }
          editable={editable}
          onSave={(text) => onTextSave?.(`caption_${layer.id}`, text)}
          variant="caption"
          sx={{ display: "block", mb: 0.5, ...typographyToSx(typography?.caption, "caption") }}
        />
      )}

      {/* Complex feature legend - attribute-based styling (compact/inline) */}
      {hasComplexLegend && layer.type === "feature" && (
        <LayerLegendPanel
          properties={props}
          geometryType={geomType}
          itemTypographySx={typographyToSx(typography?.legendItem, "legendItem")}
          headingTypographySx={typographyToSx(typography?.heading, "heading")}
          compact
          editable={editable}
          textOverrides={editable ? extractPrefixedOverrides(textOverrides, `legenditem_${layer.id}_`) : undefined}
          onTextSave={editable ? (key, text) => onTextSave?.(`legenditem_${layer.id}_${key}`, text) : undefined}
        />
      )}

      {/* Raster legend */}
      {hasRasterLegend && (
        <LayerLegendPanel
          properties={props}
          geometryType="raster"
          itemTypographySx={typographyToSx(typography?.legendItem, "legendItem")}
          editable={editable}
          textOverrides={editable ? extractPrefixedOverrides(textOverrides, `legenditem_${layer.id}_`) : undefined}
          onTextSave={editable ? (key, text) => onTextSave?.(`legenditem_${layer.id}_${key}`, text) : undefined}
        />
      )}

      {/* Raster legend URLs */}
      {layer.type === "raster" &&
        layer.other_properties?.legend_urls &&
        (layer.other_properties.legend_urls as string[]).map((url: string) => (
          <Stack key={url} spacing={1} sx={{ mt: 0.5 }} direction="column">
            <img src={url} alt="" style={{ width: "100%" }} />
          </Stack>
        ))}
    </Box>
  );
};

export default LegendElementRenderer;
