import PrintVectorEncoder from "./VectorEncoder.js";
import { getFlatLayers } from "../../utils/Layer";
import http from "../../services/http";
import { stableSort } from "ol/array.js";
import olLayerImage from "ol/layer/Image.js";
import olLayerTile from "ol/layer/Tile.js";
import olLayerVector from "ol/layer/Vector.js";
import { toDegrees } from "ol/math.js";
import * as olSize from "ol/size.js";
import olSourceImageWMS from "ol/source/ImageWMS.js";
import olSourceTileWMS from "ol/source/TileWMS.js";
import olSourceWMTS from "ol/source/WMTS.js";
import olSourceXYZ from "ol/source/XYZ";
import olTilegridWMTS from "ol/tilegrid/WMTS.js";

/**
 * @typedef {function(string): PrintService} CreatePrint
 */

/**
 * Provides a function to create print.Service objects used to
 * interact with MapFish Print v3 services.
 *
 * print.Service objects expose the following methods:
 *
 * - createSpec: create a report specification object
 * - createReport: send a create report request
 * - getStatus: get the status of a report
 * - getReportUrl: get the URL of a report
 * - getCapabilities: get the capabilities of the server
 *
 *
 *     let printBaseUrl = 'http://example.com/print';
 *     let print = new print.Service(printBaseUrl);
 *
 *     let scale = 5000;
 *     let dpi = 72;
 *     let layout = 'A4 portrait';
 *     let format = 'pdf';
 *     let reportSpec = print.createSpec(map, scale, dpi, layout, format, {
 *       'title': 'A title for my report',
 *       'rotation': 45 // degree
 *     });
 *
 * See our live example: [../examples/mapfishprint.html](../examples/mapfishprint.html)
 *
 * TODO and limitations:
 *
 * - createSpec should also accept a bbox instead of a center and a scale.
 * - Add support for ol.style.RegularShape. MapFish Print supports symbols
 *   like crosses, stars and squares, so printing regular shapes should be
 *   possible.
 * - ol.style.Icon may use a sprite image, and offsets to define to rectangle
 *   to use within the sprite. This type of icons won't be printed correctly
 *   as MapFish Print does not support sprite icons.
 *
 * @constructor
 * @param {string} url URL to MapFish print web service.
 * @hidden
 */
export default function PrintService(url) {
  /**
   * @type {string}
   * @private
   */
  this.url_ = url;

  /**
   * @type {import("print/VectorEncoder.js").default}
   * @protected
   */
  this.vectorEncoder = new PrintVectorEncoder();

  /**
   * @type {boolean}
   * @private
   */
  this.printNativeAngle_ = true;
}

/**
 * Cancel a report.
 * @param {string} ref Print report reference.
 * @param {RequestShortcutConfig=} opt_httpConfig $http config object.
 * @return {HttpPromise<Object>} HTTP promise.
 */
PrintService.prototype.cancel = function(ref, opt_httpConfig) {
  const httpConfig =
    opt_httpConfig !== undefined
      ? opt_httpConfig
      : /** @type {RequestShortcutConfig} */ ({});
  const url = `${this.url_}/cancel/${ref}`;
  // "delete" is a reserved word, so use ['delete']
  return http["delete"](url, httpConfig);
};

/**
 * Create a report specification.
 * @param {import("ol/Map.js").default} map Map.
 * @param {number} scale Scale.
 * @param {number} dpi DPI.
 * @param {string} layout Layout.
 * @param {string} format Formats.
 * @param {Object<string, *>} customAttributes Custom attributes.
 * @param {string=} email Email to send the file to.
 * @return {import('print/mapfish-print-v3.js').MapFishPrintSpec} The print spec.
 */
PrintService.prototype.createSpec = function(
  map,
  scale,
  dpi,
  layout,
  format,
  customAttributes,
  email
) {
  const specMap = /** @type {import('print/mapfish-print-v3.js').MapFishPrintMap} */ ({
    dpi: dpi,
    rotation: customAttributes.rotation
  });

  this.encodeMap_(map, scale, specMap);

  /** @type {import('print/mapfish-print-v3.js').MapFishPrintAttributes} */
  const attributes = {
    map: specMap
  };
  Object.assign(attributes, customAttributes);

  const lang = "en";

  /** @type {import('print/mapfish-print-v3.js').MapFishPrintSpec} */
  const spec = {
    attributes,
    format,
    lang,
    layout
  };

  if (email) {
    spec.smtp = { to: email };
  }

  return spec;
};

/**
 * @param {import("ol/Map.js").default} map Map.
 * @param {number} scale Scale.
 * @param {import('print/mapfish-print-v3.js').MapFishPrintMap} object Object.
 * @private
 */
