export const DEFAULT_VERSION = '1.3.0';


/**
 * Generates a WMS (Web Map Service) URL for fetching map tiles.
 *
 * @param {string} baseUrl - The base URL of the WMS service.
 * @param {string} layers - Comma-separated list of layer names to include in the request.
 * @param {string} [version="1.3.0"] - Optional WMS version. Defaults to "1.3.0" if not provided.
 * @param {number} [dpi=90] - Optional DPI (Dots Per Inch) for the map tiles. Defaults to 90 if not provided.
 * @returns {string} - The generated WMS URL with the specified parameters.
 */

export const generateWmsUrl = (baseUrl, layers, styles, version?, dpi?) => {
  const width = 256;
  const height = 256;
  const _dpi = dpi || 90;
  const _version = version || DEFAULT_VERSION;
  return `${baseUrl}?bbox={bbox-epsg-3857}&service=WMS&REQUEST=GetMap&layers=${layers}&FORMAT=image/png&TRANSPARENT=true&WIDTH=${width}&HEIGHT=${height}&SRS=EPSG:3857&CRS=EPSG:3857&VERSION=${_version}&STYLES=${styles}&DPI=${_dpi}&MAP_RESOLUTION=${_dpi}&FORMAT_OPTIONS=dpi:${_dpi}`;
};


/**
 * Generates a GetLegendGraphic URL for a WMS layer.
 *
 * @param {string} baseUrl - The base URL of the WMS service.
 * @param {string} layer - The name of the layer for which to get the legend graphic.
 * @param {string} style - The style to be applied to the layer.
 * @param {string} [wmsVersion] - The version of the WMS service (optional).
 * @param {string} [sldVersion] - The version of the Styled Layer Descriptor (SLD) (optional).
 * @returns {string} - The constructed GetLegendGraphic URL.
 */
export const generateLayerGetLegendGraphicUrl = (baseUrl, layer, style, wmsVersion?, sldVersion?) => {
  const _wmsVersion = wmsVersion || DEFAULT_VERSION;
  const _sldVersion = sldVersion || '1.1.0';
  const _style = style || 'default';

  return `${baseUrl}?service=WMS&REQUEST=GetLegendGraphic&layer=${layer}&FORMAT=image/png&TRANSPARENT=true&VERSION=${_wmsVersion}&STYLE=${_style}&SLD_VERSION=${_sldVersion}`;
};
