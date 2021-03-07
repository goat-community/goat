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

/**
 * Converts milimeter to pixel using dpi
 * @param mm
 * @param dpi
 * @returns Pixels
 */
PrintUtils.prototype.mmToPx = function(mm, dpi) {
  let dotsPerMilimeter = dpi / 25.4;
  return Math.ceil(mm * dotsPerMilimeter);
};

/**
 * Converts pixel to mm using dpi
 * @param mm
 * @param dpi
 * @returns Pixels
 */
PrintUtils.prototype.pix2mm = function(val, dpi) {
  return val / 0.0393701 / dpi;
};
