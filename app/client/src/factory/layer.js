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
import VectorLayer from "ol/layer/Vector";
import VectorSource from "ol/source/Vector";
import ImageWMS from "ol/source/ImageWMS.js";
import { Image as ImageLayer } from "ol/layer.js";
import XyzSource from "ol/source/XYZ";
import { OlStyleFactory } from "./OlStyle";
import OlStyleDefs from "../style/OlStyleDefs";

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

  /**
   * Returns an OpenLayers layer instance due to given config.
   *
   * @param  {Object} lConf  Layer config object
   * @return {ol.layer.Base} OL layer instance
   */
  getInstance(lConf) {
    // apply LID (Layer ID) if not existant
    if (!lConf.lid) {
      var now = new Date();
      lConf.lid = now.getTime();
    }

    // create correct layer type
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
    } else if (lConf.type === "VECTORTILE") {
      return this.createVectorTileLayer(lConf);
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
      name: lConf.name,
      title: lConf.title,
      canEdit: lConf.canEdit,
      editDataType: lConf.editDataType,
      editGeometry: lConf.editGeometry,
      lid: lConf.lid,
      displayInLayerList: lConf.displayInLayerList,
      visible: lConf.visible,
      opacity: lConf.opacity,
      queryable: lConf.queryable,
      requiresPois: lConf.requiresPois,
      ratio: lConf.ratio ? lConf.ratio : 1.5,
      zIndex: lConf.zIndex,
      source: new ImageWMS({
        url: lConf.url,
        params: {
          LAYERS: lConf.layers,
          viewparams: lConf.viewparams
        },
        serverType: lConf.serverType,
        ratio: lConf.ratio,
        attributions: lConf.attributions
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
      name: lConf.name,
      title: lConf.title,
      canEdit: lConf.canEdit,
      lid: lConf.lid,
      cascadePrint: lConf.cascadePrint,
      displayInLayerList: lConf.displayInLayerList,
      extent: lConf.extent,
      visible: lConf.visible,
      opacity: lConf.opacity,
      preload: lConf.preload ? parseFloat(lConf.preload) : 0, //Parse float is used because it's not possible to add values like Infinity in json config
      zIndex: lConf.zIndex,
      source: new TileWmsSource({
        url: lConf.url,
        params: {
          LAYERS: lConf.layers,
          TILED: lConf.tiled,
          viewparams: lConf.viewparams
        },
        serverType: lConf.serverType,
        attributions: lConf.attributions
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
    const xyzLayer = new TileLayer({
      name: lConf.name,
      title: lConf.title,
      lid: lConf.lid,
      cascadePrint: lConf.cascadePrint,
      displayInLayerList: lConf.displayInLayerList,
      visible: lConf.visible,
      opacity: lConf.opacity,
      source: new XyzSource({
        url: lConf.hasOwnProperty("accessToken")
          ? lConf.url + "?access_token=" + lConf.accessToken
          : lConf.url,
        maxZoom: lConf.maxZoom,
        attributions: lConf.attributions
      })
    });

    return xyzLayer;
  },

  /**
   * Returns an OpenLayers OSM layer instance due to given config.
   *
   * @param  {Object} lConf  Layer config object
   * @return {ol.layer.Tile} OL OSM layer instance
   */
  createOsmLayer(lConf) {
    const layer = new TileLayer({
      name: lConf.name,
      title: lConf.title,
      lid: lConf.lid,
      cascadePrint: lConf.cascadePrint,
      displayInLayerList: lConf.displayInLayerList,
      visible: lConf.visible,
      opacity: lConf.opacity,
      source: new OsmSource({
        url: lConf.url,
        maxZoom: lConf.maxZoom
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
    const bingMaps = new BingMaps({
      key: lConf.accessToken,
      imagerySet: lConf.imagerySet,
      maxZoom: lConf.maxZoom
    });
    const layer = new TileLayer({
      name: lConf.name,
      title: lConf.title,
      lid: lConf.lid,
      cascadePrint: lConf.cascadePrint,
      displayInLayerList: lConf.displayInLayerList,
      visible: lConf.visible,
      opacity: lConf.opacity,
      source: bingMaps
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
    const vectorLayer = new VectorLayer({
      name: lConf.name,
      title: lConf.title,
      canEdit: lConf.canEdit,
      lid: lConf.lid,
      displayInLayerList: lConf.displayInLayerList,
      extent: lConf.extent,
      visible: lConf.visible,
      opacity: lConf.opacity,
      zIndex: lConf.zIndex,
      source: new VectorSource({
        url: lConf.url,
        format: new this.formatMapping[lConf.format](lConf.formatConfig),
        attributions: lConf.attributions
      }),
      style:
        OlStyleFactory.getInstance(lConf.style) || OlStyleDefs[lConf.styleRef],
      hoverable: lConf.hoverable,
      hoverAttribute: lConf.hoverAttribute
    });

    return vectorLayer;
  },

  /**
   * Returns an OpenLayers vector tile layer instance due to given config.
   *
   * @param  {Object} lConf  Layer config object
   * @return {ol.layer.VectorTile} OL vector tile layer instance
   */
  createVectorTileLayer(lConf) {
    const vtLayer = new VectorTileLayer({
      name: lConf.name,
      title: lConf.title,
      canEdit: lConf.canEdit,
      lid: lConf.lid,
      displayInLayerList: lConf.displayInLayerList,
      visible: lConf.visible,
      opacity: lConf.opacity,
      source: new VectorTileSource({
        url: lConf.url,
        format: new this.formatMapping[lConf.format](),
        attributions: lConf.attributions
      }),
      style:
        OlStyleFactory.getInstance(lConf.style) || OlStyleDefs[lConf.styleRef],
      hoverable: lConf.hoverable,
      hoverAttribute: lConf.hoverAttribute
    });

    return vtLayer;
  }
};
