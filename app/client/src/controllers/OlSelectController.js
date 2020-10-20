import DrawInteraction from "ol/interaction/Draw";
import { unByKey } from "ol/Observable.js";
import { fromCircle } from "ol/geom/Polygon";
import {
  intersects as intersectsFilter,
  equalTo as equalToFilter,
  and as andFilter
} from "ol/format/filter";

import http from "../services/http";
import axios from "axios";

import { getSelectStyle } from "../style/OlStyleDefs";
import { wfsRequestParser } from "../utils/Layer";

import store from "../store/modules/isochrones";
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
          const filterIntersect = intersectsFilter(
            "geom",
            circleAsPolygon,
            "EPSG:3857"
          );

          const params = selectedLayer.getSource().getParams();
          const layerParams = params.LAYERS.split(":");

          const xmlRequest = wfsRequestParser(
            "EPSG:3857",
            layerParams[0],
            layerParams[1],
            filterIntersect,
            params.viewparams
          );

          const requests = [
            http.post("geoserver/cite/wfs", xmlRequest, {
              headers: { "Content-Type": "text/xml" }
            })
          ];

          const filterUserInputTable = equalToFilter(
            "scenario_id",
            store.state.activeScenario
          );
          const combinedFilter = andFilter(
            filterUserInputTable,
            filterIntersect
          );
          const modifiedReq = wfsRequestParser(
            "EPSG:3857",
            layerParams[0],
            `${layerParams[1]}_modified`,
            combinedFilter
          );
          requests.push(
            http.post("geoserver/cite/wfs", modifiedReq, {
              headers: { "Content-Type": "text/xml" }
            })
          );

          // Request only for population when building layer is active.
          if (selectedLayer.get("name") === "buildings") {
            const populationReq = wfsRequestParser(
              "EPSG:3857",
              layerParams[0],
              "population_modified",
              combinedFilter
            );
            requests.push(
              http.post("geoserver/cite/wfs", populationReq, {
                headers: { "Content-Type": "text/xml" }
              })
            );
          }

          axios
            .all(requests)
            .then(
              axios.spread((first, second, third) => {
                me.source.clear();
                onSelectionEnd({
                  first,
                  second,
                  third
                });
              })
            )
            .catch(error => {
              me.source.clear();
              throw new Error(error);
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
