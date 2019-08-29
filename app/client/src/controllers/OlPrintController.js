import MaskLayer from "../controls/print/Mask";
import * as olEvents from "ol/events.js";
import * as olMath from "ol/math.js";
import PrintUtils from "../utils/PrintUtils";

export default class OlPrintController {
  /* the OL map we want to print */
  map = null;

  constructor(map, rotationInput_) {
    Object.assign(this, {
      map,
      rotationInput_
    });
    this.maskLayer_ = new MaskLayer();

    this.capabilities_ = null;
    /**
     * @type {?import("ol/events.js").EventsKey}
     * @private
     */
    this.pointerDragListenerKey_ = null;

    /**
     * @type {?import("ol/events.js").EventsKey}
     * @private
     */
    this.mapViewResolutionChangeKey_ = null;

    /**
     * Formats availables in capabilities.
     * @type {string[]}
     * @private
     */
    this.formats_ = [];

    /**
     * An array of attributes objects from capabilities.
     * @type {Array<import('/print/mapfish-print-v3').MapFishPrintCapabilitiesLayout>}
     * @private
     */
    this.layouts_ = [];

    /**
     * An attributes object from capabilities.
     * @type {?import('print/mapfish-print-v3').MapFishPrintCapabilitiesLayout}
     * @private
     */
    this.layout_ = null;

    /**
     * @type {number[]}
     * @private
     */
    this.paperSize_ = [];

    /**
     * @type {PrintLayoutInfo}
     */
    this.layoutInfo = {};

    /**
     * @type {number}
     */
    this.rotation = 0;

    /**
     * @return {import("ol/size.js").Size} Size in dots of the map to print.
     */
    const getSizeFn = () => this.paperSize_;
    let getRotationFn;
    if (this.rotateMask) {
      /**
       * @return {number} rotation to apply.
       */
      getRotationFn = () => this.rotation;
    }

    this.maskLayer_.getSize = getSizeFn;
    this.maskLayer_.getScale = this.getScaleFn.bind(this);
    this.maskLayer_.getRotation = getRotationFn;
  }

  /**
   * Function to execute when print panel is open .
   */
  activate() {
    this.active = true;
    if (!this.capabilities_) {
      //GET CAPABILITIES HERE..
    }
    if (!this.capabilities_) {
      throw new Error("Missing capabilities");
    }

    this.capabilities_.then(
      resp => {
        if (!this.map) {
          throw new Error("Missing map");
        }

        // make sure the panel is still open
        if (!this.active) {
          return;
        }

        // Get capabilities - On success
        this.parseCapabilities_(resp);
        this.map.addLayer(this.maskLayer_);
        this.pointerDragListenerKey_ = olEvents.listen(
          this.map,
          "pointerdrag",
          this.onPointerDrag_,
          this
        );
        this.mapViewResolutionChangeKey_ = olEvents.listen(
          this.map.getView(),
          "change:resolution",
          () => {
            this.scaleManuallySelected_ = false;
          }
        );
        this.map.render();
      },
      () => {
        // Get capabilities - On error
        this.capabilities_ = null;
      }
    );
  }

  /**
   * Function to execute when print panel is closed .
   */
  deactivate() {
    this.active = false;
    if (!this.map) {
      throw new Error("Missing map");
    }
    this.map.removeLayer(this.maskLayer_);
    if (this.pointerDragListenerKey_) {
      olEvents.unlistenByKey(this.pointerDragListenerKey_);
    }
    if (this.mapViewResolutionChangeKey_) {
      olEvents.unlistenByKey(this.mapViewResolutionChangeKey_);
    }
    this.setRotation(0);
    this.map.render(); // Redraw (remove) post compose mask;
  }

  /**
   * @param {import('ol/PluggableMap.js').FrameState} frameState Frame state.
   * @return {number} Scale of the map to print.
   */
  getScaleFn(frameState) {
    // Don't compute an optimal scale if the user manually choose a value not in
    // the pre-defined scales. (`scaleInput` in `gmfPrintOptions`).
    if (this.layoutInfo.scale === undefined) {
      throw new Error("Missing layoutInfo.scale");
    }
    if (!this.layoutInfo.scales) {
      throw new Error("Missing layoutInfo.scales");
    }
    if (
      !this.scaleManuallySelected_ &&
      (this.layoutInfo.scale === -1 ||
        this.layoutInfo.scales.includes(this.layoutInfo.scale))
    ) {
      const mapSize = frameState.size;
      const viewResolution = frameState.viewState.resolution;
      this.layoutInfo.scale = this.getOptimalScale_(mapSize, viewResolution);
    }
    return this.layoutInfo.scale;
  }

