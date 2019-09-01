import * as olHas from "ol/has.js";
import { toRadians } from "ol/math.js";

/**
 * Provides a service with print utility functions.
 *
 * @constructor
 * @ngdoc service
 * @hidden
 */
export default function PrintUtils() {
  /**
   * @type {number}
   * @private
   */
  this.extentHalfHorizontalDistance_;

  /**
   * @type {number}
   * @private
   */
  this.extentHalfVerticalDistance_;
}

/**
 * @hidden
 */
export const INCHES_PER_METER = 39.37;

/**
 * @hidden
 */
export const DOTS_PER_INCH = 72;

/**
 * Return a function to use as map postcompose listener for drawing a print
 * mask on the map.
 * @param {function():import('ol/size.js').Size} getSize User-defined function returning the
 *     size in dots of the map to print.
 * @param {function(import('ol/PluggableMap.js').FrameState):number} getScale User-defined function
 *     returning the scale of the map to print.
 * @param {function():number=} opt_rotation User defined function returning the
 *     inclination of the canvas in degree (-180 to 180).
 * returning the scale of the map to print.
 * @return {function(import('ol/render/Event.js').default)} Function to use as a map postcompose
 * listener.
 */
PrintUtils.prototype.createPrintMaskPostcompose = function(
  getSize,
  getScale,
  opt_rotation
) {
  const self = this;

  return (
    /**
     * @param {import("ol/render/Event.js").default} evt Postcompose event.
     */
    function(evt) {
      const context = evt.context;
      const frameState = evt.frameState;

      const resolution = frameState.viewState.resolution;

      const viewportWidth = frameState.size[0] * frameState.pixelRatio;
      const viewportHeight = frameState.size[1] * frameState.pixelRatio;

      const center = [viewportWidth / 2, viewportHeight / 2];

      const size = getSize();
      const height = size[1] * olHas.DEVICE_PIXEL_RATIO;
      const width = size[0] * olHas.DEVICE_PIXEL_RATIO;
      const scale = getScale(frameState);

      const ppi = DOTS_PER_INCH;
      const ipm = INCHES_PER_METER;

      const extentHalfWidth = ((width / ppi / ipm) * scale) / resolution / 2;
      self.extentHalfHorizontalDistance_ = ((size[0] / ppi / ipm) * scale) / 2;

      const extentHalfHeight = ((height / ppi / ipm) * scale) / resolution / 2;
      self.extentHalfVerticalDistance_ = ((size[1] / ppi / ipm) * scale) / 2;

      // Draw a mask on the whole map.
      context.beginPath();
      context.moveTo(0, 0);
      context.lineTo(viewportWidth, 0);
      context.lineTo(viewportWidth, viewportHeight);
      context.lineTo(0, viewportHeight);
      context.lineTo(0, 0);
      context.closePath();

      // Draw the print zone
      if (!opt_rotation) {
        self.drawPrintZone_(context, center, extentHalfWidth, extentHalfHeight);
      } else {
        const rotation = toRadians(opt_rotation());
        self.drawPrintZoneWithRotation_(
          context,
          center,
          extentHalfWidth,
          extentHalfHeight,
          rotation
        );
      }

      // Fill the mask
      context.fillStyle = "rgba(0, 5, 25, 0.5)";
      context.fill();
    }
  );
};

/**
 * @param {CanvasRenderingContext2D} context Context of the Postcompose event.
 * @param {Array.<number>} center Center of the viewport (x; y).
 * @param {number} extentHalfWidth Extent half width.
 * @param {number} extentHalfHeight Extent half height.
 * @private
 */
PrintUtils.prototype.drawPrintZone_ = function(
  context,
  center,
  extentHalfWidth,
  extentHalfHeight
) {
  const minx = center[0] - extentHalfWidth;
  const miny = center[1] - extentHalfHeight;
  const maxx = center[0] + extentHalfWidth;
  const maxy = center[1] + extentHalfHeight;

  context.moveTo(minx, miny);
  context.lineTo(minx, maxy);
  context.lineTo(maxx, maxy);
  context.lineTo(maxx, miny);
  context.lineTo(minx, miny);
  context.closePath();
};

/**
 * @param {CanvasRenderingContext2D} context Context of the Postcompose event.
 * @param {Array.<number>} center Center of the viewport (x; y).
 * @param {number} extentHalfWidth Extent half width.
 * @param {number} extentHalfHeight Extent half height.
 * @param {number} rotation Rotation value in radians.
 * @private
 */
