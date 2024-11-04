export type GeoJSONPolygon = {
  type: "Feature";
  properties: object;
  geometry: {
    type: "Polygon";
    coordinates: number[][][];
  };
};

export type GeoJSONMultiPolygon = {
  type: "Feature";
  properties: object;
  geometry: {
    type: "MultiPolygon";
    coordinates: number[][][][];
  };
};

export type GeoJSONFeature = GeoJSONPolygon | GeoJSONMultiPolygon;

export type GeoJSONFeatureCollection = {
  type: "FeatureCollection";
  features: GeoJSONFeature[];
};

function createMask(featureCollection: GeoJSONFeatureCollection): GeoJSONFeature {
  const worldPolygon = [
    [-180, -90],
    [180, -90],
    [180, 90],
    [-180, 90],
    [-180, -90],
  ];

  const maskCoordinates = [worldPolygon];

  featureCollection.features.forEach((feature) => {
    if (feature.geometry.type === "Polygon") {
      maskCoordinates.push(feature.geometry.coordinates[0]);
    } else if (feature.geometry.type === "MultiPolygon") {
      feature.geometry.coordinates.forEach((polygon) => {
        maskCoordinates.push(polygon[0]);
      });
    }
  });

  return {
    type: "Feature",
    properties: {},
    geometry: {
      type: "Polygon",
      coordinates: maskCoordinates,
    },
  };
}

export default createMask;
