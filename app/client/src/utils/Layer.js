import { Group as LayerGroup } from "ol/layer.js";
import olLayerLayer from "ol/layer/Layer.js";
import olLayerImage from "ol/layer/Image.js";
import olLayerVector from "ol/layer/Vector.js";

import { appendParams as olUriAppendParams } from "ol/uri.js";
import UrlUtil from "./Url";
import { geojsonToFeature } from "./MapUtils";
import http from "../services/http";
import store from "../store/index";

const geobuf = require("geobuf");
const Pbf = require("pbf");

/**
 * Util for OL layers
 */

/**
 * Returns a set of map layers which matches the given key value pair.
 *
 * @param {String} key - Key to filter layers
 * @param {Object} value - Value to filter layers
 * @param  {ol.Map} olMap  The OL map to search in
 * @return {ol.layer.Base[]} Array of matching layers
 */
export function getLayersBy(key, value, olMap) {
  if (!olMap) {
    return [];
  }

  let layerMatches = [];
  olMap.getLayers().forEach(function(layer) {
    if (layer.get(key) === value) {
      layerMatches.push(layer);
    }
  });

  return layerMatches;
}

/**
 * Returns OL Layer type.
 *
 * @param  {ol.layer.Base} Object OL layer
 */
export function getLayerType(layer) {
  let layerType;
  if (layer instanceof olLayerImage) {
    layerType = "WMS";
  } else if (layer instanceof olLayerVector) {
    layerType = "WFS";
  }
  return layerType;
}

/**
 * Returns a map layer with the given LID (Layer ID)
 *
 * @param  {String} lid    The LID of the layer to query
 * @param  {ol.Map} olMap  The OL map to search in
 * @return {ol.layer.Base} The OL layer instance or undefined
 */
export function getLayerByLid(lid, olMap) {
  return getLayersBy("lid", lid, olMap)[0];
}

/**
 * Returns all map layers excluding from group layer
 *
 * @param  {ol.Map} olMap  The OL map to search in
 * @return {ol.layer.Base[]} Array of all map layers
 */
export function getAllChildLayers(olMap) {
  const allLayers = [];
  olMap
    .getLayers()
    .getArray()
    .forEach(layer => {
      if (layer instanceof LayerGroup) {
        const layers = layer.getLayers().getArray();
        allLayers.push(...layers);
      } else {
        allLayers.push(layer);
      }
    });
  return allLayers;
}

/**
 * Zooms to the given layer's extent.
 * Will only work if the layer has kind of vector source.
 *
 * @param  {ol.layer.Base} vecLayer OL vector layer
 * @param  {ol.Map} olMap           The map to perform the zoom on
 */
export function zoomToLayerExtent(vecLayer, olMap) {
  if (!vecLayer || !vecLayer.getSource().getExtent || !olMap) {
    return;
  }
  const extent = vecLayer.getSource().getExtent();
  olMap.getView().fit(extent);
}

/**
 * Get an array of all layers in a group. The group can contain multiple levels
 * of others groups.
 * @param {import("ol/layer/Base.js").default} layer The base layer, mostly a group of layers.
 * @return {Array<import("ol/layer/Layer.js").default<import('ol/source/Source.js').default>>} Layers.
 */
export function getFlatLayers(layer) {
  if (layer instanceof LayerGroup) {
    const sublayers = /** @type {import("ol/layer/Layer.js").default<import('ol/source/Source.js').default>[]} */ (layer
      .getLayers()
      .getArray());
    const hasGroupLayer = sublayers.some(
      sublayer => sublayer instanceof LayerGroup
    );
    if (!hasGroupLayer) {
      return sublayers.slice();
    }
  }

  return getFlatLayers_(layer, [], undefined);
}

/**
 * Get an array of all layers in a group. The group can contain multiple levels
 * of others groups. When we flatten a group, we get the child layers.
 * If opacity is defined on the group, this value is lost.
 * Computed opacity is a custom 'back-up' value that contains
 * the calculated value of all ancestors and the given layer.
 * @param {import("ol/layer/Base.js").default} layer The base layer, mostly a group of layers.
 * @param {olLayerLayer<import('ol/source/Source.js').default>[]} array An array to add layers.
 * @param {number|undefined} computedOpacity Opacity inherited from ancestor layer groups.
 * @return {olLayerLayer<import('ol/source/Source.js').default>[]} Layers.
 * @private
 */
