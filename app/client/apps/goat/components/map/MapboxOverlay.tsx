import { DataType } from "@/types/map/common";
import type {
  GroupedLayer,
  LayerProps,
  MapboxOverlayProps,
  SourceProps,
} from "@/types/map/layers";
import { Layer, Source } from "react-map-gl";

export function groupBySource(
  layers: (SourceProps & LayerProps)[]
): GroupedLayer[] {
  const groupedLayers = layers.reduce((acc, layer) => {
    const { url, data_type, data_source_name, data_reference_year, ...rest } =
      layer;
    const existingGroup = acc.find(
      (group) => group.url === url && group.data_type === data_type
    );
    if (existingGroup) {
      existingGroup.layers.push(rest);
    } else {
      acc.push({
        url,
        data_type,
        data_source_name,
        data_reference_year,
        layers: [rest],
      });
    }
    return acc;
  }, [] as GroupedLayer[]);
  return groupedLayers;
}

export default function MapboxOverlay({ layers }: MapboxOverlayProps) {
  const groupedLayers = groupBySource(layers);
  const overlays = groupedLayers.map((group) => {
    const {
      url,
      data_type,
      data_source_name: _data_source_name,
      data_reference_year: _data_reference_year,
      layers,
    } = group;
    if (data_type === DataType.mvt) {
      return (
        <Source key={url} type="vector" tiles={[url]}>
          {layers.map((layer) => (
            <Layer key={layer.id} {...layer.style} id={layer.id} />
          ))}
        </Source>
      );
    } else if (data_type === DataType.geojson) {
      return (
        <Source key={url} type="geojson" data={url}>
          {layers.map((layer) => (
            <Layer key={layer.id} {...layer.style} id={layer.id} />
          ))}
        </Source>
      );
    } else {
      return null;
    }
  });
  return <>{overlays}</>;
}
