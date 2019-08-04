import OlStyleDefs from "../style/OlStyleDefs";
import OlBaseController from "./OlBaseController";
import { Modify, Draw, Snap } from "ol/interaction";
import Overlay from "ol/Overlay.js";
import store from "../store/modules/user";
import Feature from "ol/Feature";
import LayerUtils from "../utils/Layer";
import http from "../services/http";
import { unByKey } from "ol/Observable";
import OlWaysLayerHelper from "./OlWaysLayerHelper";
import htmlString from "../templates/edit-popup-template";
/**
 * Class holding the OpenLayers related logic for the edit tool.
 */
export default class OlEditController extends OlBaseController {
  featuresToCommit = [];

  constructor(map) {
    super(map);
  }

  /**
   * Creates the edit vector layer and add it to the
   * map.
   */
  createEditLayer() {
    const me = this;
    const style = OlStyleDefs.getEditStyle();
    super.createLayer("Edit Layer", style);
    me.source.on("changefeature", me.onFeatureChange.bind(me));
  }

  /**
   * Creates the edit interaction and adds it to the map.
   */
  addInteraction(editType) {
    const me = this;
    // cleanup possible old edit interaction

    me.removeInteraction();
    me.createHelpTooltip();
    me.pointerMoveKey = me.map.on("pointermove", me.onPointerMove.bind(me));
    me.createPopupOverlay();

    switch (editType) {
      case "add":
        me.edit = new Draw({ source: me.source, type: "LineString" });
        me.edit.on("drawstart", me.onDrawStart.bind(me));
        me.edit.on("drawend", me.onDrawEnd.bind(me));
        me.snap = new Snap({ source: me.source });
        me.currentInteraction = "draw";
        me.helpMessage = "Click to start drawing";
        break;
      case "modify":
        me.edit = new Modify({ source: me.source });
        me.edit.on("modifystart", me.onModifyStart.bind(me));
        me.edit.on("modifyend", me.onModifyEnd.bind(me));
        me.currentInteraction = "modify";
        me.helpMessage = "Click and drag the features to modify";
        break;
      case "delete":
        me.currentInteraction = "delete";
        me.deleteFeatureListener = me.map.on(
          "click",
          me.openDeletePopup.bind(me)
        );
        me.helpMessage = "Click on feature to delete it";

        break;
      default:
        break;
    }
    if (me.edit) {
      me.map.addInteraction(me.edit);
    }
    if (me.snap) {
      me.map.addInteraction(me.snap);
    }
  }

  /**
   * Method to add the selected features to the edit layer
   */
  addFeatures(features) {
    this.source.addFeatures(features);
  }

  /**
   * Event for updating the edit help tooltip
   */
  onPointerMove(evt) {
    const me = this;
    const coordinate = evt.coordinate;
    me.helpTooltipElement.innerHTML = me.helpMessage;
    me.helpTooltip.setPosition(coordinate);
  }

  /**
   * Feature change event handler
   */
  onFeatureChange(evt) {
    const me = this;
    if (me.currentInteraction === "modify") {
      console.log("feature changed");
      const index = me.featuresToCommit.findIndex(
        i => i.ol_uid === evt.feature.ol_uid
      );
      if (index === -1) {
        me.featuresToCommit.push(evt.feature);
      } else {
        me.featuresToCommit[index] = evt.feature;
      }
    }
  }

  /**
   * Draw interaction start event handler
   */
  onDrawStart() {
    const me = this;
    me.featuresToCommit = [];
  }

  /**
   * Draw interaction start event handler
   */
  onDrawEnd(evt) {
    const me = this;
    const feature = evt.feature;
    me.featuresToCommit.push(feature);

    const featureCoordinates = feature.getGeometry().getCoordinates();
    me.popupOverlay.setPosition(featureCoordinates[0]);
    me.popup.title = "Attributes";
    me.popup.selectedInteraction = "add";
    me.popup.isVisible = true;
  }

  /**
   * Modify interaction start event handler
   */
  onModifyStart() {
    const me = this;
    me.featuresToCommit = [];
  }

  /**
   * Modify interaction end event handler
   */
  onModifyEnd() {
    const me = this;
    me.transact();
  }

  /**
   * Opens a popup for the delete confirmation
   */
  openDeletePopup(evt) {
    const me = this;
    const coordinate = evt.coordinate;
    const feature = me.source.getClosestFeatureToCoordinate(coordinate);

    me.selectedFeature = feature;
    if (feature) {
      const featureCoordinates = feature.getGeometry().getCoordinates();
      me.popupOverlay.setPosition(featureCoordinates[0]);
      me.popup.title = "Confirm";
      me.popup.selectedInteraction = "delete";
      me.popup.isVisible = true;
    }
  }

  /**
   * Delete the feature if user selects yes
   */
  deleteFeature() {
    const me = this;
    //TODO: If layer name is ways use openlayers ways layer helper
    OlWaysLayerHelper.deleteFeature(
      me.selectedFeature,
      me.source,
      store.state.userId
    );
    me.closePopup();
  }

