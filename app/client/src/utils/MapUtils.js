import Projection from "ol/proj/Projection";
import TileGrid from "ol/tilegrid/TileGrid";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import Vector from "ol/source/Vector";
import GeoJSON from "ol/format/GeoJSON";
import { getTopLeft, getBottomLeft } from "ol/extent";
import WKT from "ol/format/WKT";
import { getArea } from "ol/sphere";
const geobuf = require("geobuf");
const Pbf = require("pbf");
import TurfBuffer from "@turf/buffer";

export function isWithinVisibleScales(scale, maxScale, minScale) {
  if (maxScale || minScale) {
    // Alter 1: maxscale and minscale
    if (maxScale && minScale) {
      if (scale > maxScale && scale < minScale) {
        return true;
      }
    } else if (maxScale) {
      // Alter 2: only maxscale
      if (scale > maxScale) {
        return true;
      }
    } else if (minScale) {
      // Alter 3: only minscale
      if (scale < minScale) {
        return true;
      }
    }
  } else {
    // Alter 4: no scale limit
    return true;
  }
  return false;
}

export function customProjection(projectionCode, extent) {
  return new Projection({
    code: projectionCode,
    extent
  });
}

export function tileGrid(settings, defaultSettings = {}) {
  const tileGridSettings = Object.assign({}, defaultSettings, settings);
  const extent = tileGridSettings.extent;
  tileGridSettings.origin =
    tileGridSettings.alignBottomLeft === false
      ? getTopLeft(extent)
      : getBottomLeft(extent);
  return new TileGrid(tileGridSettings);
}

export function checkZoomChange(resolution, currentResolution) {
  if (resolution !== currentResolution) {
    return true;
  }

  return false;
}

export function createPointFeature(coordinate, style) {
  const feature = new Feature({
    geometry: new Point(coordinate)
  });
  feature.setStyle(style);
  return feature;
}

export function geojsonToFeature(obj, options) {
  let featureObj = obj;
  while (Array.isArray(featureObj)) {
    featureObj = featureObj[0];
  }
  if (typeof obj === "string") {
    featureObj = JSON.parse(obj);
  } else if (!featureObj.features) {
    featureObj.features = [];
  }
  const vectorSource = new Vector({
    features: new GeoJSON().readFeatures(featureObj, options)
  });
  return vectorSource.getFeatures();
}

export function geobufToFeatures(obj, config) {
  const geojson = geobuf.decode(new Pbf(obj));
  return geojsonToFeature(geojson, config);
}

export function featuresToGeojson(features, featureProjection, dataProjection) {
  const options = { featureProjection };
  if (dataProjection) {
    options.dataProjection = dataProjection;
  }
  const format = new GeoJSON(options);
  const json = format.writeFeatures(features);
  return json;
}

export function geometryToWKT(geometry, featureProjection, dataProjection) {
  const options = { featureProjection };
  if (dataProjection) {
    options.dataProjection = dataProjection;
  }
  const format = new WKT(options);
  const wktGeom = format.writeGeometry(geometry);
  return wktGeom;
}

export function wktToFeature(wkt, srsName) {
  const format = new WKT();
  const feature = format.readFeature(wkt, {
    dataProjection: srsName,
    featureProjection: srsName
  });
  return feature;
}

export function getCenter(geometry) {
  const type = geometry.getType();
  let center;
  switch (type) {
    case "Polygon":
      center = geometry.getInteriorPoint().getCoordinates();
      break;
    case "MultiPolygon":
      center = geometry.getInteriorPoints().getFirstCoordinate();
      break;
    case "Point":
      center = geometry.getCoordinates();
      break;
    case "MultiPoint":
      center = geometry[0].getCoordinates();
      break;
    case "LineString":
      center = geometry.getCoordinateAt(0.5);
      break;
    case "MultiLineString":
      center = geometry.getLineStrings()[0].getCoordinateAt(0.5);
      break;
    case "Circle":
      center = geometry.getCenter();
      break;
    default:
      break;
  }
  return center;
}

export function OlBuffer(featureCollection, bufferDistance, units = "meters") {
  const buffer = TurfBuffer(featureCollection, bufferDistance, {
    units: units
  });
  return buffer;
}

export function getPolygonArea(polygon) {
  const type = polygon.getType();
  let output = "";
  if (type === "Polygon" || type === "MultiPolygon") {
    const area = getArea(polygon);
    output = `${Math.round((area / 1000000) * 100) / 100} km²`;
  }
  return output;
}

export function resolutionToScale(resolution, projection) {
  const dpi = 25.4 / 0.28;
  const mpu = projection.getMetersPerUnit();
  let scale = resolution * mpu * 39.37 * dpi;
  scale = Math.round(scale);
  return scale;
}

export function scaleToResolution(scale, projection) {
  const dpi = 25.4 / 0.28;
  const mpu = projection.getMetersPerUnit();
  const resolution = scale / (mpu * 39.37 * dpi);
  return resolution;
}

export function flyTo(destination, map, done) {
  const duration = 2000;
  const view = map.getView();
  const zoom = view.getZoom();
  let parts = 2;
  var called = false;
  function callback(complete) {
    --parts;
    if (called) {
      return;
    }
    if (parts === 0 || !complete) {
      called = true;
      done(complete);
    }
  }
  view.animate(
    {
      center: destination,
      duration: duration
    },
    callback
  );
  view.animate(
    {
      zoom: zoom - 1,
      duration: duration / 2
    },
    {
      zoom: zoom,
      duration: duration / 2
    },
    callback
  );
}

export function checkFeaturesEquality(feature1, feature2) {
  var formatWKT = new WKT();
  var feature1WKT = formatWKT.writeGeometry(feature1.getGeometry());
  var feature2WKT = formatWKT.writeGeometry(feature2.getGeometry());
  if (feature1WKT === feature2WKT) {
    return true;
  } else {
    return false;
  }
}
