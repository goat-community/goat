import OlBaseController from "./OlBaseController";
import OlStyleDefs from "../style/OlStyleDefs";
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import DrawInteraction, { createBox } from "ol/interaction/Draw";
import { unByKey } from "ol/Observable";
import LayerUtils from "../utils/Layer";
import { transform } from "ol/proj.js";
import store from "../store/index.js";
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
      zIndex: 4,
      source: selectionSource,
      style: OlStyleDefs.getFeatureHighlightStyle()
    });
    me.map.addLayer(selectionLayer);
    me.selectionSource = selectionSource;
    store.commit("isochrones/ADD_SELECTION_LAYER", selectionLayer);
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
      console.log(store.state.isochrones.multiIsochroneCalculationMethods);
      if (
        store.state.isochrones.multiIsochroneCalculationMethods.active ===
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
          type: "Circle",
          geometryFunction: createBox()
        });

        drawBoundary.on("drawstart", me.onDrawStart.bind(me));
        drawBoundary.on("drawend", me.onDrawEnd.bind(me));
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
      const region = transform(
        evt.coordinate,
        "EPSG:3857",
        "EPSG:4326"
      ).toString();
      const regionType = "'study_area'";
      store.dispatch("isochrones/countStudyAreaPois", {
        regionType,
        region
      });
    });
  }

  /**
   * Draw interaction start event handler
   */
  onDrawStart() {
    const me = this;
    me.selectionSource.clear();
  }

  /**
   * Draw interaction end event handler
   */
  onDrawEnd(evt) {
    const feature = evt.feature;
    const region = feature
      .getGeometry()
      .clone()
      .transform("EPSG:3857", "EPSG:4326")
      .getExtent()
      .toString();

    const regionType = "'draw'";
    store.dispatch("isochrones/countStudyAreaPois", {
      regionType,
      region
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