PrintService.prototype.encodeMap_ = function(map, scale, object) {
  const view = map.getView();
  const viewCenter = view.getCenter();
  const viewProjection = view.getProjection();
  const viewResolution = view.getResolution();
  const viewRotation = object.rotation || toDegrees(view.getRotation());

  if (!viewCenter) {
    throw new Error("Missing viewCenter");
  }
  if (!viewProjection) {
    throw new Error("Missing viewProjection");
  }
  if (!viewResolution) {
    throw new Error("Missing viewResolution");
  }

  object.center = viewCenter;
  object.projection = viewProjection.getCode();
  object.rotation = viewRotation;
  object.scale = scale;
  object.layers = [];

  const mapLayerGroup = map.getLayerGroup();
  if (!mapLayerGroup) {
    throw new Error("Missing mapLayerGroup");
  }
  this.printNativeAngle_ = mapLayerGroup.get("printNativeAngle") !== false;
  let layers = getFlatLayers(mapLayerGroup);

  // Sort the layer by ZIndex
  stableSort(
    layers,
    (layer_a, layer_b) =>
      (layer_a.getZIndex() || 0) - (layer_b.getZIndex() || 0)
  );
  layers = layers.slice().reverse();

  layers.forEach(layer => {
    if (layer && layer.getVisible()) {
      this.encodeLayer(object.layers, layer, viewResolution);
    }
  });
};

/**
 * @param {Array<import('print/mapfish-print-v3.js').MapFishPrintLayer>} arr Array.
 * @param {import("ol/layer/Base.js").default} layer Layer.
 * @param {number} resolution Resolution.
 */
PrintService.prototype.encodeLayer = function(arr, layer, resolution) {
  if (!layer) return;
  if (layer instanceof olLayerImage) {
    this.encodeImageLayer_(arr, layer);
  } else if (layer instanceof olLayerTile) {
    this.encodeTileLayer_(arr, layer);
  } else if (layer instanceof olLayerVector) {
    this.encodeVectorLayer(arr, layer, resolution);
  }
};

/**
 * @param {Array<import('print/mapfish-print-v3.js').MapFishPrintLayer>} arr Array.
 * @param {olLayerVector} layer Layer.
 * @param {number} resolution Resolution.
 */
PrintService.prototype.encodeVectorLayer = function(arr, layer, resolution) {
  this.vectorEncoder.encodeVectorLayer(arr, layer, resolution);
};

PrintService.prototype.encodeOverlay = function(overlay) {
  return this.vectorEncoder.encodeOverlay(overlay);
};

/**
 * @param {Array<import('print/mapfish-print-v3.js').MapFishPrintLayer>} arr Array.
 * @param {import("ol/layer/Image.js").default} layer Layer.
 * @private
 */
PrintService.prototype.encodeImageLayer_ = function(arr, layer) {
  if (!(layer instanceof olLayerImage)) {
    throw new Error("layer not instance of olLayerImage");
  }
  const source = layer.getSource();
  if (source instanceof olSourceImageWMS) {
    this.encodeImageWmsLayer_(arr, layer);
  }
};

/**
 * @param {Array<import('print/mapfish-print-v3.js').MapFishPrintLayer>} arr Array.
 * @param {import("ol/layer/Image.js").default} layer Layer.
 * @private
 */
PrintService.prototype.encodeImageWmsLayer_ = function(arr, layer) {
  if (!(layer instanceof olLayerImage)) {
    throw new Error("layer not instance of olLayerImage");
  }
  const source = layer.getSource();
  if (!(source instanceof olSourceImageWMS)) {
    throw new Error("source not instance of olSourceImageWMS");
  }

  const url = source.getUrl();

  if (url !== undefined) {
    this.encodeWmsLayer_(arr, layer, url, source.getParams());
  }
};

/**
 * @param {Array<import('print/mapfish-print-v3.js').MapFishPrintLayer>} arr Array.
 * @param {import("ol/layer/Image.js").default|import("ol/layer/Tile.js").default} layer The layer.
 * @param {string} url Url of the WMS server.
 * @param {Object} params Url parameters
 * @private
 */
PrintService.prototype.encodeWmsLayer_ = function(arr, layer, url, params) {
  if (url.startsWith("/")) {
    url = window.location.origin + url;
  }
  const url_url = new URL(url);
  /** @type {Object<string, string>} */
  const customParams = { TRANSPARENT: "true" };
  if (url_url.searchParams) {
    url_url.searchParams.forEach(
      /**
       * @param {string} value
       * @param {string} key
       */
      (value, key) => {
        customParams[key] = value;
      }
    );
  }
  for (const key in params) {
    const value = params[key];
    // remove empty params
    if (value !== null && value !== undefined) {
      customParams[key] = value;
    }
  }
  delete customParams.LAYERS;
  delete customParams.FORMAT;
  delete customParams.SERVERTYPE;
  delete customParams.VERSION;

  /** @type {import('print/mapfish-print-v3.js').MapFishPrintWmsLayer} */
  const object = {
    baseURL: getAbsoluteUrl_(url_url.origin + url_url.pathname),
    imageFormat: "FORMAT" in params ? params.FORMAT : "image/png",
    layers: params.LAYERS.split(","),
    customParams: customParams,
    serverType: params.SERVERTYPE,
    type: "wms",
    opacity: this.getOpacityOrInherited_(layer),
    version: params.VERSION,
    useNativeAngle: this.printNativeAngle_
  };
  arr.push(object);
};

