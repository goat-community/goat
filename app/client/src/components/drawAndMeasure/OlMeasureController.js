import DrawInteraction from "ol/interaction/Draw";
import { unByKey } from "ol/Observable.js";
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import { getArea, getLength } from "ol/sphere.js";
import Overlay from "ol/Overlay.js";
import { LineString, Polygon } from "ol/geom.js";
import OlStyleDefs from "../../style/OlStyleDefs";

/**
 * Class holding the OpenLayers related logic for the measure tool.
 */
export default class OlMeasureController {
  /* the OL map we want to measure on */
  map = null;
  /**
   * The measure tooltip element.
   * @type {Element}
   */
  measureTooltipElement;
  /**
   * Overlay to show the measurement.
   * @type {module:ol/Overlay}
   */
  measureTooltip;

  /**
   * Overlay objects to be removed on map clear.
   * @type {module:ol/Overlay []}
   */
  overlayersGarbageCollector = [];

  constructor(olMap, measureConf) {
    this.map = olMap;
    this.measureConf = measureConf || {};
  }

  /**
   * Creates a vector layer for the measurement results and adds it to the
   * map.
   */
  createMeasureLayer() {
    const me = this;
    // create a vector layer to
    const source = new VectorSource();
    const style = OlStyleDefs.getMeasureStyle(me.measureConf);
    const vector = new VectorLayer({
      name: "Measure Layer",
      displayInLayerList: false,
      source: source,
      style: style
    });

    me.map.addLayer(vector);

    // make vector source available as member
    me.source = source;
  }

  /**
   * Creates and adds the necessary draw interaction and adds it to the map.
   */
  addInteraction(measureType) {
    const me = this;
    // cleanup possible old draw interaction
    if (me.draw) {
      me.removeInteraction();
    }
    var type = measureType === "area" ? "Polygon" : "LineString";
    var draw = new DrawInteraction({
      source: me.source,
      type: type,
      style: OlStyleDefs.getMeasureInteractionStyle(me.measureConf)
    });
    me.map.addInteraction(draw);
    me.createMeasureTooltip();

    var listener;
    var sketch;

    draw.on(
      "drawstart",
      evt => {
        // preserve sketch
        sketch = evt.feature;

        /** @type {module:ol/coordinate~Coordinate|undefined} */
        var tooltipCoord = evt.coordinate;
        me.listener = sketch.getGeometry().on("change", function(evt) {
          var geom = evt.target;
          var output;
          if (geom instanceof Polygon) {
            output = me.formatArea(geom);
            tooltipCoord = geom.getInteriorPoint().getCoordinates();
          } else if (geom instanceof LineString) {
            output = me.formatLength(geom);
            tooltipCoord = geom.getLastCoordinate();
          }
          me.measureTooltipElement.innerHTML = output;
          me.measureTooltip.setPosition(tooltipCoord);
        });
      },
      me
    );

    draw.on(
      "drawend",
      () => {
        me.measureTooltipElement.className = "tooltip tooltip-static";
        me.measureTooltip.setOffset([0, -7]);
        // unset sketch
        sketch = null;
        // unset tooltip so that a new one can be created
        me.measureTooltipElement = null;
        me.createMeasureTooltip();
        unByKey(listener);
      },
      me
    );

    // make draw interaction available as member
    me.draw = draw;
  }
  /**
   * Calculates and formats the length of the given line.
   *
   * @param  {ol.geom.LineString} line The LineString object to calculate length for
   */
  formatLength(line) {
    const length = getLength(line);
    let output;
    if (length > 100) {
      output = Math.round((length / 1000) * 100) / 100 + " " + "km";
    } else {
      output = Math.round(length * 100) / 100 + " " + "m";
    }
    return output;
  }
  /**
   * Calculates and formats the area of the given polygon.
   *
   * @param  {ol.geom.Polygon} polygon The Polygon object to calculate area for
   */
  formatArea(polygon) {
    const area = getArea(polygon);
    let output;
    if (area > 10000) {
      output = Math.round((area / 1000000) * 100) / 100 + " " + "km²";
    } else {
      output = Math.round(area * 100) / 100 + " " + "m²";
    }
    return output;
  }

  /**
   * Creates a new measure tooltip
   */
  createMeasureTooltip() {
    const me = this;
    if (me.measureTooltipElement) {
      me.measureTooltipElement.parentNode.removeChild(me.measureTooltipElement);
    }
    me.measureTooltipElement = document.createElement("div");
    me.measureTooltipElement.className = "tooltip tooltip-measure";
    me.measureTooltip = new Overlay({
      element: me.measureTooltipElement,
      name: "measure-overlay",
      offset: [0, -15],
      positioning: "bottom-center"
    });
    me.map.addOverlay(me.measureTooltip);
    me.overlayersGarbageCollector.push(me.measureTooltip);
  }

  /**
   * Removes the current interaction and clears the values.
   */
  removeInteraction() {
    const me = this;
    console.log(me.map.getOverlays());
    if (me.draw) {
      me.map.removeInteraction(me.draw);
    }
  }
  clear() {
    const me = this;
    me.removeInteraction();
    console.log(me.map.getOverlays());
    if (me.overlayersGarbageCollector) {
      me.overlayersGarbageCollector.forEach(overlay => {
        me.map.removeOverlay(overlay);
      });
      me.overlayersGarbageCollector = [];
    }
    if (me.source) {
      me.source.clear();
    }
  }
}
