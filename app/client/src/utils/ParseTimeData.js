// https://github.com/conveyal/analysis-ui/blob/main/lib/actions/analysis/parse-times-data.ts
// Code ported from conveyal analysis-ui

const CURRENT_VERSION = 0;
const HEADER_ENTRIES = 7;
const HEADER_LENGTH = 9; // type + entries
const TIMES_GRID_TYPE = "ACCESSGR";

/**
 * Parse a grid header created by a GridResultWriter
 */
export function parseGridHeader(ab) {
  const headerData = new Int8Array(ab, 0, TIMES_GRID_TYPE.length);
  const headerType = String.fromCharCode.apply(null, headerData);
  if (headerType !== TIMES_GRID_TYPE) {
    throw new Error(
      `Retrieved grid header ${headerType} !== ${TIMES_GRID_TYPE}. Please check your data.`
    );
  }

  // First read the header to figure out how big the body is, then read the full
  // body, then read the JSON metadata at the end.
  const header = new Int32Array(
    ab,
    2 * Int32Array.BYTES_PER_ELEMENT,
    HEADER_ENTRIES
  );
  const version = header[0];
  // validate header and version
  if (version !== CURRENT_VERSION) {
    throw new Error(`Unsupported version ${version} of travel time surface`);
  }

  return {
    zoom: header[1],
    west: header[2],
    north: header[3],
    width: header[4],
    height: header[5],
    depth: header[6],
    version
  };
}

/**
 * Parse the ArrayBuffer from a `*_times.dat` file for a point in a network.
 */
export function parseTimesData(ab) {
  const header = parseGridHeader(ab);
  const gridSize = header.width * header.height;

  // skip the header
  const data = new Int32Array(
    ab,
    HEADER_LENGTH * Int32Array.BYTES_PER_ELEMENT,
    gridSize * header.depth
  );

  // de delta-code
  for (let i = 0, position = 0; i < header.depth; i++) {
    let previous = 0;
    for (let j = 0; j < gridSize; j++, position++) {
      data[position] = data[position] + previous;
      previous = data[position];
    }
  }

  // Decode metadata
  const rawMetadata = new Uint8Array(
    ab,
    (HEADER_LENGTH + header.width * header.height * header.depth) *
      Int32Array.BYTES_PER_ELEMENT
  );
  const metadata = decodeMetadata(rawMetadata);

  function contains(x, y, z) {
    return (
      x >= 0 &&
      x < header.width &&
      y >= 0 &&
      y < header.height &&
      z >= 0 &&
      z < header.depth
    );
  }

  return {
    ...header,
    ...metadata, // may contain accessibility
    data,
    errors: [],
    warnings: metadata.scenarioApplicationWarnings || [],
    contains,
    get(x, y, z) {
      if (contains(x, y, z)) return data[z * gridSize + y * header.width + x];
      return Infinity;
    }
  };
}

function decodeMetadata(rawMetadata) {
  const decoder = getDecoder();
  return JSON.parse(decoder.decode(rawMetadata));
}

function getDecoder() {
  if (window === undefined || typeof window.TextDecoder !== "function") {
    const util = require("util");
    return new util.TextDecoder("utf-8");
  } else {
    return new window.TextDecoder("utf-8");
  }
}