/**
 * @param {Array<import('print/mapfish-print-v3.js').MapFishPrintLayer>} arr Array.
 * @param {import("ol/layer/Image.js").default|import("ol/layer/Tile.js").default} layer The layer.
 * @private
 */
PrintService.prototype.encodeCascadeWmsLayer_ = function(arr, layer) {
  const object = {
    baseURL: this.mapproxyUrl_,
    imageFormat: "image/png",
    layers: [layer.get("name")],
    customParams: {
      TRANSPARENT: "true"
    },
    type: "wms",
    opacity: this.getOpacityOrInherited_(layer),
    useNativeAngle: this.printNativeAngle_
  };
  arr.push(object);
};

/**
 * @param {string} url URL.
 * @return {string} Absolute URL.
 * @private
 * @hidden
 */
function getAbsoluteUrl_(url) {
  const a = document.createElement("a");
  a.href = encodeURI(url);
  return decodeURI(a.href);
}

/**
 * @param {Array<import('print/mapfish-print-v3.js').MapFishPrintLayer>} arr Array.
 * @param {import("ol/layer/Tile.js").default} layer Layer.
 * @private
 */
PrintService.prototype.encodeTileLayer_ = function(arr, layer) {
  if (!(layer instanceof olLayerTile)) {
    throw new Error("layer not instance of olLayerTile");
  }
  const source = layer.getSource();
  if (source instanceof olSourceWMTS) {
    this.encodeTileWmtsLayer_(arr, layer);
  } else if (source instanceof olSourceTileWMS) {
    this.encodeTileWmsLayer_(arr, layer);
  } else if (source instanceof olSourceXYZ) {
    this.encodeXYZLayer_(arr, layer);
  }
};

/**
 * @param {Array<import('print/mapfish-print-v3.js').MapFishPrintLayer>} arr Array.
 * @param {import("ol/layer/Tile.js").default} layer Layer.
 * @private
 */
PrintService.prototype.encodeTileWmtsLayer_ = function(arr, layer) {
  if (!(layer instanceof olLayerTile)) {
    throw new Error("layer not instance of olLayerTile");
  }
  const source = layer.getSource();
  if (!(source instanceof olSourceWMTS)) {
    throw new Error("source not instance of olSourceWMTS");
  }

  const projection = source.getProjection();
  if (!projection) {
    throw new Error("Missing projection");
  }
  const metersPerUnit = projection.getMetersPerUnit();
  if (!metersPerUnit) {
    throw new Error("Missing metersPerUnit");
  }
  const tileGrid = source.getTileGrid();
  if (!(tileGrid instanceof olTilegridWMTS)) {
    throw new Error("tileGrid not instance of olTilegridWMTS");
  }
  const matrixIds = tileGrid.getMatrixIds();

  /** @type {Array<import('print/mapfish-print-v3.js').MapFishPrintWmtsMatrix>} */
  const matrices = [];

  for (let i = 0, ii = matrixIds.length; i < ii; ++i) {
    const tileRange = tileGrid.getFullTileRange(i);
    matrices.push(
      /** @type {import('print/mapfish-print-v3.js').MapFishPrintWmtsMatrix} */ ({
        identifier: matrixIds[i],
        scaleDenominator: (tileGrid.getResolution(i) * metersPerUnit) / 0.28e-3,
        tileSize: olSize.toSize(tileGrid.getTileSize(i)),
        topLeftCorner: tileGrid.getOrigin(i),
        matrixSize: [
          tileRange.maxX - tileRange.minX,
          tileRange.maxY - tileRange.minY
        ]
      })
    );
  }

  const dimensions = source.getDimensions();
  const dimensionKeys = Object.keys(dimensions);

  const object = /** @type {import('print/mapfish-print-v3.js').MapFishPrintWmtsLayer} */ ({
    baseURL: this.getWmtsUrl_(source),
    dimensions: dimensionKeys,
    dimensionParams: dimensions,
    imageFormat: source.getFormat(),
    layer: source.getLayer(),
    matrices: matrices,
    matrixSet: source.getMatrixSet(),
    opacity: this.getOpacityOrInherited_(layer),
    requestEncoding: source.getRequestEncoding(),
    style: source.getStyle(),
    type: "WMTS",
    version: source.getVersion()
  });

  arr.push(object);
};

