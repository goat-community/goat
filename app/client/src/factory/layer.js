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
import { OlStyleFactory } from "./OlStyle";
import { baseStyleDefs } from "../style/OlStyleDefs";

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
    } else if (lConf.type === "VECTORIMAGE") {
      return this.createVectorImageLayer(lConf);
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
      type: lConf.type,
      title: lConf.title,
      canEdit: lConf.canEdit,
      canModifyGeom: lConf.canModifyGeom,
      editDataType: lConf.editDataType,
      editGeometry: lConf.editGeometry,
      modifyAttributes: lConf.modifyAttributes,
      lid: lConf.lid,
      displayInLayerList: lConf.displayInLayerList,
      displayInLegend: lConf.displayInLegend,
      legendGraphicUrl: lConf.legendGraphicUrl,
      group: lConf.group,
      visible: lConf.visible,
      opacity: lConf.opacity,
      queryable: lConf.queryable,
      requiresPois: lConf.requiresPois,
      requiresAois: lConf.requiresAois,
      ratio: lConf.ratio ? lConf.ratio : 1.5,
      zIndex: lConf.zIndex,
      docUrl: lConf.docUrl,
      styles: lConf.styles,
      viewparamsDynamicKeys: lConf.viewparamsDynamicKeys,
      source: new ImageWMS({
        url: lConf.url,
        params: {
          LAYERS: lConf.layers,
          viewparams: lConf.viewparams,
          STYLES:
            lConf.styles && lConf.styles.default ? lConf.styles.default : ""
        },
        serverType: lConf.serverType ? lConf.serverType : "geoserver",
        ratio: lConf.ratio,
        attributions: lConf.attributions,
        crossOrigin: "Anonymous"
      }),
      minResolution: lConf.minResolution,
      maxResolution: lConf.maxResolution,
      minZoom: lConf.minZoom,
      maxZoom: lConf.maxZoom,
      otherProps: lConf.otherProps
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
      group: lConf.group,
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
        serverType: lConf.serverType ? lConf.serverType : "geoserver",
        attributions: lConf.attributions,
        crossOrigin: "Anonymous"
      }),
      minResolution: lConf.minResolution,
      maxResolution: lConf.maxResolution,
      minZoom: lConf.minZoom,
      maxZoom: lConf.maxZoom
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
      group: lConf.group,
      visible: lConf.visible,
      opacity: lConf.opacity,
      zIndex: lConf.zIndex,
      source: new XyzSource({
        url: lConf.hasOwnProperty("accessToken")
          ? lConf.url + "?access_token=" + lConf.accessToken
          : lConf.url,
        maxZoom: lConf.maxZoom,
        attributions: lConf.attributions,
        crossOrigin: "Anonymous"
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
      group: lConf.group,
      source: new OsmSource({
        url: lConf.url,
        maxZoom: lConf.maxZoom,
        crossOrigin: "Anonymous"
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
      maxZoom: lConf.maxZoom,
      crossOrigin: "Anonymous"
    });
    const layer = new TileLayer({
      name: lConf.name,
      title: lConf.title,
      lid: lConf.lid,
      cascadePrint: lConf.cascadePrint,
      displayInLayerList: lConf.displayInLayerList,
      visible: lConf.visible,
      opacity: lConf.opacity,
      group: lConf.group,
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
    const sourceOpts = {
      format: this.formatMapping[lConf.format]
        ? new this.formatMapping[lConf.format](lConf.formatConfig)
        : GeoJsonFormat(),
      attributions: lConf.attributions,
      crossOrigin: "Anonymous"
    };

    lConf.url ? (sourceOpts.url = lConf.url) : lConf.url;
    const vectorLayer = new VectorImageLayer({
      name: lConf.name,
      title: lConf.title,
      type: lConf.type,
      canEdit: lConf.canEdit,
      canModifyGeom: lConf.canModifyGeom,
      editDataType: lConf.editDataType,
      editGeometry: lConf.editGeometry,
      modifyAttributes: lConf.modifyAttributes,
      requiresPois: lConf.requiresPois,
      requiresAois: lConf.requiresAois,
      queryable: lConf.queryable,
      displayInLegend: lConf.displayInLegend,
      legendGraphicUrl: lConf.legendGraphicUrl,
      docUrl: lConf.docUrl,
      lid: lConf.lid,
      displayInLayerList: lConf.displayInLayerList,
      extent: lConf.extent,
      visible: lConf.visible,
      opacity: lConf.opacity,
      zIndex: lConf.zIndex,
      queryParams: lConf.queryParams,
      styleConf: lConf.style,
      source: new VectorSource(sourceOpts),
      format: lConf.format,
      url: lConf.url,
      group: lConf.group,
      concurrentRequests: lConf.concurrentRequests,
      style:
        OlStyleFactory.getInstance(lConf.style) ||
        baseStyleDefs[lConf.styleRef],
      hoverable: lConf.hoverable,
      hoverAttribute: lConf.hoverAttribute,
      minResolution: lConf.minResolution,
      maxResolution: lConf.maxResolution,
      minZoom: lConf.minZoom,
      maxZoom: lConf.maxZoom,
      otherProps: lConf.otherProps
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
      type: lConf.type,
      canEdit: lConf.canEdit,
      canModifyGeom: lConf.canModifyGeom,
      editDataType: lConf.editDataType,
      editGeometry: lConf.editGeometry,
      modifyAttributes: lConf.modifyAttributes,
      queryable: lConf.queryable,
      requiresPois: lConf.requiresPois,
      requiresAois: lConf.requiresAois,
      docUrl: lConf.docUrl,
      lid: lConf.lid,
      displayInLegend: lConf.displayInLegend,
      legendGraphicUrl: lConf.legendGraphicUrl,
      displayInLayerList: lConf.displayInLayerList,
      visible: lConf.visible,
      opacity: lConf.opacity,
      queryParams: lConf.queryParams,
      styleConf: lConf.style,
      zIndex: lConf.zIndex,
      url: lConf.url,
      group: lConf.group,
      concurrentRequests: lConf.concurrentRequests,
      source: new VectorTileSource({
        url: lConf.url,
        format: new this.formatMapping[lConf.format](),
        attributions: lConf.attributions,
        crossOrigin: "Anonymous"
      }),
      hoverable: lConf.hoverable,
      hoverAttribute: lConf.hoverAttribute,
      minResolution: lConf.minResolution,
      maxResolution: lConf.maxResolution,
      minZoom: lConf.minZoom,
      maxZoom: lConf.maxZoom,
      otherProps: lConf.otherProps
    });

    return vtLayer;
  }
};
