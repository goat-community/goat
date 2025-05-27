import { useMemo } from "react";
import { useTranslation } from "@/i18n/client";
import type { Layer } from "@/lib/validations/layer";
import { SymbolPlacementAnchor } from "@/lib/validations/layer";
import type { ProjectLayer } from "@/lib/validations/project";
import type { SelectorItem } from "@/types/map/common";

export function useSymbolOptions(layer: ProjectLayer | Layer) {
  const { t } = useTranslation("common");

  const anchorItems: SelectorItem[] = useMemo(() => {
    const pointAnchorOptions = [
      {
        value: SymbolPlacementAnchor.enum.center,
        label: t("label_point_anchor_options.center"),
      },
      {
        value: SymbolPlacementAnchor.enum.top,
        label: t("label_point_anchor_options.top"),
      },
      {
        value: SymbolPlacementAnchor.enum.bottom,
        label: t("label_point_anchor_options.bottom"),
      },
      {
        value: SymbolPlacementAnchor.enum.left,
        label: t("label_point_anchor_options.left"),
      },
      {
        value: SymbolPlacementAnchor.enum.right,
        label: t("label_point_anchor_options.right"),
      },
      {
        value: SymbolPlacementAnchor.enum["top-left"],
        label: t("label_point_anchor_options.top_left"),
      },
      {
        value: SymbolPlacementAnchor.enum["top-right"],
        label: t("label_point_anchor_options.top_right"),
      },
      {
        value: SymbolPlacementAnchor.enum["bottom-left"],
        label: t("label_point_anchor_options.bottom_left"),
      },
      {
        value: SymbolPlacementAnchor.enum["bottom-right"],
        label: t("label_point_anchor_options.bottom_right"),
      },
    ];

    const lineAnchorOptions = [
      {
        value: SymbolPlacementAnchor.enum.center,
        label: t("label_line_anchor_options.center"),
      },
      {
        value: SymbolPlacementAnchor.enum.top,
        label: t("label_line_anchor_options.above"),
      },
      {
        value: SymbolPlacementAnchor.enum.bottom,
        label: t("label_line_anchor_options.below"),
      },
    ];

    if (layer.feature_layer_geometry_type === "line") {
      return lineAnchorOptions;
    }

    return pointAnchorOptions;
  }, [t, layer.feature_layer_geometry_type]);

  return { anchorItems };
}
