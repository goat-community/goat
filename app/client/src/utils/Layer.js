import { Group as LayerGroup } from "ol/layer.js";
import olLayerLayer from "ol/layer/Layer.js";
import { WFS } from "ol/format";
import olLayerImage from "ol/layer/Image.js";
import olLayerVector from "ol/layer/Vector.js";
import olSourceImageWMS from "ol/source/ImageWMS.js";
import { appendParams as olUriAppendParams } from "ol/uri.js";

const ServerType = "geoserver";

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
 * Creates the WFS serialized string
 *
 * @param  {string} srsName The source coordinate reference system
 * @param  {string} namespace The Geoserver namespace
 * @param  {string} workspace The Geoserver workspace
 * @param  {string} layerName The Layer name
 * @param  {ol.format.filter} filter The Openlayers filter
 *
 */
export function wfsRequestParser(
  srsName,
  workspace,
  layerName,
  filter,
  viewparams = undefined
) {
  const xs = new XMLSerializer();
  const opt = {
    srsName: srsName,
    featurePrefix: workspace,
    featureTypes: [layerName],
    outputFormat: "application/json",
    filter: filter
  };
  if (viewparams) {
    opt.viewParams = viewparams.toString();
  }

  const wfs = new WFS().writeGetFeature(opt);
  const xmlparser = xs.serializeToString(wfs);
  return xmlparser;
}

export function wfsTransactionParser(
  featuresToAdd,
  featuresToUpdate,
  featuresToDelete,
  formatGML
) {
  const wfs = new WFS();
  const xml = wfs.writeTransaction(
    featuresToAdd,
    featuresToUpdate,
    featuresToDelete,
    formatGML
  );
  return xml;
}

export function readTransactionResponse(data) {
  const wfs = new WFS();
  return wfs.readTransactionResponse(data);
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
 * Create and return a basic WMS layer with only a source URL and a comma
 * separated layers names (see {@link import("ol/source/ImageWMS.js").default}).
 *
 * @param {string} sourceURL The source URL.
 * @param {string} sourceLayersName A comma separated names string.
 * @param {string} sourceFormat Image format, for example 'image/png'.
 * @param {string=} opt_serverType Type of the server ("mapserver",
 *     "geoserver", "qgisserver", …).
 * @param {string=} opt_time time parameter for layer queryable by time/period
 * @param {Object<string, string>=} opt_params WMS parameters.
 * @param {string=} opt_crossOrigin crossOrigin.
 * @param {Object=} opt_customSourceOptions Some initial options.
 * @param {Object=} opt_customLayerOptions The layer opacity.
 * @return {import("ol/layer/Image.js").default} WMS Layer.
 */
export function createBasicWMSLayer(
  sourceURL,
  sourceLayersName,
  sourceFormat,
  opt_serverType,
  opt_time,
  opt_params,
  opt_crossOrigin,
  opt_customSourceOptions,
  opt_customLayerOptions
) {
  /** @type {Object<string, string>} */
  const params = {
    FORMAT: sourceFormat,
    LAYERS: sourceLayersName
  };
  let olServerType;
  if (opt_time) {
    params.TIME = opt_time;
  }
  if (opt_serverType) {
    params.SERVERTYPE = opt_serverType;
    // OpenLayers expects 'qgis' insteads of 'qgisserver'
    olServerType = opt_serverType.replace(ServerType.QGISSERVER, "qgis");
  }
  const options = Object.assign({}, opt_customSourceOptions, {
    url: sourceURL,
    params: params,
    serverType: olServerType,
    crossOrigin: opt_crossOrigin
  });
  const source = new olSourceImageWMS(options);
  if (opt_params) {
    source.updateParams(opt_params);
  }

  const layerOptions = Object.assign({}, opt_customLayerOptions, { source });
  return new olLayerImage(layerOptions);
}

/**
 * Get the WMTS legend URL for the given layer.
 * @param {import("ol/layer/Tile.js").default} layer Tile layer as returned by the
 * layerHelper service.
 * @return {string|undefined} The legend URL or undefined.
 */
export function getWMTSLegendURL(layer) {
  // FIXME case of multiple styles ?  case of multiple legendUrl ?
  let url;
  const styles = layer.get("capabilitiesStyles");
  if (styles !== undefined) {
    const legendURL = styles[0].legendURL;
    if (legendURL !== undefined) {
      url = legendURL[0].href;
    }
  }
  return url;
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
  opt_language
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
    int: "integer",
    number: "number"
  };
  let obj = {
    $id: "https://example.com/person.schema.json",
    $schema: "http://json-schema.org/draft-07/schema#",
    type: "object",
    required: [],
    properties: {}
  };

  props.forEach(prop => {
    let type = mapping[prop.localType];
    if (type) {
      obj.properties[prop.name] = {
        type,
        layerName
      };
      if (prop.nillable === false) {
        obj.required.push(prop.name);
      }
      if (!layerConf) return;
      if (
        layerConf["hiddenProps"] &&
        layerConf["hiddenProps"].includes(prop.name)
      ) {
        obj.properties[prop.name]["x-display"] = "hidden";
      }
      if (
        layerConf["listValues"] &&
        layerConf["listValues"][prop.name] &&
        Array.isArray(layerConf["listValues"][prop.name].values)
      ) {
        obj.properties[prop.name]["enum"] =
          layerConf["listValues"][prop.name].values;
        //Show as autocomplete
        obj.properties[prop.name]["isAutocomplete"] = true;
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
