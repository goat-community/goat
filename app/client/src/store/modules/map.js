import { getField, updateField } from "vuex-map-fields";

const state = {
  map: null,
  messages: {
    snackbar: {
      type: "info",
      message: "",
      state: false,
      timeout: 2000
    }
  },
  layers: {}, // Only for operational layers
  helpTooltip: {
    isActive: false,
    currentMessage: ""
  },
  contextmenu: null,
  osmMode: false,
  reqFields: null,
  bldEntranceLayer: null,
  editLayer: null,
  selectedEditLayer: null,
  isMapillaryBtnDisabled: false,
  busyLayers: [],
  print: {
    active: false,
    title: "",
    crs: [{ display: "Web Mercator", value: "EPSG:3857" }],
    selectedCrs: "EPSG:3857",
    outputFormats: [
      { display: "PDF", value: "pdf" },
      { display: "PNG", value: "png" }
    ],
    selectedFormat: "pdf",
    rotation: 0,
    dpi: 150,
    dpis: [300, 150, 75],
    layout: {
      name: "A4 landscape",
      format: "a4",
      orientation: "landscape",
      size: [297, 210],
      padding: 5 // in mm.
    },
    layouts: [
      {
        name: "A4 portrait",
        format: "a4",
        orientation: "portrait",
        size: [210, 297],
        padding: 5 // in mm.
      },
      {
        name: "A4 landscape",
        format: "a4",
        orientation: "landscape",
        size: [297, 210],
        padding: 5 // in mm.
      },
      {
        name: "A3 portrait",
        format: "a3",
        orientation: "portrait",
        size: [297, 410],
        padding: 10 // in mm.
      },
      {
        name: "A3 landscape",
        format: "a3",
        orientation: "landscape",
        size: [410, 297],
        padding: 10 // in mm.
      }
    ],
    legend: true,
    grid: false,
    scale: null,
    scales: [500000, 100000, 50000, 25000, 10000, 5000, 2500, 500, 250, 100]
  }
};

const getters = {
  map: state => state.map,
  layers: state => state.layers,
  osmMode: state => state.osmMode,
  helpTooltip: state => state.helpTooltip,
  messages: state => state.messages,
  contextmenu: state => state.contextmenu,
  snackbar: state => state.messages.snackbar,
  reqFields: state => state.reqFields,
  bldEntranceLayer: state => state.bldEntranceLayer,
  editLayer: state => state.editLayer,
  selectedEditLayer: state => state.selectedEditLayer,
  isMapillaryBtnDisabled: state => state.isMapillaryBtnDisabled,
  busyLayers: state => state.busyLayers,
  print: state => state.print,
  getField
};

const actions = {};

const mutations = {
  UPDATE_HELP_TOOLTIP(state, message) {
    state.currentMessage = message;
  },
  TOGGLE_SNACKBAR(state, payload) {
    Object.assign(state.messages.snackbar, payload);
  },
  SET_LAYER(state, layer) {
    if (layer.get("name")) {
      state.layers[layer.get("name")] = layer;
    }
  },
  START_HELP_TOOLTIP(state, message) {
    state.helpTooltip.isActive = true;
    state.helpTooltip.currentMessage = message;
  },
  STOP_HELP_TOOLTIP(state) {
    state.helpTooltip.isActive = false;
  },
  SET_MAP(state, map) {
    state.map = map;
  },
  SET_CONTEXTMENU(state, contextmenu) {
    state.contextmenu = contextmenu;
  },
  SET_OSM_MODE(state) {
    state.osmMode = !state.osmMode;
  },
  UPDATE_REQ_FIELDS(state, reqFields) {
    state.reqFields = reqFields;
  },
  SET_BLD_ENTRANCE_LAYER(state, entranceLayer) {
    state.bldEntranceLayer = entranceLayer;
  },
  SET_EDIT_LAYER(state, editLayer) {
    state.editLayer = editLayer;
  },
  INSERT_BUSY_LAYER(state, layer) {
    state.busyLayers.push(layer);
  },
  REMOVE_BUSY_LAYER(state, layer) {
    state.busyLayers = state.busyLayers.filter(
      l => l.get("name") !== layer.get("name")
    );
  },
  updateField
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
