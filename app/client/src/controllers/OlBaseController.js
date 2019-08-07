import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import Overlay from "ol/Overlay.js";

export default class OlBaseController {
  /**
   * The tooltip element.
   * @type {Element}
   */
  tooltipElement;

  /**
   * Overlay to show the measurement.
   * @type {module:ol/Overlay}
   */
  tooltip;

  /**
   * The help tooltip element.
   * @type {Element}
   */
  helpTooltipElement;

  /**
   * Overlay to show help tooltip message.
   * @type {module:ol/Overlay}
   */
  helpTooltip;

  /**
   * Overlay objects to be removed on map clear.
   * @type {module:ol/Overlay []}
   */
  overlayersGarbageCollector = [];

  constructor(map) {
    Object.assign(this, { map });
  }

  /**
   * Creates a vector layer and adds it to the
   * map.
   */
  createLayer(name, style) {
    const me = this;

    // create a vector layer to
    const source = new VectorSource({ wrapX: false });
    const vector = new VectorLayer({
      name: name,
      displayInLayerList: false,
      source: source,
      style: style
    });

    me.map.addLayer(vector);

    // make vector source available as member
    me.source = source;
  }

  /**
   * Get layer source
   */
  getLayerSource() {
    const me = this;
    return me.source;
  }

  /**
   * Creates a value tooltip
   */
  createTooltip() {
    const me = this;
    if (me.tooltipElement) {
      me.tooltipElement.parentNode.removeChild(me.tooltipElement);
    }
    me.tooltipElement = document.createElement("div");
    me.tooltipElement.className = "tooltip tooltip-measure";
    me.tooltip = new Overlay({
      element: me.tooltipElement,
      offset: [0, -22],
      positioning: "bottom-center"
    });
    me.map.addOverlay(me.tooltip);
    me.overlayersGarbageCollector.push(me.tooltip);
  }

  /**
   * Creates a help tooltip
   */

  createHelpTooltip() {
    const me = this;
    if (me.helpTooltipElement) {
      me.helpTooltipElement.parentNode.removeChild(me.helpTooltipElement);
    }
    me.helpTooltipElement = document.createElement("div");
    me.helpTooltipElement.className = "tooltip";
    me.helpTooltip = new Overlay({
      element: me.helpTooltipElement,
      offset: [15, 0],
      positioning: "center-left"
    });
    me.map.addOverlay(me.helpTooltip);
    me.overlayersGarbageCollector.push(me.helpTooltip);
  }

  /**
   * Removes the current interaction and clears the values.
   */
  clear() {
    const me = this;
    me.removeInteraction();
    if (me.source) {
      me.source.clear();
    }
    if (me.overlayersGarbageCollector) {
      me.overlayersGarbageCollector.forEach(overlay => {
        me.map.removeOverlay(overlay);
      });
      me.overlayersGarbageCollector = [];
    }
  }
}
