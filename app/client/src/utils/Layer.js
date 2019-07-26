import { Group as LayerGroup } from "ol/layer.js";

/**
 * Util class for OL layers
 */
const LayerUtils = {
  /**
   * Returns a set of map layers which matches the given key value pair.
   *
   * @param {String} key - Key to filter layers
   * @param {Object} value - Value to filter layers
   * @param  {ol.Map} olMap  The OL map to search in
   * @return {ol.layer.Base[]} Array of matching layers
   */
  getLayersBy(key, value, olMap) {
    if (!olMap) {
      console.warn(
        "No OL map passed to LayerUtil.getLayersBy - " +
          "no layer detection possible!"
      );
      return [];
    }

    let layerMatches = [];
    olMap.getLayers().forEach(function(layer) {
      if (layer.get(key) === value) {
        layerMatches.push(layer);
      }
    });

    return layerMatches;
  },

  /**
   * Returns a map layer with the given LID (Layer ID)
   *
   * @param  {String} lid    The LID of the layer to query
   * @param  {ol.Map} olMap  The OL map to search in
   * @return {ol.layer.Base} The OL layer instance or undefined
   */
  getLayerByLid(lid, olMap) {
    return LayerUtils.getLayersBy("lid", lid, olMap)[0];
  },

  /**
   * Returns all map layers excluding from group layer
   *
   * @param  {ol.Map} olMap  The OL map to search in
   * @return {ol.layer.Base[]} Array of all map layers
   */
  getAllChildLayers(olMap) {
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
  },
  /**
   * Zooms to the given layer's extent.
   * Will only work if the layer has kind of vector source.
   *
   * @param  {ol.layer.Base} vecLayer OL vector layer
   * @param  {ol.Map} olMap           The map to perform the zoom on
   */
  zoomToLayerExtent(vecLayer, olMap) {
    if (!vecLayer || !vecLayer.getSource().getExtent || !olMap) {
      return;
    }
    const extent = vecLayer.getSource().getExtent();
    olMap.getView().fit(extent);
  }
};

export default LayerUtils;
