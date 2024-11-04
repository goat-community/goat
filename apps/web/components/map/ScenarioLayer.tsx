import { useMemo } from "react";
import type { LayerProps } from "react-map-gl/maplibre";
import { Layer, Source } from "react-map-gl/maplibre";

import { scenarioFeatureStateColor, scenarioLayerStyleSpec } from "@/lib/transformers/layer";
import { getLayerKey } from "@/lib/utils/map/layer";
import type { ProjectLayer } from "@/lib/validations/project";
import type { ScenarioFeature, ScenarioFeatures } from "@/lib/validations/scenario";

type ScenarioLayerProps = {
  scenarioLayerData: ScenarioFeatures | undefined;
  projectLayers?: ProjectLayer[];
};

type ScenarioLayerFeatureMapping = {
  layer: ProjectLayer;
  features: ScenarioFeatures;
};

const ScenarioLayer = ({ scenarioLayerData, projectLayers }: ScenarioLayerProps) => {
  const layerWithScenarioData = useMemo(() => {
    const scenarioLayerFeatureMapping: ScenarioLayerFeatureMapping[] = [];
    if (!projectLayers || !scenarioLayerData) return scenarioLayerFeatureMapping;
    projectLayers.forEach((layer) => {
      const _features = [] as ScenarioFeature[];
      scenarioLayerData.features.forEach((feature) => {
        if (feature.properties?.layer_project_id === layer.id) {
          _features.push(feature);
        }
      });
      if (!_features.length) return;
      const _obj = {
        layer,
        features: {
          type: "FeatureCollection",
          features: _features,
        },
      } as ScenarioLayerFeatureMapping;
      scenarioLayerFeatureMapping.push(_obj);
    });

    return scenarioLayerFeatureMapping;
  }, [scenarioLayerData, projectLayers]);

  return (
    <>
      {/* SCEANRIO LAYER (Show the scenario layer on the map) */}
      {layerWithScenarioData?.length > 0 &&
        layerWithScenarioData.map((scenarioLayerMapping) => {
          const { layer, features } = scenarioLayerMapping;
          const highlightStyle = scenarioLayerStyleSpec(layer) as LayerProps;
          return (
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            <Source key={`source-scenario-layer-${layer.updated_at}`} type="geojson" data={features as any}>
              {highlightStyle && (
                <Layer
                  key={`scenario-layer-${getLayerKey(layer)}`}
                  id={`scenario-layer-${layer.id}`}
                  {...highlightStyle}
                />
              )}
              {/* Show the pattern layer for the scenario layer when the edit_type is "d" */}
              {layer.feature_layer_geometry_type === "polygon" && (
                <Layer
                  id={`highlight-scenario-pattern-layer-${layer.id}`}
                  type="fill"
                  paint={{
                    "fill-pattern": [
                      "case",
                      ["==", ["get", "edit_type"], "d"],
                      "goat-pattern-stripe-diagonal-left",
                      ["==", ["get", "edit_type"], "m"],
                      "goat-pattern-stripe-horizontal",
                      ["==", ["get", "edit_type"], "n"],
                      "goat-pattern-grid",
                      "",
                    ],
                    "fill-opacity": layer.properties.opacity,
                  }}
                  filter={["in", ["get", "edit_type"], ["literal", ["d", "m", "n"]]]}
                />
              )}

              {/* Show the circle background for point layers */}
              {layer.feature_layer_geometry_type === "point" && (
                <Layer
                  id={`highlight-scenario-point-layer-${layer.id}`}
                  type="circle"
                  beforeId={`scenario-layer-${layer.id}`}
                  paint={{
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    "circle-color": scenarioFeatureStateColor as any,
                    "circle-radius":
                      (layer.properties["custom_marker"]
                        ? layer.properties["marker_size"]
                        : layer.properties["radius"] || 5) + 10,
                    "circle-opacity": layer.properties.opacity,
                  }}
                  filter={["in", ["get", "edit_type"], ["literal", ["d", "m", "n"]]]}
                />
              )}
            </Source>
          );
        })}
    </>
  );
};

export default ScenarioLayer;