export function getFlatLayers_(layer, array, computedOpacity) {
  const opacity = layer.getOpacity();
  if (computedOpacity !== undefined) {
    computedOpacity *= opacity;
  } else {
    computedOpacity = opacity;
  }
  if (layer instanceof LayerGroup) {
    const sublayers = layer.getLayers();
    sublayers.forEach(l => {
      getFlatLayers_(l, array, computedOpacity);
    });
  } else if (layer instanceof olLayerLayer) {
    if (!array.includes(layer)) {
      layer.set("inheritedOpacity", computedOpacity, true);
      array.push(layer);
    }
  }
  return array;
}

/**
 * Gets teh active baselayer if there
 * is one activated otherwise it will return an empty array.
 * @param  {ol.Map} olMap           The map to perform the search on.
 * @return {Array<import("ol/layer/Layer.js").default<import('ol/source/Source.js').default>>} Layers.
 */

export function getActiveBaseLayer(map) {
  const activeBaselayer = map
    .getLayers()
    .getArray()
    .filter(groupLayer => {
      return groupLayer.get("name") === "backgroundLayers";
    })[0]
    .getLayers()
    .getArray()
    .filter(layer => {
      return layer.getVisible() === true;
    });
  return activeBaselayer;
}

/**
 * Get the WMS legend URL for the given node.
 * @param {string|undefined} url The base url of the wms service.
 * @param {string} layerName The name of a wms layer.
 * @param {number=} opt_scale A scale.
 * @param {string=} opt_legendRule rule parameters to add to the returned URL.
 * @param {number=} opt_legendWidth the legend width.
 * @param {number=} opt_legendHeight the legend height.
 * @param {string=} opt_servertype the OpenLayers server type.
 * @param {number=} opt_dpi the DPI.
 * @param {number[]=} opt_bbox the bbox.
 * @param {string=} opt_srs The projection code.
 * @param {Object<string, string>=} opt_additionalQueryString Additional query string parameters.
 * @return {string|undefined} The legend URL or undefined.
 */
export function getWMSLegendURL(
  url,
  layerName,
  opt_scale,
  opt_legendRule,
  opt_legendWidth,
  opt_legendHeight,
  opt_servertype,
  opt_dpi,
  opt_bbox,
  opt_srs,
  opt_additionalQueryString,
  opt_language,
  opt_style
) {
  if (!url) {
    return undefined;
  }
  /** @type {Object<string, string|boolean|number>} */
  const queryString = {
    FORMAT: "image/png",
    TRANSPARENT: true,
    SERVICE: "WMS",
    VERSION: "1.1.1",
    REQUEST: "GetLegendGraphic",
    LAYER: layerName
  };
  if (opt_scale !== undefined) {
    queryString.SCALE = opt_scale;
  }
  if (opt_language) {
    queryString.LANGUAGE = opt_language;
  }
  if (opt_style) {
    queryString.STYLE = opt_style;
  }
  if (opt_legendRule !== undefined) {
    queryString.RULE = opt_legendRule;
    if (opt_legendWidth !== undefined) {
      queryString.WIDTH = opt_legendWidth;
    }
    if (opt_legendHeight !== undefined) {
      queryString.HEIGHT = opt_legendHeight;
    }
  }
  if (opt_servertype == "qgis") {
    if (opt_dpi != undefined) {
      queryString.DPI = opt_dpi;
    }
    if (
      opt_bbox != undefined &&
      opt_srs != undefined &&
      opt_scale != undefined &&
      opt_dpi != undefined &&
      opt_legendRule == undefined
    ) {
      queryString.BBOX = opt_bbox.join(",");
      queryString.SRS = opt_srs;
      queryString.WIDTH = Math.round(
        ((opt_bbox[2] - opt_bbox[0]) / opt_scale) * 39.37 * opt_dpi
      );
      queryString.HEIGHT = Math.round(
        ((opt_bbox[3] - opt_bbox[1]) / opt_scale) * 39.37 * opt_dpi
      );
    }
  }
  if (opt_additionalQueryString) {
    Object.assign(queryString, opt_additionalQueryString);
  }
  return olUriAppendParams(url, queryString);
}

