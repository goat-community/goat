import OlBaseController from "./OlBaseController";
import { Modify, Draw, Snap, Translate } from "ol/interaction";
import SnapGuides from "ol-ext/interaction/SnapGuides";
import DrawHole from "ol-ext/interaction/DrawHole";
import VectorImageLayer from "ol/layer/VectorImage";
import Overlay from "ol/Overlay.js";
import { unByKey } from "ol/Observable";
import i18n from "../../src/plugins/i18n";

/**
 * Class holding the OpenLayers related logic for the edit tool.
 */
export default class OlEditController extends OlBaseController {
  isSnapGuideActive = 0;
  isInteractionOnProgress = false;
  selectedLayer = null;
  originIdName = null;
  highlightSource = null;
  bldEntranceLayer = null;
  popup = null;
  editType = null;
  constructor(map) {
    super(map);
  }

  /**
   * Creates the edit interaction and adds it to the map.
   */
  addInteraction(editType, startCb, endCb) {
    const me = this;
    // cleanup possible old edit interaction
    me.removeInteraction();
    me.createHelpTooltip();
    me.pointerMoveKey = me.map.on("pointermove", me.onPointerMove.bind(me));
    me.createPopupOverlay();
    switch (editType) {
      case "add": {
        let geometryType = this.selectedLayer["editGeometry"];
        me.edit = new Draw({
          type: geometryType[0]
        });
        me.edit.on("drawstart", startCb);
        me.edit.on("drawend", endCb);
        if (this.selectedLayer["name"] !== "poi") {
          me.snap = new Snap({ source: me.source });
        }
        me.currentInteraction = "draw";

        me.helpMessage = i18n.t(
          ["Point"].some(r => geometryType.includes(r))
            ? "map.tooltips.clickToPlacePoint"
            : "map.tooltips.clickToStartDrawing"
        );

        if (!["Point", "LineString"].some(r => geometryType.includes(r))) {
          me.isSnapGuideActive = 1;
        } else {
          me.isSnapGuideActive = 0;
        }
        break;
      }
      case "modify": {
        me.edit = new Modify({ source: me.source });
        me.edit.on("modifystart", startCb);
        me.edit.on("modifyend", endCb);
        me.snap = new Snap({ source: me.source });
        me.currentInteraction = "modify";
        me.helpMessage = i18n.t("map.tooltips.clickAndDragToModify");
        break;
      }
      case "addBldEntrance": {
        me.edit = new Draw({
          type: "Point",
          condition: function(evt) {
            // when the point's button is 1(leftclick), allows drawing
            if (evt.originalEvent.buttons === 1) {
              return true;
            } else {
              return false;
            }
          }
        });
        me.edit.on("drawend", endCb);
        me.modify = new Modify({
          source: me.bldEntranceLayer.getSource()
        });
        me.modify.on("modifyend", endCb);
        me.snap = new Snap({
          source: me.source,
          pixelTolerance: 4
        });
        me.helpMessage = i18n.t("map.tooltips.clickToBldEntrance");
        me.currentInteraction = "addBldEntrance";
        break;
      }
      case "modifyAttributes": {
        me.currentInteraction = "modifyAttributes";
        me.modifyAttributeLister = me.map.on("click", startCb);
        me.helpMessage = i18n.t("map.tooltips.clickToModifyAttributes");
        break;
      }
      case "delete": {
        me.currentInteraction = "delete";
        me.deleteFeatureListener = me.map.on("click", endCb);
        me.helpMessage = i18n.t("map.tooltips.clickOnFeatureToDelete");
        break;
      }
      case "move": {
        me.currentInteraction = "move";
        me.edit = new Translate({ layers: [me.layer] });
        me.edit.on("translatestart", startCb);
        me.edit.on("translateend", endCb);
        me.helpMessage = i18n.t("map.tooltips.clickOnFeatureToMove");
        break;
      }
      case "drawHole": {
        me.currentInteraction = "drawHole";
        me.edit = new DrawHole({ layers: [me.layer] });
        me.edit.on("modifystart", startCb);
        me.edit.on("modifyend", endCb);
        me.helpMessage = i18n.t("map.tooltips.drawHoleOnPolygon");
        me.isSnapGuideActive = 1;
        break;
      }
      default:
        break;
    }
    if (me.edit) {
      me.map.addInteraction(me.edit);
      if (this.isSnapGuideActive) {
        me.addSnapGuideInteraction();
      }
    }
    if (me.snap) {
      me.map.addInteraction(me.snap);
    }
    if (me.modify) {
      me.map.addInteraction(me.modify);
    }
  }

