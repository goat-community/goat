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
  osmMappingLayers: {}, // Only for osm mapping layers
  helpTooltip: {
    isActive: false,
    currentMessage: ""
  },
  contextmenu: null,
  osmMode: false
};

const getters = {
  map: state => state.map,
  layers: state => state.layers,
  osmMappingLayers: state => state.osmMappingLayers,
  osmMode: state => state.osmMode,
  helpTooltip: state => state.helpTooltip,
  messages: state => state.messages,
  contextmenu: state => state.contextmenu,
  snackbar: state => state.messages.snackbar
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
  SET_OSM_MAPPING_LAYER(state, layer) {
    if (layer.get("name")) {
      state.osmMappingLayers[layer.get("name")] = layer;
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
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
