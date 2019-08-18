import OlBaseController from "./OlBaseController";
import OlStyleDefs from "../style/OlStyleDefs";
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import DrawInteraction, { createBox } from "ol/interaction/Draw";
import { unByKey } from "ol/Observable";
import isochroneStore from "../store/modules/isochrones";
import poisStore from "../store/modules/pois";
import LayerUtils from "../utils/Layer";
import { transform } from "ol/proj.js";

export default class OlIsochroneController extends OlBaseController {
  constructor(map) {
    super(map);
  }

  /**
   * Creates the study area selection vector layer and add it to the
   * map.
   */
  createSelectionLayer() {
    const me = this;
    const selectionSource = new VectorSource({ wrapX: false });
    const selectionLayer = new VectorLayer({
      displayInLayerList: false,
      source: selectionSource,
      style: OlStyleDefs.getFeatureHighlightStyle()
    });
    me.map.addLayer(selectionLayer);
    me.selectionSource = selectionSource;
  }

  /**
   * Creates and adds the necessary draw interaction and adds it to the map.
   */
  addInteraction(calculationType) {
    const me = this;
    me.clear();
    //Add Interaction for single|multiple calculation type...
    if (calculationType === "single") {
      console.log("single...");
    } else {
      console.log(isochroneStore.state.multiIsochroneCalculationMethods);
      if (
        isochroneStore.state.multiIsochroneCalculationMethods.active ===
        "study_area"
      ) {
        //Study are method
        if (!me.studyAreaLayer) {
          me.studyAreaLayer = LayerUtils.getAllChildLayers(me.map).filter(
            layer => layer.get("name") === "study_area_administration"
          );
        }
        if (me.studyAreaLayer.length > 0) {
          me.studyAreaLayer[0].setVisible(true);
        }
        me.setupMapClick();
      } else {
        //Draw Boundary box method
        const drawBoundary = new DrawInteraction({
          source: me.selectionSource,
          type: "Circle",
          geometryFunction: createBox()
        });

        me.map.addInteraction(drawBoundary);

        // make select interaction available as member
        me.drawBoundary = drawBoundary;
      }
    }
  }

  /**
   * Add a map click interaction to let the user select multiple
   * study-areas for multi-isochrone calculation
   */
  setupMapClick() {
    const me = this;
    const map = me.map;
    me.mapClickListenerKey = map.on("click", evt => {
      const coordinate = transform(evt.coordinate, "EPSG:3857", "EPSG:4326");
      const speed = isochroneStore.state.options.speed;
      const minutes = isochroneStore.state.options.minutes;
      const regionType = "study_area";

      const amenities = poisStore.state.selectedPois
        .map(item => {
          return "'" + item.value + "'";
        })
        .toString();

      console.log(coordinate, speed, minutes, regionType, amenities);
    });
  }

  removeInteraction() {
    const me = this;
    // cleanup possible old select interaction
    if (me.drawBoundary) {
      me.map.removeInteraction(me.drawBoundary);
    }
    if (me.mapClickListenerKey) {
      unByKey(me.mapClickListenerKey);
    }
  }

  clear() {
    super.clear();
    const me = this;
    if (me.selectionSource) {
      me.selectionSource.clear();
    }
  }
}
