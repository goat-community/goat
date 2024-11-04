import { encodeSync, parseSync } from "@loaders.gl/core";
import { WKTLoader } from "@loaders.gl/wkt";
import { WKTWriter } from "@loaders.gl/wkt";




/**
 * Converts a WKT string to GeoJSON
 * @param wkt
 * @returns Array of GeoJSON objects
 */
export function wktToGeoJSON(wkt: string) {
  const geojson = parseSync(wkt, WKTLoader);
  return geojson;
}

/**
 * Converts a GeoJSON object to WKT
 * @param geojson
 * @returns Array of GeoJSON objects
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function geoJSONToWKT(geojson: any) {
  const wkt = encodeSync(geojson, WKTWriter);
  return wkt;
}


/**
 * Stringifies a GeoJSON object into WKT
 * @param geoJSON
 * @returns WKT string
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function stringify(geoJSON: any) {
  if (geoJSON.type === 'Feature') {
    geoJSON = geoJSON.geometry;
  }

  function pairWKT(c) {
    return c.join(' ');
  }

  function ringWKT(r) {
    return r.map(pairWKT).join(', ');
  }

  function ringsWKT(r) {
    return r.map(ringWKT).map(wrapParens).join(', ');
  }

  function multiRingsWKT(r) {
    return r.map(ringsWKT).map(wrapParens).join(', ');
  }

  function wrapParens(s) { return '(' + s + ')'; }

  const gJ = geoJSON;
  switch (gJ.type) {
    case 'Point':
      if (gJ.coordinates && gJ.coordinates.length === 3)
        return 'POINT Z (' + pairWKT(gJ.coordinates) + ')';
      else return 'POINT (' + pairWKT(gJ.coordinates) + ')';

    case 'LineString':
      if (gJ.coordinates && gJ.coordinates[0] && gJ.coordinates[0].length === 3)
        return 'LINESTRING Z (' + ringWKT(gJ.coordinates) + ')';
      else return 'LINESTRING (' + ringWKT(gJ.coordinates) + ')';

    case 'Polygon':
      if (gJ.coordinates && gJ.coordinates[0] && gJ.coordinates[0][0] && gJ.coordinates[0][0].length === 3)
        return 'POLYGON Z (' + ringsWKT(gJ.coordinates) + ')';
      else return 'POLYGON (' + ringsWKT(gJ.coordinates) + ')';

    case 'MultiPoint':
      if (gJ.coordinates && gJ.coordinates[0] && gJ.coordinates[0].length === 3)
        return 'MULTIPOINT Z (' + ringWKT(gJ.coordinates) + ')';
      else return 'MULTIPOINT (' + ringWKT(gJ.coordinates) + ')';

    case 'MultiLineString':
      if (gJ.coordinates && gJ.coordinates[0] && gJ.coordinates[0][0] && gJ.coordinates[0][0].length === 3)
        return 'MULTILINESTRING Z (' + ringsWKT(gJ.coordinates) + ')';
      else return 'MULTILINESTRING (' + ringsWKT(gJ.coordinates) + ')';

    case 'MultiPolygon':
      if (gJ.coordinates && gJ.coordinates[0] && gJ.coordinates[0][0] && gJ.coordinates[0][0] && gJ.coordinates[0][0][0].length === 3)
        return 'MULTIPOLYGON Z (' + multiRingsWKT(gJ.coordinates) + ')';
      else return 'MULTIPOLYGON (' + multiRingsWKT(gJ.coordinates) + ')';


    case 'GeometryCollection':
      return 'GEOMETRYCOLLECTION (' + gJ.geometries.map(stringify).join(', ') + ')';

    default:
      throw new Error('stringify requires a valid GeoJSON Feature or geometry object as input');
  }
};

export const globalExtent = 'POLYGON((-180 -90, 180 -90, 180 90, -180 90, -180 -90))';