/**
 * @param {Array<import('print/mapfish-print-v3.js').MapFishPrintLayer>} arr Array.
 * @param {import("ol/layer/Tile.js").default} layer Layer.
 * @private
 */
PrintService.prototype.encodeTileWmsLayer_ = function(arr, layer) {
  if (!(layer instanceof olLayerTile)) {
    throw new Error("layer not instance of olLayerTile");
  }
  const source = layer.getSource();
  if (!(source instanceof olSourceTileWMS)) {
    throw new Error("source not instance of olSourceTileWMS");
  }

  const urls = source.getUrls();
  if (!urls) {
    throw new Error("Missing urls");
  }
  this.encodeWmsLayer_(arr, layer, urls[0], source.getParams());
};

/**
 * @param {Array<import('print/mapfish-print-v3.js').MapFishPrintLayer>} arr Array.
 * @param {import("ol/layer/Tile.js").default} layer Layer.
 * @private
 */
PrintService.prototype.encodeXYZLayer_ = function(arr, layer) {
  const urls = layer.getSource().getUrls();
  const object = {
    baseURL: urls[0],
    imageFormat: "image/png",
    type: "osm",
    opacity: this.getOpacityOrInherited_(layer),
    useNativeAngle: this.printNativeAngle_
  };
  arr.push(object);
};

/**
 * Return the WMTS URL to use in the print spec.
 * @param {import("ol/source/WMTS.js").default} source The WMTS source.
 * @return {string} URL.
 * @private
 */
PrintService.prototype.getWmtsUrl_ = function(source) {
  const urls = source.getUrls();
  if (!urls) {
    throw new Error("Missing urls");
  }
  return getAbsoluteUrl_(urls[0]);
};

PrintService.prototype.getGridLayer = function() {
  return {
    type: "grid",
    gridType: "LINES",
    numberOfLines: [5, 5],
    renderAsSvg: true,
    valueFormat: "###,###",
    unitFormat: " %s",
    horizontalYOffset: -8,
    verticalXOffset: 8,
    formatGroupingSeparator: "'",
    font: {
      name: [
        "Arial",
        "Helvetica",
        "Nimbus Sans L",
        "Liberation Sans",
        "FreeSans",
        "Sans-serif"
      ],
      size: 8
    }
  };
};

/**
 * Return an opacity value for the specified layer.
 * @param {import("ol/layer/Base.js").default} layer Layer.
 * @return {number} opacity Opacity value.
 * @private
 */
PrintService.prototype.getOpacityOrInherited_ = function(layer) {
  if (layer.get("inheritedOpacity") !== undefined) {
    return layer.get("inheritedOpacity");
  }
  return layer.getOpacity();
};

/**
 * Send a create report request to the MapFish Print service.
 * @param {import('print/mapfish-print-v3.js').MapFishPrintSpec} printSpec Print specification.
 * @return {httpPromise<Object>} HTTP promise.
 */
PrintService.prototype.createReport = function(printSpec) {
  const format = printSpec.format || "pdf";
  const url = `${this.url_}/goat/report.${format}`;
  const httpConfig = {};
  Object.assign(httpConfig, { responseType: "json" });
  return http.post(url, printSpec, httpConfig);
};

/**
 * Send a create report request to the MapFish Print service.
 * @param {import('print/mapfish-print-v3.js').MapFishPrintSpec} printSpec Print specification.
 * @return {httpPromise<Object>} HTTP promise.
 */
PrintService.prototype.downloadReport = function(referenceId) {
  const url = `${this.url_}/goat/report/${referenceId}`;
  const httpConfig = {};
  Object.assign(httpConfig, { responseType: "blob" });
  return http.get(url, httpConfig);
};

/**
 * Get the status of a report.
 * @param {string} ref Print report reference.
 * @return {httpPromise<Object>} HTTP promise.
 */
PrintService.prototype.getStatus = function(ref) {
  const url = `${this.url_}/goat/status/${ref}.json`;
  return http.get(url);
};

/**
 * Get the URL of a report.
 * @param {string} ref Print report reference.
 * @return {string} The report URL for this ref.
 */
PrintService.prototype.getReportUrl = function(ref) {
  return `${this.url_}/goat/report/${ref}`;
};

/**
 * Cancel the print job
 * @param {import('print/mapfish-print-v3.js').MapFishPrintSpec} printSpec Print specification.
 * @return {httpPromise<Object>} HTTP promise.
 */
PrintService.prototype.cancelReportJob = function(referenceId) {
  const url = `${this.url_}/goat/cancel/${referenceId}`;
  return http.delete(url);
};