  /**
   * Commit feature  if user selects yes
   */
  commitFeature() {
    const me = this;
    me.transact();
  }

  /**
   * Closes the popup if user choose cancel.
   */
  closePopup() {
    const me = this;
    if (me.popupOverlay) {
      me.popupOverlay.setPosition(undefined);
      me.popup.isVisible = false;
    }
  }

  /**
   * Reference popup element
   */
  referencePopupElement(popup) {
    const me = this;
    me.popup = popup;
  }

  /**
   * Transact features to the database using geoserver wfs-t protocol
   */
  transact() {
    const me = this;
    const featuresToAdd = [];
    const featuresToUpdate = [];
    const featuresToRemove = [];

    me.featuresToCommit.forEach(feature => {
      const props = feature.getProperties();
      feature.setProperties({
        status: null
      });

      //Transform the feature
      const geometry = feature.getGeometry().clone();
      geometry.transform("EPSG:3857", "EPSG:4326");
      const transformed = new Feature({
        userid: store.state.userId,
        geom: geometry,
        class_id: props.class_id || null,
        status: null
      });
      transformed.setGeometryName("geom");

      if (me.currentInteraction === "draw") {
        transformed.set("type", "bridge");
      }
      if (
        props.type &&
        props.type !== null &&
        me.currentInteraction === "modify"
      ) {
        props.original_id = null;
      }
      if (
        !props.hasOwnProperty("original_id") &&
        me.currentInteraction === "modify"
      ) {
        transformed.set("original_id", feature.getProperties().id);
      }
      if (
        (typeof feature.getId() == "undefined" &&
          Object.keys(props).length === 1) ||
        !props.hasOwnProperty("original_id")
      ) {
        featuresToAdd.push(transformed);
        featuresToRemove.push(feature);
      } else if (
        props.hasOwnProperty("original_id") &&
        me.currentInteraction === "modify"
      ) {
        transformed.setId(feature.getId());
        featuresToUpdate.push(transformed);
      }
    });

    //TODO: Get feature namespace and feature type (layername) dynamically (node env or ol layer object)
    const formatGML = {
      featureNS: "muc",
      featureType: "ways_modified",
      srsName: "urn:x-ogc:def:crs:EPSG:4326"
    };

    let payload;
    switch (me.currentInteraction) {
      case "draw":
        payload = LayerUtils.wfsTransactionParser(
          featuresToAdd,
          null,
          null,
          formatGML
        );
        break;
      case "modify":
        payload = LayerUtils.wfsTransactionParser(
          featuresToAdd,
          featuresToUpdate,
          null,
          formatGML
        );
        break;
      case "delete":
        payload = LayerUtils.wfsTransactionParser(
          null,
          null,
          featuresToRemove,
          formatGML
        );
        break;
    }
    payload = new XMLSerializer().serializeToString(payload);
    http
      .post("geoserver/wfs", payload, {
        headers: { "Content-Type": "text/xml" }
      })
      .then(function(response) {
        const result = LayerUtils.readTransactionResponse(response.data);
        const FIDs = result.insertIds;

        if (FIDs != undefined && FIDs[0] != "none") {
          let i;
          for (i = 0; i < FIDs.length; i++) {
            const id = parseInt(FIDs[i].split(".")[1]);
            me.source.removeFeature(featuresToRemove[i]);
            featuresToAdd[i].setId(id);
            featuresToAdd[i].getGeometry().transform("EPSG:4326", "EPSG:3857");
            me.source.addFeature(featuresToAdd[i]);
          }
        }
        if (me.currentInteraction == "draw") {
          me.featuresToCommit = [];
        }
      });
  }

  /**
   * Show popup when user deletes or draws a feature.
   */
  createPopupOverlay() {
    const me = this;
    const element = document.createElement("div");
    element.innerHTML = htmlString;
    me.popupOverlay = new Overlay({
      element: me.popup.el.$el,
      autoPan: true,
      autoPanAnimation: {
        duration: 250
      }
    });
    me.map.addOverlay(me.popupOverlay);
    me.overlayersGarbageCollector.push(me.popupOverlay);
  }

  /**
   * Removes the current edit interaction.
   */
  removeInteraction() {
    const me = this;
    me.featuresToCommit = [];
    me.currentInteraction = "";
    me.closePopup();
    if (me.edit) {
      me.map.removeInteraction(me.edit);
      me.edit = null;
    }
    if (me.snap) {
      me.map.removeInteraction(me.snap);
      me.snap = null;
    }
    if (me.deleteFeatureListener) {
      unByKey(me.deleteFeatureListener);
    }
    if (me.selectedFeature) {
      me.selectedFeature = null;
    }
    if (me.pointerMoveKey) {
      unByKey(me.pointerMoveKey);
    }
  }
}
