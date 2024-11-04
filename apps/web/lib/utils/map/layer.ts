import type { FeatureLayerPointProperties, Layer } from "@/lib/validations/layer";
import type { ProjectLayer } from "@/lib/validations/project";

export const getLayerKey = (layer: ProjectLayer | Layer) => {
  let id = layer.id.toString();
  if (layer.type === "feature") {
    const geometry_type = layer.feature_layer_geometry_type;
    if (geometry_type === "point") {
      const pointFeature = layer.properties as FeatureLayerPointProperties;
      const renderAs =
        pointFeature.custom_marker && (pointFeature.marker?.name || pointFeature.marker_field)
          ? "marker"
          : "circle";
      id = `${id}-${renderAs}`;
    }
  }
  return id;
};