/**
 * Get decscibeFeatureType properties and converts to a json schema for generating dynamic vuetify fields
 * @param {props} decscibeFeatureType json schema
 * @return {object} Vuetify json schema form
 */
export function mapFeatureTypeProps(props, layerName, layerConf) {
  const mapping = {
    string: "string",
    text: "string",
    int: "integer",
    integer: "integer",
    bigint: "integer",
    number: "number",
    numeric: "number"
  };
  let obj = {
    $id: "https://example.com/person.schema.json",
    $schema: "http://json-schema.org/draft-07/schema#",
    type: "object",
    required: [],
    properties: {}
  };

  props.forEach(prop => {
    let type = mapping[prop.data_type];
    if (type) {
      obj.properties[prop.column_name] = {
        type,
        layerName
      };
      if (prop.is_nullable === "NO") {
        obj.required.push(prop.column_name);
      }
      if (!layerConf) return;
      if (
        layerConf["hiddenProps"] &&
        layerConf["hiddenProps"].includes(prop.column_name)
      ) {
        obj.properties[prop.column_name]["x-display"] = "hidden";
      }
      if (
        layerConf["listValues"] &&
        layerConf["listValues"][prop.column_name] &&
        Array.isArray(layerConf["listValues"][prop.column_name].values)
      ) {
        obj.properties[prop.column_name]["enum"] =
          layerConf["listValues"][prop.column_name].values;
        //Show as autocomplete
        obj.properties[prop.column_name]["isAutocomplete"] = true;
      }
    }
  });
  return obj;
}

/**
 * Get the array of pois values
 * @param {poisConfiguration} object pois configuration
 * @return {array} pois key values
 */
export function getPoisListValues(pois) {
  const poisListValues = [];

  pois.forEach(category => {
    const children = category.children;
    children.forEach(pois => {
      poisListValues.push(pois.value);
    });
  });
  return poisListValues;
}

/**
 * Update vector layers query params
 * @param {layer} object map layer
 * @param {key} String Url Key to update
 * @param {value} String
 */
export function updateLayerUrlQueryParam(layer, queryParams) {
  const layerSource = layer.getSource();
  let layerUrl = layerSource.getUrls
    ? layerSource.getUrls()[0]
    : layerSource.getUrl();
  const keys = Object.keys(queryParams);
  if (layerUrl) {
    keys.forEach(key => {
      const value = queryParams[key];
      layerUrl = UrlUtil.updateQueryStringParameter(layerUrl, key, value);
    });
    layerSource.setUrl(layerUrl);
  }
}

/** Refetch layer features if there is no url */
export function fetchLayerFeatures(layer, payload) {
  // Prevent layer to trigger concurrentRequests
  if (layer.get("concurrentRequests") === false) {
    layer.set("isBusy", true);
    store.commit("map/INSERT_BUSY_LAYER", layer);
  }

  http
    .post(layer.get("url"), payload, {
      responseType: "arraybuffer"
    })
    .then(response => {
      const data = response.data;
      const geojson = geobuf.decode(new Pbf(data));
      layer.getSource().clear();
      if (geojson) {
        const features = geojsonToFeature(geojson, {
          dataProjection: "EPSG:4326",
          featureProjection: "EPSG:3857"
        });
        layer.getSource().addFeatures(features);
      }
      if (layer.get("isBusy")) {
        setTimeout(() => {
          layer.set("isBusy", false);
          store.commit("map/REMOVE_BUSY_LAYER", layer);
        }, 200);
      }
    })
    .catch(error => {
      if (layer.get("isBusy")) {
        layer.set("isBusy", false);
        store.commit("map/REMOVE_BUSY_LAYER", layer);
      }
      layer.getSource().clear();
      console.error("Error:", error);
    });
}
