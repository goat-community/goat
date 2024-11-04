import bbox from "@turf/bbox";
import type { MapRef } from "react-map-gl/maplibre";

import { wktToGeoJSON } from "@/lib/utils/map/wkt";

export function zoomToLayer(map: MapRef, wkt_extent: string) {
  const geojson = wktToGeoJSON(wkt_extent);
  const boundingBox = bbox(geojson);
  fitBounds(map, boundingBox as [number, number, number, number]);
}

export function fitBounds(map: MapRef, bounds: [number, number, number, number], padding = 40, maxZoom = 18) {
  map.fitBounds(bounds, {
    padding: padding,
    maxZoom: maxZoom,
    duration: 1000,
  });
}
