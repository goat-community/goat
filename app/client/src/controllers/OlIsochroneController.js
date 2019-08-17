import OlBaseController from "./OlBaseController";
import OlStyleDefs from "../style/OlStyleDefs";
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import { unByKey } from "ol/Observable";
import store from "../store/modules/isochrones";
import LayerUtils from "../utils/Layer";

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
    me.removeInteraction();
    //Add Interaction for single|multiple calculation type...
    if (calculationType === "single") {
      console.log("single...");
    } else {
      if (
        store.state.multiIsochroneCalculationMethods.active === "study_area"
      ) {
        if (!me.studyAreaLayer) {
          me.studyAreaLayer = LayerUtils.getAllChildLayers(me.map).filter(
            layer => layer.get("name") === "study_area_administration"
          );
        }
        if (me.studyAreaLayer.length > 0) {
          //Make study area layer visible if is not.
          me.studyAreaLayer[0].setVisible(true);
        }
        me.setupMapClick();
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
      console.log(evt);
    });
  }

  removeInteraction() {
    const me = this;
    if (me.mapClickListenerKey) {
      unByKey(me.mapClickListenerKey);
    }
  }

  clear() {
    super.clear();
    const me = this;
    if (me.selectionSource) {
      me.selectionSource().clear();
    }
  }
}
