import type { GeoJSONFeatureCollection } from "ol/format/GeoJSON.js";
import GeoJSON from "ol/format/GeoJSON.js";
import WFS from "ol/format/WFS.js";

type WFSVersion = "1.0.0" | "1.1.0" | "2.0.0";

/**
 * Class to handle WFS data transformation.
 */

class WFSTransformer {
  private baseUrl: string;
  private version: WFSVersion;
  private typeNames: string;
  private srsName: string;

  /**
   * Constructor to initialize the WFSTransformer.
   * @param baseUrl - The base URL of the WFS service.
   * @param version - The WFS version to use.
   * @param typeNames - The type names to request.
   * @param srsName - The spatial reference system name.
   */

  constructor(baseUrl: string, version: WFSVersion = '1.1.0', typeNames: string, srsName: string = 'urn:ogc:def:crs:EPSG::4326') {
    this.baseUrl = baseUrl;
    this.version = version;
    this.typeNames = typeNames;
    this.srsName = srsName;
  }

  /**
   * Fetches WFS data and transforms it to GeoJSON.
   * @returns A promise that resolves to a GeoJSONFeatureCollection or null if an error occurs.
   */
  public async fetchAndTransform(): Promise<GeoJSONFeatureCollection | null> {
    const wfsUrl = `${this.baseUrl}?service=WFS&version=${this.version}&request=GetFeature&typeNames=${this.typeNames}&srsName=${this.srsName}`;
    try {
      const response = await fetch(wfsUrl);
      const data = await response.text();
      const wfsFormat = new WFS({ version: this.version });
      const geojsonFormat = new GeoJSON();
      const features = wfsFormat.readFeatures(data, {
        dataProjection: this.srsName,
      });
      const geojson = geojsonFormat.writeFeaturesObject(features);
      return geojson
    } catch (error) {
      console.error("Error fetching WFS layer data", error);
      return null;
    }
  }

  /**
   * Static method to get the WFS version from a URL.
   * @param url - The URL to parse.
   * @param defaultVersion - The default version to return if none is found.
   * @returns The WFS version.
   */
  static getWFSVersion(url: string, defaultVersion: WFSVersion = '1.1.0'): WFSVersion {
    try {
      const parsedUrl = new URL(url);
      const params = new URLSearchParams(parsedUrl.search);
      const version = params.get('VERSION') || params.get('version');
      if (version === '1.0.0' || version === '1.1.0' || version === '2.0.0') {
        return version;
      } else {
        return defaultVersion;
      }
    } catch (error) {
      console.error("Invalid URL", error);
      return defaultVersion;
    }
  }

}

export default WFSTransformer;
