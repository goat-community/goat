/**
 * Compute an isoline as a GeoJSON feature from a regular grid
 * Uses the Marching Squares algorithm, with code ported from
 * https://github.com/conveyal/r5/blob/master/src/main/java/com/conveyal/r5/analyst/IsochroneFeature.java
 * @author mattwigway
 * https://github.com/conveyal/analysis-ui/blob/main/lib/utils/jsolines.ts
 * Code from conveyal-ui
 */

import { point } from "@turf/helpers";
import inside from "@turf/boolean-point-in-polygon";

const MAX_COORDS = 20000;

// Set a limit for logging errors so that we can log high usage functions that
// would usually slow the application down from too much I/O
export default function createLogError(maxLimit = 50, delayMs = 1) {
  return function logError(...args) {
    if (maxLimit !== 0) {
      maxLimit -= 1;
      setTimeout(() => console.error(...args), delayMs);
    }
  };
}

// Previously we used `debug`
const logError = createLogError();
/**
 * Create a JSON isoline. Surface is a (possibly typed) array, width and height
 * are its width and height, and cutoff is the cutoff. It is possible to disable
 * linear interpolation for testing purposes by passing interpolation: false.
 */
export function jsolines({
  cutoff,
  height,
  maxCoordinates = MAX_COORDS,
  project,
  interpolation = true,
  surface,
  width,
  excludeHoles = false // Don't include holes in the output
}) {
  // First, create the contour grid.
  const contour = getContour({ surface, width, height, cutoff });
  const cWidth = width - 1;

  // Store warnings
  const warnings = [];

  // JavaScript does not have boolean arrays.
  const found = new Uint8Array((width - 1) * (height - 1));

  // DEBUG, comment out to save memory
  const indices = [];

  // We'll sort out what shell goes with what hole in a bit.
  const shells = [];
  const holes = [];

  // Find a cell that has a line in it, then follow that line, keeping filled
  // area to your left. This lets us use winding direction to determine holes.
  for (let origy = 0; origy < height - 1; origy++) {
    for (let origx = 0; origx < width - 1; origx++) {
      let index = origy * cWidth + origx;
      if (found[index] === 1) {
        continue;
      }

      let idx = contour[index];
      // Continue if there is no line here or if it's a saddle, as we don't know which way the saddle goes.
      if (idx === 0 || idx === 5 || idx === 10 || idx === 15) continue;

      // Huzzah! We have found a line, now follow it, keeping the filled area to our left,
      // which allows us to use the winding direction to determine what should be a shell and
      // what should be a hole
      let pos = [origx, origy];
      let prev = [-1, -1];
      let start = [-1, -1];

      // Track winding direction
      let direction = 0;

      const coords = [];

      // Make sure we're not traveling in circles.
      // NB using index from _previous_ cell, we have not yet set an index for this cell
      while (found[index] !== 1) {
        prev = start;
        start = pos;
        idx = contour[index];

        indices.push(idx);

        // Mark as found if it's not a saddle because we expect to reach saddles twice.
        if (idx !== 5 && idx !== 10) {
          found[index] = 1;
        }

        if (idx === 0 || idx >= 15) {
          warnings.push("Ran off outside of ring");
          break;
        }

        // Follow the loop
        pos = followLoop(idx, pos, prev);
        index = pos[1] * cWidth + pos[0];

        // Keep track of winding direction
        direction += (pos[0] - start[0]) * (pos[1] + start[1]);

        // Shift exact coordinates
        const coord = interpolation
          ? interpolate(pos, cutoff, start, surface, width, height)
          : noInterpolate(pos, start);

        if (!coord) {
          warnings.push(
            `Unexpected coordinate shift from ${start[0]}, ${start[1]} to ${pos[0]}, ${pos[1]}, discarding ring`
          );
          break;
        }

        coords.push(project(coord));

        // TODO Remove completely? May be unnecessary.
        if (coords.length > maxCoordinates) {
          warnings.push(`Ring coordinates > ${maxCoordinates} found, skipping`);
          break;
        }

        // We're back at the start of the ring
        if (pos[0] === origx && pos[1] === origy) {
          coords.push(coords[0]); // close the ring

          // make it a fully-fledged GeoJSON object
          const geom = {
            type: "Feature",
            geometry: {
              type: "Polygon",
              coordinates: [coords]
            }
          };

          // Check winding direction. Positive here means counter clockwise,
          // see http://stackoverflow.com/questions/1165647
          // +y is down so the signs are reversed from what would be expected
          if (direction > 0) shells.push(geom);
          else holes.push(geom);
          break;
        }
      }

      // Log error
      if (found[index] === 1) {
        warnings.push([
          `Ring crosses other ring (or possibly self) at ${pos[0]}, ${pos[1]} coming from case ${idx}`,
          `Last few indices: ${indices
            .slice(Math.max(0, indices.length - 10))
            .join(",")}`
        ]);
      }
    }
  }

  // Shell game time. Sort out shells and holes.
  if (excludeHoles === false) {
    holes.forEach(hole => {
      // Only accept holes that are at least 2-dimensional.
      const vertices = Object.keys(
        hole.geometry.coordinates[0].reduce((unique, [lat, lng]) => {
          unique[`${lat}-${lng}`] = null;
          return unique;
        }, {})
      );

      if (vertices.length >= 3) {
        // NB this is checking whether the first coordinate of the hole is inside
        // the shell. This is sufficient as shells don't overlap, and holes are
        // guaranteed to be completely contained by a single shell.
        const holePoint = point(hole.geometry.coordinates[0][0]);
        const containingShell = shells.find(shell => inside(holePoint, shell));

        if (containingShell) {
          containingShell.geometry.coordinates.push(
            hole.geometry.coordinates[0]
          );
        } else {
          logError("Did not find fitting shell for hole");
        }
      }
    });
  }

  return {
    type: "Feature",
    properties: {},
    geometry: {
      type: "MultiPolygon",
      coordinates: shells.map(s => s.geometry.coordinates)
    }
  };
}