PrintUtils.prototype.drawPrintZoneWithRotation_ = function(
  context,
  center,
  extentHalfWidth,
  extentHalfHeight,
  rotation
) {
  // diagonal = distance p1 to center.
  const diagonal = Math.sqrt(
    Math.pow(extentHalfWidth, 2) + Math.pow(extentHalfHeight, 2)
  );
  // gamma = angle between horizontal and diagonal (with rotation).
  const gamma = Math.atan(extentHalfHeight / extentHalfWidth) - rotation;
  // omega = angle between diagonal and vertical (with rotation).
  const omega = Math.atan(extentHalfWidth / extentHalfHeight) - rotation;
  // Calculation of each corner.
  const x1 = center[0] - Math.cos(gamma) * diagonal;
  const y1 = center[1] + Math.sin(gamma) * diagonal;
  const x2 = center[0] + Math.sin(omega) * diagonal;
  const y2 = center[1] + Math.cos(omega) * diagonal;
  const x3 = center[0] + Math.cos(gamma) * diagonal;
  const y3 = center[1] - Math.sin(gamma) * diagonal;
  const x4 = center[0] - Math.sin(omega) * diagonal;
  const y4 = center[1] - Math.cos(omega) * diagonal;

  context.moveTo(x1, y1);
  context.lineTo(x2, y2);
  context.lineTo(x3, y3);
  context.lineTo(x4, y4);
  context.lineTo(x1, y1);
  context.closePath();
};

/**
 * Get the optimal print scale for a map, the map being defined by its
 * size (in pixels) and resolution (in map units per pixel).
 * @param {import("ol/size.js").Size} mapSize Size of the map on the screen (px).
 * @param {number} mapResolution Resolution of the map on the screen.
 * @param {import("ol/size.js").Size} printMapSize Size of the map on the paper (dots).
 * @param {Array.<number>} printMapScales Supported map scales on the paper.
 * The scales are provided as scale denominators, sorted in ascending order.
 * E.g. `[500, 1000, 2000, 4000]`.
 * @return {number} The best scale. `-1` is returned if there is no optimal
 * scale, that is the optimal scale is lower than or equal to the first value
 * in `printMapScales`.
 */
PrintUtils.prototype.getOptimalScale = function(
  mapSize,
  mapResolution,
  printMapSize,
  printMapScales
) {
  const mapWidth = mapSize[0] * mapResolution;
  const mapHeight = mapSize[1] * mapResolution;

  const scaleWidth =
    (mapWidth * INCHES_PER_METER * DOTS_PER_INCH) / printMapSize[0];
  const scaleHeight =
    (mapHeight * INCHES_PER_METER * DOTS_PER_INCH) / printMapSize[1];

  const scale = Math.min(scaleWidth, scaleHeight);

  let optimal = -1;
  for (let i = 0, ii = printMapScales.length; i < ii; ++i) {
    if (scale > printMapScales[i]) {
      optimal = printMapScales[i];
    }
  }

  return optimal;
};

/**
 * Get the optimal map resolution for a print scale and a map size.
 * @param {import("ol/size.js").Size} mapSize Size of the map on the screen (px).
 * @param {import("ol/size.js").Size} printMapSize Size of the map on the paper (dots).
 * @param {number} printMapScale Map scale on the paper.
 * @return {number} The optimal map resolution.
 */
PrintUtils.prototype.getOptimalResolution = function(
  mapSize,
  printMapSize,
  printMapScale
) {
  const dotsPerMeter = DOTS_PER_INCH * INCHES_PER_METER;

  const resolutionX =
    (printMapSize[0] * printMapScale) / (dotsPerMeter * mapSize[0]);
  const resolutionY =
    (printMapSize[1] * printMapScale) / (dotsPerMeter * mapSize[1]);

  const optimalResolution = Math.max(resolutionX, resolutionY);

  return optimalResolution;
};

/**
 * Get the coordinates of the bottom left corner of the printed map.
 * @param {import("ol/coordinate.js").Coordinate} mapCenter Center of the map to print.
 * @return {import("ol/coordinate.js").Coordinate} The coordinates of the bottom left corner.
 */
PrintUtils.prototype.getBottomLeftCorner = function(mapCenter) {
  return [
    mapCenter[0] - this.extentHalfHorizontalDistance_,
    mapCenter[1] - this.extentHalfVerticalDistance_
  ];
};

/**
 * Get the coordinates of the bottom right corner of the printed map.
 * @param {import("ol/coordinate.js").Coordinate} mapCenter Center of the map to print.ç
 * @return {import("ol/coordinate.js").Coordinate} The coordinates of the bottom right corner.
 */
PrintUtils.prototype.getBottomRightCorner = function(mapCenter) {
  return [
    mapCenter[0] + this.extentHalfHorizontalDistance_,
    mapCenter[1] - this.extentHalfVerticalDistance_
  ];
};

/**
 * Get the coordinates of the up left corner of the printed map.
 * @param {import("ol/coordinate.js").Coordinate} mapCenter Center of the map to print.
 * @return {import("ol/coordinate.js").Coordinate} The coordinates of the up left corner.
 */
PrintUtils.prototype.getUpLeftCorner = function(mapCenter) {
  return [
    mapCenter[0] - this.extentHalfHorizontalDistance_,
    mapCenter[1] + this.extentHalfVerticalDistance_
  ];
};

/**
 * Get the coordinates of the up right corner of the printed map.
 * @param {import("ol/coordinate.js").Coordinate} mapCenter Center of the map to print.
 * @return {import("ol/coordinate.js").Coordinate} The coordinates of the up right corner.
 */
PrintUtils.prototype.getUpRightCorner = function(mapCenter) {
  return [
    mapCenter[0] + this.extentHalfHorizontalDistance_,
    mapCenter[1] + this.extentHalfVerticalDistance_
  ];
};