  /**
   * Event for updating the edit help tooltip
   */
  onPointerMove(evt) {
    const me = this;
    //Hide helptooltip if mouse is over popoverlay
    if (me.popupOverlay.getPosition() !== undefined) {
      me.helpTooltip.setPosition(undefined);
      return;
    }
    if (me.contextmenu && me.contextmenu.isOpen()) {
      me.helpTooltip.setPosition(undefined);
      return;
    }

    const coordinate = evt.coordinate;
    me.helpTooltipElement.innerHTML = me.helpMessage;
    me.helpTooltip.setPosition(coordinate);
    if (
      ["addBldEntrance", "move", "modify", "drawHole"].includes(
        this.currentInteraction
      )
    ) {
      if (this.selectedLayer["name"] === "poi") {
        const featureAtCoord = this.source.getClosestFeatureToCoordinate(
          evt.coordinate
        );
        if (
          featureAtCoord &&
          featureAtCoord.get("edit_type") === "d" &&
          me.isInteractionOnProgress === false
        ) {
          me.edit.setActive(false);
        } else {
          me.edit.setActive(true);
        }
        return;
      }

      if (this.selectedLayer["name"] === "building") {
        const buildingFeaturesAtCoord = this.source.getFeaturesAtCoordinate(
          evt.coordinate
        );
        if (
          buildingFeaturesAtCoord.length === 0 ||
          (buildingFeaturesAtCoord.length > 0 &&
            buildingFeaturesAtCoord[0].getProperties().edit_type !== "n")
        ) {
          me.map.getTarget().style.cursor = "not-allowed";
          if (me.isInteractionOnProgress === false) {
            me.edit.setActive(false);
          } else {
            return;
          }
          if (this.currentInteraction === "addBldEntrance") {
            me.helpMessage = i18n.t(
              "map.tooltips.clickToBldEntranceNotAllowed"
            );
          }
          if (this.currentInteraction === "move") {
            me.helpMessage = i18n.t(
              "map.tooltips.moveExistingBuildingNotAllowed"
            );
          }
          if (this.currentInteraction === "modify") {
            me.helpMessage = i18n.t(
              "map.tooltips.modifyExistingBuildingNotAllowed"
            );
          }
          if (this.currentInteraction === "drawHole") {
            me.helpMessage = i18n.t("map.tooltips.drawHoleOnPolygonNotAllowed");
          }
        } else {
          if (this.currentInteraction === "addBldEntrance") {
            me.helpMessage = i18n.t("map.tooltips.clickToBldEntrance");
          }
          if (this.currentInteraction === "move") {
            me.helpMessage = i18n.t("map.tooltips.clickOnFeatureToMove");
          }
          if (this.currentInteraction === "modify") {
            me.helpMessage = i18n.t("map.tooltips.clickAndDragToModify");
          }
          if (this.currentInteraction === "drawHole") {
            me.helpMessage = i18n.t("map.tooltips.drawHoleOnPolygon");
          }
          me.map.getTarget().style.cursor = "pointer";
          me.edit.setActive(true);
        }
      }
    }
  }

  /**
   * Show popup when user deletes or draws a feature.
   */
  createPopupOverlay() {
    const me = this;
    me.popupOverlay = new Overlay({
      element: me.popup.el.$el,
      autoPan: true,
      autoPanMargin: 40,
      positioning: "bottom-left",
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
    me.currentInteraction = "";
    me.removeSnapGuideInteraction();
    if (me.edit) {
      me.map.removeInteraction(me.edit);
      me.edit = null;
    }
    if (me.snap) {
      me.map.removeInteraction(me.snap);
      me.snap = null;
    }
    if (me.modify) {
      me.map.removeInteraction(me.modify);
      me.modify = null;
    }
    if (me.deleteFeatureListener) {
      unByKey(me.deleteFeatureListener);
    }
    if (me.modifyAttributeLister) {
      unByKey(me.modifyAttributeLister);
    }
    if (me.selectedFeature) {
      me.selectedFeature = null;
    }
    if (me.pointerMoveKey) {
      unByKey(me.pointerMoveKey);
    }
    if (me.clearOverlays) {
      me.clearOverlays();
    }
  }

  /**
   * Add snap interaction (aka guide lines) used for building
   */
  addSnapGuideInteraction() {
    // Only for draw and edit
    this.removeSnapGuideInteraction();
    if (
      this.edit &&
      (this.edit instanceof Draw || this.edit instanceof Modify)
    ) {
      const snapi = new SnapGuides({
        vectorClass: VectorImageLayer
      });

      if (this.edit instanceof Draw) {
        snapi.setDrawInteraction(this.edit);
      } else {
        if (
          ["Polygon"].some(r => this.selectedLayer["editGeometry"].includes(r))
        ) {
          snapi.setModifyInteraction(this.edit);
        }
      }
      this.map.addInteraction(snapi);
      this.snapGuideInteraction = snapi;
    }
  }

  /**
   * Remove snap interaction (aka guide lines) used for building
   */
  removeSnapGuideInteraction() {
    if (this.snapGuideInteraction) {
      this.map.removeInteraction(this.snapGuideInteraction);
    }
  }
}
