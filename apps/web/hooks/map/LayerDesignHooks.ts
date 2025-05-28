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
        value: SymbolPlacementAnchor.Enum.center,
        label: t("label_point_anchor_options.center"),
      },
      {
        value: SymbolPlacementAnchor.Enum.top,
        label: t("label_point_anchor_options.top"),
      },
      {
        value: SymbolPlacementAnchor.Enum.bottom,
        label: t("label_point_anchor_options.bottom"),
      },
      {
        value: SymbolPlacementAnchor.Enum.left,
        label: t("label_point_anchor_options.left"),
      },
      {
        value: SymbolPlacementAnchor.Enum.right,
        label: t("label_point_anchor_options.right"),
      },
      {
        value: SymbolPlacementAnchor.Enum["top-left"],
        label: t("label_point_anchor_options.top_left"),
      },
      {
        value: SymbolPlacementAnchor.Enum["top-right"],
        label: t("label_point_anchor_options.top_right"),
      },
      {
        value: SymbolPlacementAnchor.Enum["bottom-left"],
        label: t("label_point_anchor_options.bottom_left"),
      },
      {
        value: SymbolPlacementAnchor.Enum["bottom-right"],
        label: t("label_point_anchor_options.bottom_right"),
      },
    ];

    const lineAnchorOptions = [
      {
        value: SymbolPlacementAnchor.Enum.center,
        label: t("label_line_anchor_options.center"),
      },
      {
        value: SymbolPlacementAnchor.Enum.top,
        label: t("label_line_anchor_options.above"),
      },
      {
        value: SymbolPlacementAnchor.Enum.bottom,
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
