import TileLayer from "ol/layer/Tile";
import TileWmsSource from "ol/source/TileWMS";
import OsmSource from "ol/source/OSM";
import BingMaps from "ol/source/BingMaps";
import VectorTileLayer from "ol/layer/VectorTile";
import VectorTileSource from "ol/source/VectorTile";
import MvtFormat from "ol/format/MVT";
import GeoJsonFormat from "ol/format/GeoJSON";
import TopoJsonFormat from "ol/format/TopoJSON";
import KmlFormat from "ol/format/KML";
import VectorSource from "ol/source/Vector";
import VectorImageLayer from "ol/layer/VectorImage";
import ImageWMS from "ol/source/ImageWMS.js";
import { Image as ImageLayer } from "ol/layer.js";
import XyzSource from "ol/source/XYZ";
import { OlStyleFactory } from "../factory/OlStyle";
import { all } from "ol/loadingstrategy";
import ApiService from "../services/api.service";
import { geobufToFeatures } from "../utils/MapUtils";
import appStore from "../store/modules/app";
import scenarioStore from "../store/modules/scenarios";
import poisAoisStore from "../store/modules/poisaois";
import mapStore from "../store/modules/map";
import axios from "axios";

/**
 * Factory, which creates OpenLayers layer instances according to a given config
 * object.
 */
