import DrawInteraction from "ol/interaction/Draw";
import { unByKey } from "ol/Observable.js";
import { getArea, getLength } from "ol/sphere.js";
import { LineString, Polygon } from "ol/geom.js";
import {
  getMeasureStyle,
  getMeasureInteractionStyle
} from "../style/OlStyleDefs";

import OlBaseController from "./OlBaseController";
import i18n from "../../src/plugins/i18n";

/**
 * Class holding the OpenLayers related logic for the measure tool.
 */
export default class OlMeasureController extends OlBaseController {
  constructor(map, measureConf) {
    super(map);
    Object.assign(this, { measureConf });
  }

  /**
   * Creates a vector layer for the measurement results and adds it to the
   * map.
   */
  createMeasureLayer() {
    const me = this;
    const style = getMeasureStyle(me.measureConf);
    super.createLayer("Measure Layer", style);
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
    let type = measureType === "area" ? "Polygon" : "LineString";
    let draw = new DrawInteraction({
      source: me.source,
      type: type,
      style: getMeasureInteractionStyle(me.measureConf)
    });
    me.map.addInteraction(draw);

    me.pointerMoveKey = me.map.on("pointermove", me.onPointerMove.bind(me));
    me.createTooltip();
    me.createHelpTooltip();

    me.helpMessage = i18n.t("map.tooltips.clickToStartMeasure");

    let listener;
    let sketch;

    draw.on(
      "drawstart",
      evt => {
        // preserve sketch
        sketch = evt.feature;
        /** @type {module:ol/coordinate~Coordinate|undefined} */
        let tooltipCoord = evt.coordinate;
        me.listener = sketch.getGeometry().on("change", function(evt) {
          const geom = evt.target;
          let output;
          if (geom instanceof Polygon) {
            output = me.formatArea(geom);
            tooltipCoord = geom.getInteriorPoint().getCoordinates();
            if (geom.getLinearRing(0).getCoordinates().length > 3) {
              me.helpMessage = i18n.t(
                "map.tooltips.clickToFinishDrawingPolygon"
              );
            } else {
              me.helpMessage = i18n.t("map.tooltips.clickToContinueDrawing");
            }
          } else if (geom instanceof LineString) {
            output = me.formatLength(geom);
            tooltipCoord = geom.getLastCoordinate();
            me.helpMessage = i18n.t("map.tooltips.clickToFinishDrawingPolygon");
          }
          me.tooltipElement.innerHTML = output;
          me.tooltip.setPosition(tooltipCoord);
        });
      },
      me
    );

    draw.on(
      "drawend",
      () => {
        me.tooltipElement.className = "tooltip tooltip-static";
        me.tooltip.setOffset([0, -7]);
        me.helpMessage = i18n.t("map.tooltips.clickToStartMeasure");
        me.helpTooltipElement.innerHTML = me.helpMessage;
        // unset sketch
        sketch = null;
        // unset tooltip so that a new one can be created
        me.tooltipElement = null;
        me.createTooltip();
        unByKey(listener);
      },
      me
    );

    // make draw interaction available as member
    me.draw = draw;
  }

  /**
   * Event for updating the measure help tooltip
   */
  onPointerMove(evt) {
    const me = this;
    const coordinate = evt.coordinate;
    me.helpTooltipElement.innerHTML = me.helpMessage;
    me.helpTooltip.setPosition(coordinate);
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
   * Removes the current interaction and clears the values.
   */
  removeInteraction() {
    const me = this;
    if (me.draw) {
      me.map.removeInteraction(me.draw);
    }
    if (me.pointerMoveKey) {
      unByKey(me.pointerMoveKey);
    }
    if (me.helpTooltip) {
      me.map.removeOverlay(me.helpTooltip);
    }
    if (me.tooltip) {
      me.map.removeOverlay(me.tooltip);
    }
  }
}
