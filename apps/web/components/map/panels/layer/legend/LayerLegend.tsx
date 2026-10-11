import { Box, Stack, Typography } from "@mui/material";
import React from "react";
import { useTranslation } from "react-i18next";

import { cleanEditedText } from "@/lib/utils/editableText";
import { getLegendColorMap, getLegendMarkerMap } from "@/lib/utils/map/legend";
import type { RasterLayerProperties } from "@/lib/validations/layer";

import { LayerIcon } from "./LayerIcon";

interface LayerLegendPanelProps {
  properties: Record<string, unknown>;
  geometryType: string; // "point", "line", "polygon"
  /** Optional sx overrides for legend item label text */
  itemTypographySx?: Record<string, unknown>;
  /** Optional sx overrides for section heading text (field names) */
  headingTypographySx?: Record<string, unknown>;
  /** Whether text labels are inline-editable */
  editable?: boolean;
  /** Text overrides keyed by "item_{index}" */
  textOverrides?: Record<string, string>;
  /** Save callback for text overrides */
  onTextSave?: (key: string, text: string) => void;
  /** Compact mode: render items inline in a flow layout (for print legends) */
  compact?: boolean;
  /** Hide the attribute/field name headings while keeping color values */
  hideHeading?: boolean;
}

export const LayerLegendPanel = ({ properties, geometryType, itemTypographySx, headingTypographySx, editable, textOverrides, onTextSave, compact, hideHeading }: LayerLegendPanelProps) => {
  const { t } = useTranslation("common");

  // Container sx for sections — compact indents items under layer name
  const sectionSx = {
    pb: compact ? 0.5 : 1,
    pt: compact ? 0.25 : 0.5,
    ...(!compact && { pr: 2 }),
    ...(compact && { pl: 1.5 }),
  };

  // Editable heading helper
  const renderHeading = (defaultText: string, overrideKey: string) => {
    if (hideHeading) return null;
    const displayText =
      editable && textOverrides?.[overrideKey] != null
        ? cleanEditedText(textOverrides[overrideKey])
        : defaultText;
    // Hide heading entirely when user has cleared the text
    if (editable && textOverrides?.[overrideKey] != null && !displayText.trim()) {
      return null;
    }
    const handleBlur = (e: React.FocusEvent<HTMLSpanElement>) => {
      const newText = cleanEditedText(e.currentTarget.textContent ?? "");
      if (newText !== displayText) {
        onTextSave?.(overrideKey, newText);
      }
    };
    return (
      <Typography
        variant="caption"
        color="text.secondary"
        className={editable ? "legend-editable-text" : undefined}
        sx={{
          display: "block",
          mb: 0.5,
          ...headingTypographySx,
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
        {displayText}
      </Typography>
    );
  };

  // Check if this is a raster layer with styling
  const rasterProperties = properties as RasterLayerProperties;
  const rasterStyle = rasterProperties?.style;

  // 1. Raster Layer Legends
  if (rasterStyle) {
    return <RasterLayerLegend style={rasterStyle} itemTypographySx={itemTypographySx} editable={editable} textOverrides={textOverrides} onTextSave={onTextSave} />;
  }

  // 2. Feature Layer Legends
  // Compute Maps
  const colorMap = getLegendColorMap(properties, "color", t("no_data"));
  const strokeMap = getLegendColorMap(properties, "stroke_color", t("no_data"));
  const markerMap = getLegendMarkerMap(properties);

  // Track a running index for editable keys
  let rowIndex = 0;

  // 2. Helper to render a single legend row
  const renderRow = (label: string, iconNode: React.ReactNode) => {
    // Always consume an index, even for hidden rows — the keys are positional,
    // so skipping one would shift every later row's override onto its neighbour.
    const idx = rowIndex++;
    const overrideKey = `item_${idx}`;
    const displayLabel =
      editable && textOverrides?.[overrideKey] != null ? cleanEditedText(textOverrides[overrideKey]) : label;

    // Hide the row entirely when the user has cleared its label, so the icon
    // goes with it instead of lingering on its own.
    if (editable && textOverrides?.[overrideKey] != null && !displayLabel.trim()) {
      return null;
    }

    const handleBlur = (e: React.FocusEvent<HTMLSpanElement>) => {
      const newText = cleanEditedText(e.currentTarget.textContent ?? "");
      if (newText !== displayLabel) {
        onTextSave?.(overrideKey, newText);
      }
    };

    return (
      <Stack
        direction="row"
        alignItems="center"
        spacing={compact ? 0.5 : 1}
        sx={{ py: compact ? 0 : 0.5 }}>
        <Box sx={{ width: 20, height: 20, display: "flex", justifyContent: "center", alignItems: "center", flexShrink: 0 }}>
          {iconNode}
        </Box>
        <Typography
          variant="caption"
          className={editable ? "legend-editable-text" : undefined}
          sx={{
            lineHeight: 1.2,
            wordBreak: "break-word",
            ...itemTypographySx,
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
          {displayLabel}
        </Typography>
      </Stack>
    );
  };

  // --- RENDER LOGIC ---
  // Priority: Check if markers and colors represent the same attribute
  // If they do, show only the colored markers
  // If they don't, show both sections separately

  const markerFieldName = (properties.marker_field as { name?: string })?.name;
  const colorFieldName = (properties.color_field as { name?: string })?.name;
  const hasMatchingFields = markerFieldName && colorFieldName && markerFieldName === colorFieldName;

  // A. Custom Markers with matching color field - show colored markers only
  if (markerMap.length > 1 && geometryType === "point" && hasMatchingFields) {
    return (
      <Box sx={sectionSx}>
        {renderHeading(markerFieldName || t("legend"), "heading")}
        {markerMap.map((item, index) => (
          <React.Fragment key={`${item.marker}-${item.value?.join(",") || index}`}>
            {renderRow(
              item.value?.join(", ") || t("other"),
              <LayerIcon
                type="point"
                iconUrl={item.marker || ""}
                color={item.color || undefined}
                iconSource={item.source}
              />
            )}
          </React.Fragment>
        ))}
      </Box>
    );
  }

  // B. Custom Markers WITHOUT matching color field - show both sections
  if (markerMap.length > 1 && geometryType === "point" && !hasMatchingFields) {
    return (
      <Box sx={sectionSx}>
        {/* Icons section */}
        {renderHeading(markerFieldName ? t("icons_based_on", { field: markerFieldName }) : t("icons"), "heading_marker")}
        {markerMap.map((item, index) => (
          <React.Fragment key={`${item.marker}-${item.value?.join(",") || index}`}>
            {renderRow(
              item.value?.join(", ") || t("other"),
              <LayerIcon
                type="point"
                iconUrl={item.marker || ""}
                color={item.color || undefined}
                iconSource={item.source}
              />
            )}
          </React.Fragment>
        ))}

        {/* Fill color section if it exists */}
        {colorMap.length > 1 && (
          <>
            {renderHeading(t("fill_color_based_on", { field: colorFieldName || t("color") }), "heading_color")}
            {colorMap.map((item, index) => (
              <React.Fragment key={`${item.color}-${item.value?.join(",") || index}`}>
                {renderRow(item.label || item.value?.join(", ") || t("other"), <LayerIcon type="point" color={item.color} />)}
              </React.Fragment>
            ))}
          </>
        )}
      </Box>
    );
  }

  // C. Single marker with attribute-based colors - show icon in each color
  if (markerMap.length === 1 && geometryType === "point" && colorMap.length > 1) {
    const singleMarker = markerMap[0];
    return (
      <Box sx={sectionSx}>
        {/* Show the icon in each color instead of circles */}
        {renderHeading(colorFieldName || t("legend"), "heading")}
        {colorMap.map((item, index) => (
          <React.Fragment key={`${item.color}-${item.value?.join(",") || index}`}>
            {renderRow(
              item.label || item.value?.join(", ") || t("other"),
              <LayerIcon
                type="point"
                iconUrl={singleMarker.marker || ""}
                color={item.color}
                iconSource={singleMarker.source}
              />
            )}
          </React.Fragment>
        ))}
      </Box>
    );
  }

  // C2. Multiple markers only (no fill/stroke colors) - show markers without color section
  if (markerMap.length > 1 && geometryType === "point" && colorMap.length <= 1 && strokeMap.length <= 1) {
    return (
      <Box sx={sectionSx}>
        {renderHeading(markerFieldName ? t("icons_based_on", { field: markerFieldName }) : t("icons"), "heading_marker")}
        {markerMap.map((item, index) => (
          <React.Fragment key={`${item.marker}-${item.value?.join(",") || index}`}>
            {renderRow(
              item.value?.join(", ") || t("other"),
              <LayerIcon
                type="point"
                iconUrl={item.marker || ""}
                color={item.color || undefined}
                iconSource={item.source}
              />
            )}
          </React.Fragment>
        ))}
      </Box>
    );
  }

  // D. Attribute-based Colors (Fill) with or without stroke
  if (colorMap.length > 1) {
    // Check if stroke color is also attribute-based on a different field
    const strokeColorFieldName = (properties.stroke_color_field as { name?: string })?.name;
    const hasDifferentStrokeField = strokeColorFieldName && strokeColorFieldName !== colorFieldName;

    // Get stroke properties for proper rendering
    const stroked = properties.stroked !== false; // Default to true if not specified
    const strokeColor = properties.stroke_color
      ? Array.isArray(properties.stroke_color)
        ? `rgb(${(properties.stroke_color as number[]).join(",")})`
        : (properties.stroke_color as string)
      : undefined;
    const filled = properties.filled !== false; // Default to true if not specified

    // If both fill and stroke are attribute-based on different fields, show both sections
    if (hasDifferentStrokeField && strokeMap.length > 1) {
      return (
        <Box sx={sectionSx}>
          {/* Fill color section */}
          {renderHeading(t("fill_color_based_on", { field: colorFieldName || t("color") }), "heading_color")}
          {colorMap.map((item, index) => (
            <React.Fragment key={`fill-${item.color}-${item.value?.join(",") || index}`}>
              {renderRow(
                item.label || item.value?.join(", ") || t("other"),
                <LayerIcon type={geometryType} color={item.color} filled={filled} />
              )}
            </React.Fragment>
          ))}

          {/* Stroke color section */}
          {renderHeading(t("stroke_color_based_on", { field: strokeColorFieldName }), "heading_stroke")}
          {strokeMap.map((item, index) => (
            <React.Fragment key={`stroke-${item.color}-${item.value?.join(",") || index}`}>
              {renderRow(
                item.label || item.value?.join(", ") || t("other"),
                <LayerIcon type={geometryType} color={undefined} strokeColor={item.color} filled={false} />
              )}
            </React.Fragment>
          ))}
        </Box>
      );
    }

    // Otherwise, show fill color with stroke (classified if same field, static otherwise)
    const sameFieldStroke = strokeMap.length > 1;
    return (
      <Box sx={sectionSx}>
        {renderHeading(colorFieldName || t("legend"), "heading")}
        {colorMap.map((item, index) => (
          <React.Fragment key={`${item.color}-${item.value?.join(",") || index}`}>
            {renderRow(
              item.label || item.value?.join(", ") || t("other"),
              <LayerIcon
                type={geometryType}
                color={item.color}
                strokeColor={stroked ? (sameFieldStroke ? strokeMap[index]?.color : strokeColor) : undefined}
                filled={filled}
              />
            )}
          </React.Fragment>
        ))}
      </Box>
    );
  }

  // E. Attribute-based Stroke only (no fill color field)
  if (strokeMap.length > 1) {
    const filled = properties.filled !== false;
    const fillColor = properties.color
      ? Array.isArray(properties.color)
        ? `rgb(${(properties.color as number[]).join(",")})`
        : (properties.color as string)
      : undefined;
    return (
      <Box sx={sectionSx}>
        {renderHeading((properties.stroke_color_field as { name?: string })?.name || t("legend"), "heading")}
        {strokeMap.map((item, index) => (
          <React.Fragment key={`${item.color}-${item.value?.join(",") || index}`}>
            {renderRow(
              item.label || item.value?.join(", ") || t("other"),
              <LayerIcon type={geometryType} color={filled ? fillColor : undefined} strokeColor={item.color} filled={filled} />
            )}
          </React.Fragment>
        ))}
      </Box>
    );
  }

  // If no expanded legend is needed (Simple single-color layer),
  // usually we don't render anything here because the main Row Icon handles it.
  return null;
};

// Raster Layer Legend Component
interface RasterLayerLegendProps {
  style: RasterLayerProperties["style"];
  itemTypographySx?: Record<string, unknown>;
  editable?: boolean;
  textOverrides?: Record<string, string>;
  onTextSave?: (key: string, text: string) => void;
}

const RasterLayerLegend = ({ style, itemTypographySx, editable, textOverrides, onTextSave }: RasterLayerLegendProps) => {
  const { t } = useTranslation("common");
  if (!style) return null;

  let rowIndex = 0;

  // Helper to render a single legend row
  const renderRow = (label: string, color: string) => {
    // Always consume an index, even for hidden rows — see the feature-layer
    // renderRow above.
    const idx = rowIndex++;
    const overrideKey = `item_${idx}`;
    const displayLabel =
      editable && textOverrides?.[overrideKey] != null ? cleanEditedText(textOverrides[overrideKey]) : label;

    // Hide the row entirely when the user has cleared its label, so the colour
    // swatch goes with it.
    if (editable && textOverrides?.[overrideKey] != null && !displayLabel.trim()) {
      return null;
    }

    const handleBlur = (e: React.FocusEvent<HTMLSpanElement>) => {
      const newText = cleanEditedText(e.currentTarget.textContent ?? "");
      if (newText !== displayLabel) {
        onTextSave?.(overrideKey, newText);
      }
    };

    return (
      <Stack direction="row" alignItems="center" spacing={1} sx={{ py: 0.5 }}>
        <Box
          sx={{
            width: 20,
            height: 12,
            backgroundColor: color,
            border: "1px solid",
            borderColor: "divider",
            borderRadius: 0.5,
          }}
        />
        <Typography
          variant="caption"
          className={editable ? "legend-editable-text" : undefined}
          sx={{
            lineHeight: 1.2,
            ...itemTypographySx,
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
          {displayLabel}
        </Typography>
      </Stack>
    );
  };

  // 1. Categories Style
  if (style.style_type === "categories") {
    return (
      <Box sx={{ pb: 1, pr: 2, pt: 0.5 }}>
        {style.categories.map((cat) => (
          <React.Fragment key={`${cat.value}-${cat.color}`}>
            {renderRow(cat.label || t("value_n", { value: cat.value }), cat.color)}
          </React.Fragment>
        ))}
      </Box>
    );
  }

  // 2. Color Range Style
  if (style.style_type === "color_range" && style.color_map.length > 0) {
    const minLabelRaw =
      style.min_label || style.min_value?.toString() || style.color_map[0]?.[0]?.toString() || "Min";
    const maxLabelRaw =
      style.max_label ||
      style.max_value?.toString() ||
      style.color_map[style.color_map.length - 1]?.[0]?.toString() ||
      "Max";
    const minLabel =
      editable && textOverrides?.["item_min"] != null
        ? cleanEditedText(textOverrides["item_min"])
        : minLabelRaw;
    const maxLabel =
      editable && textOverrides?.["item_max"] != null
        ? cleanEditedText(textOverrides["item_max"])
        : maxLabelRaw;

    const editableSx = editable
      ? {
          cursor: "text" as const,
          outline: "none",
          "&:hover": { backgroundColor: "rgba(0,0,0,0.04)" },
          "&:focus": { backgroundColor: "rgba(0,0,0,0.08)" },
        }
      : {};

    return (
      <Box sx={{ pb: 1, pr: 2, pt: 3 }}>
        <Box
          sx={{
            width: "100%",
            height: 16,
            background: `linear-gradient(to right, ${style.color_map.map(([, color]) => color).join(", ")})`,
            borderRadius: 0.5,
            mb: 0.5,
          }}
        />
        <Stack direction="row" justifyContent="space-between">
          <Typography
            variant="caption"
            className={editable ? "legend-editable-text" : undefined}
            sx={{ color: "text.secondary", ...itemTypographySx, ...editableSx }}
            contentEditable={editable}
            suppressContentEditableWarning
            onBlur={editable ? (e) => {
              const t = cleanEditedText(e.currentTarget.textContent ?? "");
              if (t !== minLabel) onTextSave?.("item_min", t);
            } : undefined}>
            {minLabel}
          </Typography>
          <Typography
            variant="caption"
            className={editable ? "legend-editable-text" : undefined}
            sx={{ color: "text.secondary", ...itemTypographySx, ...editableSx }}
            contentEditable={editable}
            suppressContentEditableWarning
            onBlur={editable ? (e) => {
              const t = cleanEditedText(e.currentTarget.textContent ?? "");
              if (t !== maxLabel) onTextSave?.("item_max", t);
            } : undefined}>
            {maxLabel}
          </Typography>
        </Stack>
      </Box>
    );
  }

  // 3. Image/Hillshade Styles - No legend needed
  return null;
};