export const LayerFactory = {
  /**
   * Maps the format literal of the config to the corresponding OL module.
   * @type {Object}
   */
  formatMapping: {
    MVT: MvtFormat,
    GeoJSON: GeoJsonFormat,
    TopoJSON: TopoJsonFormat,
    KML: KmlFormat
  },

  baseConf(lConf) {
    if (["heatmap", "basemap"].includes(lConf.group)) {
      lConf.queryable = false;
    }
    lConf.queryable = lConf.queryable === undefined ? true : lConf.queryable;

    let lOpts = {
      group: lConf.group,
      name: lConf.name,
      type: lConf.type,
      visible: lConf.visible || false,
      opacity: lConf.opacity || 1,
      showOptions: false,
      attributeDisplayStatusKey: 0,
      layerTreeKey: 0,
      layerOrderKey: 1,
      queryable: lConf.queryable,
      displayInLayerList: lConf.display_in_layer_list || true,
      legendGraphicUrls: lConf.legend_urls || null
    };
    if (lConf.min_resolution) {
      lOpts.minResolution = lConf.min_resolution;
    }
    if (lConf.max_resolution) {
      lOpts.maxResolution = lConf.max_resolution;
    }

    if (lConf.z_index) {
      lOpts.zIndex = lConf.z_index;
    }
    let sOpts = {
      url: lConf.url,
      crossOrigin: "Anonymous"
    };
    if (lConf.map_attribution) {
      sOpts.attributions = lConf.map_attribution;
    }
    return {
      lOpts,
      sOpts
    };
  },

  /**
   * Returns an OpenLayers layer instance due to given config.
   *
   * @param  {Object} lConf  Layer config object
   * @return {ol.layer.Base} OL layer instance
   */
  getInstance(lConf) {
    lConf.type = lConf.type.toUpperCase();
    if (lConf.group.toLowerCase() === "heatmap") {
      return this.createHeatmapLayer(lConf);
    }
    if (lConf.type === "WMS") {
      return this.createWmsLayer(lConf);
    } else if (lConf.type === "WMSTILE") {
      return this.createWmsTileLayer(lConf);
    } else if (lConf.type === "XYZ") {
      return this.createXyzLayer(lConf);
    } else if (lConf.type === "OSM") {
      return this.createOsmLayer(lConf);
    } else if (lConf.type === "BING") {
      return this.createBingLayer(lConf);
    } else if (lConf.type === "VECTOR") {
      return this.createVectorLayer(lConf);
    } else if (lConf.type === "VECTORIMAGE") {
      return this.createVectorImageLayer(lConf);
    } else if (["VECTORTILE", "MVT"].includes(lConf.type)) {
      return this.createVectorTileLayer(lConf);
    } else if (lConf.type === "GEOBUF") {
      return this.createGeoBufLayer(lConf);
    } else {
      return null;
    }
  },

  /**
   * Returns an OpenLayers WMS layer instance due to given config.
   *
   * @param  {Object} lConf  Layer config object
   * @return {ol.layer.Tile} OL WMS layer instance
   */
  createWmsLayer(lConf) {
    const layer = new ImageLayer({
      ...this.baseConf(lConf).lOpts,
      source: new ImageWMS({
        ...this.baseConf(lConf).sOpts
      })
    });
    return layer;
  },
  /**
   * Returns an OpenLayers WMS Tile layer instance due to given config.
   *
   * @param  {Object} lConf  Layer config object
   * @return {ol.layer.Tile} OL WMS layer instance
   */
  createWmsTileLayer(lConf) {
    const layer = new TileLayer({
      ...this.baseConf(lConf).lOpts,
      source: new TileWmsSource({
        ...this.baseConf(lConf).sOpts
      })
    });
    return layer;
  },

  /**
   * Returns an XYZ based tile layer instance due to given config.
   *
   * @param  {Object} lConf  Layer config object
   * @return {ol.layer.Tile} OL XYZ layer instance
   */
  createXyzLayer(lConf) {
    const layer = new TileLayer({
      ...this.baseConf(lConf).lOpts,
      maxZoom: lConf.max_zoom || 19,
      source: new XyzSource({
        ...this.baseConf(lConf).sOpts
      })
    });
    return layer;
  },

  /**
   * Returns an OpenLayers OSM layer instance due to given config.
   *
   * @param  {Object} lConf  Layer config object
   * @return {ol.layer.Tile} OL OSM layer instance
   */
  createOsmLayer(lConf) {
    const layer = new TileLayer({
      ...this.baseConf(lConf).lOpts,
      maxZoom: lConf.max_zoom || 19,
      source: new OsmSource({
        ...this.baseConf(lConf).sOpts
      })
    });

    return layer;
  },

  /**
   * Returns an OpenLayers BING layer instance due to given config.
   *
   * @param  {Object} lConf  Layer config object
   * @return {ol.layer.Tile} OL BING layer instance
   */
  createBingLayer(lConf) {
    const layer = new TileLayer({
      ...this.baseConf(lConf).lOpts,
      maxZoom: lConf.max_zoom || 19,
      source: new BingMaps({
        ...this.baseConf(lConf).sOpts,
        key: lConf.access_token,
        imagerySet: lConf.imagery_set
      })
    });

    return layer;
  },

  /**
   * Returns an OpenLayers vector layer instance due to given config.
   *
   * @param  {Object} lConf  Layer config object
   * @return {ol.layer.Vector} OL vector layer instance
   */
  createVectorLayer(lConf) {
    const layer = new VectorImageLayer({
      ...this.baseConf(lConf).lOpts,
      source: new VectorSource({
        ...this.baseConf(lConf).sOpts
      })
    });

    return layer;
  },

  /**
   * Returns an OpenLayers vector layer instance due to given config that uses a geobuf endpoint.
   *
   * @param  {Object} lConf  Layer config object
   * @return {ol.layer.Vector} OL vector layer instance
   */
  createGeoBufLayer(lConf) {
    const url =
      lConf.url || `/layers/vector/static/${lConf.name}?return_type=db_geobuf`;
    const layer = new VectorImageLayer({
      ...this.baseConf(lConf).lOpts,
      source: new VectorSource({
        ...this.baseConf(lConf).sOpts,
        // eslint-disable-next-line no-unused-vars
        loader: function(extent, resolution, projection, success, failure) {
          const proj = projection.getCode();
          const source = this;
          source.clear();
          ApiService.get_(url, {
            responseType: "arraybuffer",
            headers: {
              Accept: "application/pdf"
            }
          })
            .then(response => {
              if (response.data) {
                const olFeatures = geobufToFeatures(response.data, {
                  dataProjection: lConf.data_projection,
                  featureProjection: proj
                });
                source.addFeatures(olFeatures);
              }
            })
            .catch(({ response }) => {
              console.log(response);
            });
        },
        strategy: all
      })
    });
    this.styleVectorLayer(layer, lConf);
    return layer;
  },

  /**
   * Return heatmap layers
   * @param {Object} lConf
   * @returns {ol.layer.VectorImage} OlVector layer instance
   */

  createHeatmapLayer(lConf) {
    const layer = new VectorImageLayer({
      ...this.baseConf(lConf).lOpts,
      source: new VectorSource({
        ...this.baseConf(lConf).sOpts,
        // eslint-disable-next-line no-unused-vars
        loader: function(extent, resolution, projection, success, failure) {
          const proj = projection.getCode();
          const source = this;
          source.clear();
          const baseUrl_ = `heatmap`;
          const returnType = "db_geobuf";
          const modus = appStore.state.calculationMode.active;
          const activeScenario = scenarioStore.state.activeScenario;
          const scenarioId = `${
            activeScenario ? "&scenario_id=" + activeScenario : ""
          }`;
          const heatmapConfiguration = {};
          poisAoisStore.state.selectedPoisAois.forEach(poiAoiObject => {
            if (appStore.state.poiIcons[poiAoiObject.value]) {
              heatmapConfiguration[poiAoiObject.value] = {
                sensitivity: poiAoiObject.sensitivity,
                weight: poiAoiObject.weight || 1
              };
            }
          });
          const heatmapParams = {
            heatmap_connectivity: `${baseUrl_}/connectivity?return_type=${returnType}`,
            heatmap_population: `${baseUrl_}/population?modus=${modus}${scenarioId}&return_type=${returnType}`,
            heatmap_accessibility_population: `${baseUrl_}/local-accessibility?heatmap_type=heatmap_accessibility_population&heatmap_configuration=${JSON.stringify(
              heatmapConfiguration
            )}&modus=${modus}${scenarioId}&return_type=${returnType}`,
            heatmap_local_accessibility: `${baseUrl_}/local-accessibility?heatmap_type=heatmap_local_accessibility&heatmap_configuration=${JSON.stringify(
              heatmapConfiguration
            )}&modus=${modus}${scenarioId}&return_type=${returnType}`
          };
          const url = heatmapParams[lConf.name];
          mapStore.state.isMapBusy = true;
          const CancelToken = axios.CancelToken;
          ApiService.get_(url, {
            responseType: "arraybuffer",
            headers: {
              Accept: "application/pdf"
            },
            cancelToken: new CancelToken(c => {
              // An executor function receives a cancel function as a parameter
              mapStore.state.heatmapCancelToken = c;
            })
          })
            .then(response => {
              if (response.data) {
                const olFeatures = geobufToFeatures(response.data, {
                  dataProjection: lConf.data_projection,
                  featureProjection: proj
                });

                source.addFeatures(olFeatures);
              }
            })
            .catch(({ response }) => {
              console.log(response);
            })
            .finally(() => {
              mapStore.state.isMapBusy = false;
              mapStore.state.heatmapCancelToken = null;
            });
        },
        strategy: all
      })
    });
    this.styleVectorLayer(layer, lConf);
    return layer;
  },

  /**
   * Returns an OpenLayers vector tile layer instance due to given config.
   *
   * @param  {Object} lConf  Layer config object
   * @return {ol.layer.VectorTile} OL vector tile layer instance
   */
  createVectorTileLayer(lConf) {
    let url = lConf.url;
    if (!url) {
      lConf.url = `./layers/tiles/${lConf.name}/{z}/{x}/{y}.pbf`;
    }
    const layer = new VectorTileLayer({
      ...this.baseConf(lConf).lOpts,
      source: new VectorTileSource({
        ...this.baseConf(lConf).sOpts,
        format: new this.formatMapping[lConf.type || "MVT"](),
        tileLoadFunction: function(tile, url) {
          tile.setLoader(function(extent, resolution, projection) {
            ApiService.get_(url, {
              responseType: "arraybuffer",
              headers: {
                Accept: "application/pdf"
              }
            }).then(response => {
              if (response.data) {
                const format = tile.getFormat(); // ol/format/MVT configured as source format
                const features = format.readFeatures(response.data, {
                  extent: extent,
                  featureProjection: projection
                });
                tile.setFeatures(features);
              }
            });
          });
        }
      })
    });
    this.styleVectorLayer(layer, lConf);
    return layer;
  },

  /**
   * Styles the vector layer based on the layer config.
   *
   * @param  {ol.layer.Vector} layer Vector layer instance
   * @param  {Object} lConf  Layer config object
   * @return {ol.layer} OL vector layer instance
   */
  styleVectorLayer(layer, lConf) {
    // Style the vector tile layer
    let styleObj;
    if (typeof lConf.style === "object") {
      styleObj = {
        format: "geostyler",
        style: lConf.style
      };
    } else if (lConf.style === "custom") {
      styleObj = {
        format: "custom"
      };
    } else {
      return layer;
    }
    const olStyle = OlStyleFactory.getOlStyle(styleObj, lConf.name);
    if (olStyle) {
      if (olStyle instanceof Promise) {
        olStyle
          .then(style => {
            layer.setStyle(style);
          })
          .catch(error => {
            console.log(error);
            console.log("error", lConf.name);
          });
      } else {
        layer.setStyle(olStyle);
      }
    }
  }
};