/**
 * Follow the loop
 * We keep track of which contour cell we're in, and we always keep the filled
 * area to our left. Thus we always indicate only which direction we exit the
 * cell.
 */
function followLoop(idx, [x, y], [prevx, prevy]) {
  switch (idx) {
    case 1:
      return [x - 1, y];
    // NB: +y is down
    case 2:
      return [x, y + 1];
    case 3:
      return [x - 1, y];
    case 4:
      return [x + 1, y];
    case 5:
      // Assume that saddle has // orientation (as opposed to \\). It doesn't
      // really matter if we're wrong, we'll just have two disjoint pieces
      // where we should have one, or vice versa.

      // From bottom
      if (prevy > y) return [x + 1, y];

      // From top
      if (prevy < y) return [x - 1, y];

      logError("Entered case 5 saddle point from wrong direction!");
      return [x, y];
    case 6:
      return [x, y + 1];
    case 7:
      return [x - 1, y];
    case 8:
      return [x, y - 1];
    case 9:
      return [x, y - 1];
    case 10: // hex a
      // From left
      if (prevx < x) return [x, y + 1];

      // From right
      if (prevx > x) return [x, y - 1];

      logError("Entered case 10 saddle point from wrong direction.");
      return [x, y];
    case 11:
      return [x, y - 1]; // b
    case 12:
      return [x + 1, y]; // c
    case 13:
      return [x + 1, y]; // d
    case 14:
      return [x, y + 1]; // e
    default:
      logError(`Default case reached in followLoop for id ${idx}.`);
      return [x, y];
  }
}

// Calculated fractions may not be numbers causing interpolation to fail.
const ensureFractionIsNumber = (frac, direction) => {
  if (isNaN(frac) || frac === Infinity) {
    logError(
      `Segment fraction from ${direction} is ${frac}; if this is at the edge of the query this is expected.`
    );
    return 0.5;
  }
  return frac;
};

/**
 * Do linear interpolation.
 */
function interpolate([x, y], cutoff, [startx, starty], surface, width, height) {
  const index = y * width + x;
  let topLeft = surface[index];
  let topRight = surface[index + 1];
  let botLeft = surface[index + width];
  let botRight = surface[index + width + 1];

  // The edges are always considered unreachable to avoid edge effects so set
  // them to the cutoff.
  if (x === 0) topLeft = botLeft = cutoff;
  if (y === 0) topLeft = topRight = cutoff;
  if (y === height - 2) botRight = botLeft = cutoff;
  if (x === width - 2) topRight = botRight = cutoff;

  // From left
  if (startx < x) {
    const frac = (cutoff - topLeft) / (botLeft - topLeft);
    return [x, y + ensureFractionIsNumber(frac, "left")];
  }

  // From right
  if (startx > x) {
    const frac = (cutoff - topRight) / (botRight - topRight);
    return [x + 1, y + ensureFractionIsNumber(frac, "right")];
  }

  // From bottom
  if (starty > y) {
    const frac = (cutoff - botLeft) / (botRight - botLeft);
    return [x + ensureFractionIsNumber(frac, "bottom"), y + 1];
  }

  // From top
  if (starty < y) {
    const frac = (cutoff - topLeft) / (topRight - topLeft);
    return [x + ensureFractionIsNumber(frac, "top"), y];
  }
}

/**
 * Used for testing.
 */
function noInterpolate([x, y], [startx, starty]) {
  // From left
  if (startx < x) return [x, y + 0.5];
  // From right
  if (startx > x) return [x + 1, y + 0.5];
  // From bottom
  if (starty > y) return [x + 0.5, y + 1];
  // From top
  if (starty < y) return [x + 0.5, y];
}

/**
 * Get a contouring grid. Exported for testing purposes, not generally used
 * outside jsolines testing
 */
export function getContour({ surface, width, height, cutoff }) {
  const contour = new Uint8Array((width - 1) * (height - 1));

  // compute contour values for each cell
  for (let x = 0; x < width - 1; x++) {
    for (let y = 0; y < height - 1; y++) {
      const index = y * width + x;
      let topLeft = surface[index] < cutoff;
      let topRight = surface[index + 1] < cutoff;
      let botLeft = surface[index + width] < cutoff;
      let botRight = surface[index + width + 1] < cutoff;

      // if we're at the edge of the area, set the outer sides to false, so that
      // isochrones always close even when they actually extend beyond the edges
      // of the surface
      if (x === 0) topLeft = botLeft = false;
      if (x === width - 2) topRight = botRight = false;
      if (y === 0) topLeft = topRight = false;
      if (y === height - 2) botRight = botLeft = false;

      let idx = 0;

      if (topLeft) idx |= 1 << 3;
      if (topRight) idx |= 1 << 2;
      if (botRight) idx |= 1 << 1;
      if (botLeft) idx |= 1;

      contour[y * (width - 1) + x] = idx;
    }
  }

  return contour;
}