  /**
   * Gets the print capabilities.
   * @param {string} roleId The roles ids.
   * @private
   */
  getCapabilities(url) {
    console.log(url);
  }
  /**
   * Create the list of layouts, get the formats, get the first layout in
   * gmf print v3 capabilities and then update the print panel layout information.
   * @param {axios} resp Response.
   * @private
   */
  parseCapabilities_(resp) {
    const data = resp["data"];
    this.formats_ = data["formats"] || [];
    this.layouts_ = data["layouts"];
    this.layout_ = data["layouts"][0];

    this.layoutInfo.layouts = [];
    this.layouts_.forEach(layout => {
      this.layoutInfo.layouts.push(layout.name);
    });

    this.updateFields_();
  }

  /**
   * Update layout information with the user values if there are always available in the
   * current layout otherwise use the defaults values of the layout.
   * If a field doesn't exist in the current layout, set it to undefined so the
   * view can hide it. Update also the paper size.
   * custom print templates).
   * @private
   */
  updateFields_() {
    this.layoutInfo.layout = this.layout_.name;

    const mapInfo = this.isAttributeInCurrentLayout_("map");
    console.assert(mapInfo);
    const clientInfo = mapInfo["clientInfo"];
    console.assert(clientInfo);
    this.paperSize_ = [clientInfo["width"], clientInfo["height"]];

    this.layoutInfo.legend =
      this.layoutInfo.attributes.indexOf("legend") >= 0
        ? this.fieldValues["legend"] !== false
        : undefined;
    this.layoutInfo.scales = clientInfo["scales"] || [];
    this.layoutInfo.dpis = clientInfo["dpiSuggestions"] || [];

    const mapSize = this.map.getSize();
    const viewResolution = this.map.getView().getResolution();
    this.layoutInfo.scale = this.getOptimalScale_(mapSize, viewResolution);

    this.layoutInfo.dpi =
      this.layoutInfo.dpi &&
      this.layoutInfo.dpis.indexOf(this.layoutInfo.dpi) > 0
        ? this.layoutInfo.dpi
        : this.layoutInfo.dpis[0];

    this.layoutInfo.formats = {};
    this.formats_.forEach(format => {
      this.layoutInfo.formats[format] = true;
    });

    this.attributesOut = this.layoutInfo.simpleAttributes;

    // Force the update of the mask
    this.map.render();
  }

  /**
   * Return a capabilities 'attribute' object corresponding to the given name.
   * @param {string} name Name of the attribute to get.
   * @return {?Object} corresponding attribute or null.
   * @private
   */
  isAttributeInCurrentLayout_(name) {
    if (!this.layout_) {
      throw new Error("Missing layout");
    }
    let attr = null;
    this.layout_.attributes.forEach(attribute => {
      if (attribute.name === name) {
        attr = attribute;
        return attribute;
      }
    });
    return attr;
  }

  /**
   * Set the current rotation value.
   * Updating the rotation will redraw the mask or rotate the map (depending on the configuration).
   * @param {number} rotation The optional new rotation value in degrees.
   */
  setRotation(rotation) {
    if (!this.map) {
      throw new Error("Missing map");
    }
    this.updateRotation_(rotation);
    // Render the map to update the postcompose mask or rotate the map.
    if (this.rotateMask) {
      this.map.render();
    } else {
      this.map.getView().setRotation(olMath.toRadians(this.rotation));
    }
  }

  /**
   * Set the current rotation value.
   * @param {number} rotation The optional new rotation value in degrees.
   */
  updateRotation_(rotation) {
    this.rotation = olMath.clamp(rotation, -180, 180);
    // sync all the inputs
    this.rotationInput_ = this.rotation;
  }

  /**
   * Get the optimal scale to display the print mask. Return the first scale if
   * no scale matches.
   * @param {import("ol/size.js").Size|undefined} mapSize Size of the map on the screen (px).
   * @param {number|undefined} viewResolution Resolution of the map on the screen.
   * @return {number} The best scale. -1 is returned if there is no optimal
   *     scale, that is the optimal scale is lower than or equal to the first
   *     value in printMapScales.
   * @private
   */
  getOptimalScale_(mapSize, viewResolution) {
    const scales = this.layoutInfo.scales.slice();
    if (mapSize !== undefined && viewResolution !== undefined) {
      return PrintUtils.getOptimalScale(
        mapSize,
        viewResolution,
        this.paperSize_,
        scales.reverse()
      );
    }
    return this.layoutInfo.scales[0];
  }
}
