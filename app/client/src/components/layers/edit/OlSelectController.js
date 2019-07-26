import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";

import OlStyleDefs from "../../../style/OlStyleDefs";

/**
 * Class holding the OpenLayers related logic for the select tool.
 */

export default class OlSelectController {
  /* the OL map we want to select on */
  map = null;

  constructor(olMap) {
    this.map = olMap;
  }

  /**
   * Creates a vector layer for the measurement results and adds it to the
   * map.
   */
  createSelectLayer() {
    const me = this;

    // create a vector layer to
    const source = new VectorSource();
    const style = OlStyleDefs.getSelectStyle();
    const vector = new VectorLayer({
      name: "Select Layer",
      displayInLayerList: false,
      source: source,
      style: style
    });

    me.map.addLayer(vector);

    // make vector source available as member
    me.source = source;
  }
}
