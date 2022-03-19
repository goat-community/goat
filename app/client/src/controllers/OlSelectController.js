import DrawInteraction from "ol/interaction/Draw";
import { unByKey } from "ol/Observable.js";
import { fromCircle } from "ol/geom/Polygon";

import axios from "axios";
import ApiService from "../services/api.service";

import { getSelectStyle } from "../style/OlStyleDefs";
import { geometryToWKT } from "../utils/MapUtils";

import store from "../store/modules/scenarios";
import mapStore from "../store/modules/map";
import OlBaseController from "./OlBaseController";
import i18n from "../../src/plugins/i18n";
/**
 * Class holding the OpenLayers related logic for the select tool.
 */
export default class OlSelectController extends OlBaseController {
  constructor(map) {
    super(map);
  }

  /**
   * Creates a vector layer for the selections and adds it to the
   * map.
   */
  createSelectionLayer() {
    const style = getSelectStyle();
    super.createLayer("Select Layer", style);
  }

  /**
   * Creates and adds the necessary select interaction and adds it to the map.
   */
  addInteraction(
    selectionType,
    selectedLayer,
    onSelectionStart,
    onSelectionEnd
  ) {
    if (selectionType === "multiple") {
      const me = this;
      // cleanup possible old select interaction
      if (me.select) {
        me.clear();
      }

      let listener;
      let sketch;

      const select = new DrawInteraction({
        source: me.source,
        type: "Circle",
        condition: function() {
          if (me.circleRadius > 1000) {
            return false;
          } else {
            return true;
          }
        }
      });

      me.map.addInteraction(select);

      me.createTooltip();
      me.pointerMoveKey = me.map.on("pointermove", me.onPointerMove.bind(me));

      select.on(
        "drawstart",
        evt => {
          //clear existing geometry
          me.source.clear();
          onSelectionStart();
          // preserve sketch
          sketch = evt.feature;
          me.listener = sketch.getGeometry().on("change", function(evt) {
            const geom = evt.target;
            const type = geom.getType();
            if (type === "Circle") {
              me.circleRadius = geom.getRadius().toFixed();
            }
          });
        },
        me
      );

      select.on(
        "drawend",
        evt => {
          const circle = evt.feature.getGeometry();
          //Create polygon from circle geometry;
          const circleAsPolygon = fromCircle(circle);
          circleAsPolygon.transform("EPSG:3857", "EPSG:4326");
          const circleWkt = geometryToWKT(circleAsPolygon);
          // Request from origin table.
          const promiseOriginTable = ApiService.get_(
            `/scenarios/${store.state.activeScenario}/${selectedLayer["name"]}/features?intersect=${circleWkt}&return_type=geojson`
          );

          const requests = [promiseOriginTable];
          mapStore.state.isMapBusy = true;
          axios
            .all(requests)
            .then(
              axios.spread(first => {
                me.source.clear();
                onSelectionEnd(first);
              })
            )
            .catch(error => {
              me.source.clear();
              throw new Error(error);
            })
            .finally(() => {
              mapStore.state.isMapBusy = false;
            });
          // unset sketch
          sketch = null;
          unByKey(listener);
          me.circleRadius = 0;
        },
        me
      );

      // make select interaction available as member
      me.select = select;
    }
  }

  /**
   * Event for updating the select tooltip
   */
  onPointerMove(evt) {
    const me = this;
    const coordinate = evt.coordinate;
    let innerHTML;
    if (!me.circleRadius || me.circleRadius === 0) {
      innerHTML = i18n.t("map.tooltips.clickToStartDrawingCircle");
    } else if (me.circleRadius > 1000) {
      innerHTML = i18n.t("map.tooltips.maxCircleRadius");
    } else {
      innerHTML = me.circleRadius + " m";
    }
    me.tooltipElement.innerHTML = innerHTML;
    me.tooltip.setPosition(coordinate);
  }

  /**
   * Removes the current select interaction.
   */
  removeInteraction() {
    const me = this;

    if (me.select) {
      me.map.removeInteraction(me.select);
    }
    if (me.pointerMoveKey) {
      unByKey(me.pointerMoveKey);
    }
    if (me.clearOverlays) {
      me.clearOverlays();
    }
  }
}
