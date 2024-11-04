import type { DrawMode } from "@mapbox/mapbox-gl-draw";
import MapboxDraw from "@mapbox/mapbox-gl-draw";
import { circle } from "@turf/circle";
import { distance } from "@turf/distance";
import { lineString, point } from "@turf/helpers";
import { length } from "@turf/length";

MapboxDraw.lib.doubleClickZoom;

const { draw_line_string } = MapboxDraw.modes;
const Constants = MapboxDraw.constants;
const { doubleClickZoom } = MapboxDraw.lib;

const CircleDrawMode = { ...draw_line_string };

type CircleDrawModeOpts = {
  unit: "kilometers" | "miles";
  maxRadius: number;
  passingMode: boolean;
};

const DRAW_CIRCLE = "draw_circle";

const _createGeoJSONCircle = function (lineGeojson, units: "kilometers" | "miles", props = {}) {
  const center = point(lineGeojson["geometry"].coordinates[0]);
  const currentVertex = point(lineGeojson["geometry"].coordinates[1]);
  const radius = distance(center, currentVertex, { units });
  const circleFeature = circle(center, radius, {
    steps: 64,
    units,
    properties: {
      meta: "feature",
      "meta:type": "Polygon",
      ...props,
    },
  });

  return circleFeature;
};

CircleDrawMode.onSetup = function (opts: CircleDrawModeOpts) {
  const lineGeojson = this.newFeature({
    type: "Feature",
    properties: {
      ...opts,
      unit: opts.unit || "kilometers",
      maxRadius: opts.maxRadius || 200,
      passingMode: opts.passingMode || true,
    },
    geometry: {
      type: Constants.geojsonTypes.LINE_STRING,
      coordinates: [],
    },
  });

  const state = {
    line: lineGeojson,
    currentVertexPosition: 0,
    direction: "forward",
  };

  this.addFeature(lineGeojson);
  this.clearSelectedFeatures();
  doubleClickZoom.disable(this);
  this.updateUIClasses({ mouse: Constants.cursors.ADD });
  this.activateUIButton();

  return state;
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
CircleDrawMode.onClick = CircleDrawMode.onTap = function (state, e: any) {
  // this ends the drawing after the user creates a second point, triggering this.onStop
  if (state.currentVertexPosition === 1) {
    return this.changeMode(Constants.modes.SIMPLE_SELECT, {
      featureIds: [state.line.id],
    });
  }
  this.updateUIClasses({ mouse: "add" });
  state.line.updateCoordinate(state.currentVertexPosition, e.lngLat.lng, e.lngLat.lat);

  if (state.direction === "forward") {
    state.currentVertexPosition += 1; // eslint-disable-line
    state.line.updateCoordinate(state.currentVertexPosition, e.lngLat.lng, e.lngLat.lat);
  } else {
    state.line.addCoordinate(0, e.lngLat.lng, e.lngLat.lat);
  }

  return null;
};

CircleDrawMode.onStop = function (state) {
  doubleClickZoom.enable(this);
  this.activateUIButton();

  // check to see if we've deleted this feature
  if (this.getFeature(state.line.id) === undefined) return;

  const isLineValid = state.line.isValid();
  if (isLineValid) {
    const lineGeoJson = state.line.toGeoJSON();
    const circleGeojson = _createGeoJSONCircle(lineGeoJson, "kilometers", {
      active: Constants.activeStates.INACTIVE,
    });
    circleGeojson.id = state.line.id;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    this.map.fire(Constants.events.CREATE as any, {
      features: [state.line.toGeoJSON(), circleGeojson],
    });
  }

  if (!isLineValid || state.line.properties.passingMode) {
    const lineId = state.line.id as string;
    this.deleteFeature(lineId, { silent: true });
    // If passing mode is enabled allow user to repeat drawing circles
    if (state.line.properties.passingMode) {
      this.changeMode(DRAW_CIRCLE as DrawMode, {});
    } else {
      this.changeMode(Constants.modes.SIMPLE_SELECT, {}, { silent: true });
    }
  }
};

CircleDrawMode.toDisplayFeatures = function (state, lineGeojson, display) {
  const isActive = lineGeojson["properties"].id === state.line.id;
  const { units, maxRadius } = state.line.properties;
  const lineCoordinates = lineGeojson["geometry"].coordinates;

  if (maxRadius && lineCoordinates.length > 1) {
    const _lineString = lineString(lineGeojson["geometry"].coordinates);
    const lineLength = length(_lineString, { units });
    if (lineLength > maxRadius) {
      // todo: draw circle with max radius and radius line that follows the cursor
      return;
    }
  }

  const isActiveState = isActive ? Constants.activeStates.ACTIVE : Constants.activeStates.INACTIVE;
  lineGeojson["properties"].active = isActiveState;

  // Render radius line
  display(lineGeojson);

  // Render circle
  if (lineCoordinates.length > 1 && lineCoordinates.length < 3) {
    const circleFeature = _createGeoJSONCircle(lineGeojson, units, {
      active: isActiveState,
    });

    display(circleFeature);
  }
};

export default CircleDrawMode;
