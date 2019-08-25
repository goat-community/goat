const state = {
  map: null,
  messages: {
    interaction: {
      calculateIsochrone: "Click for calculation"
    },
    snackbar: {
      type: "info",
      message: "",
      state: false,
      timeout: 2000
    }
  },
  helpTooltip: {
    isActive: false,
    currentMessage: ""
  },
  studyAreaBbox: ""
};

const getters = {
  map: state => state.map,
  helpTooltip: state => state.helpTooltip,
  messages: state => state.messages,
  studyAreaBbox: state => state.studyAreaBbox,
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
  SET_STUDYAREA_BBOX(state, bbox) {
    state.studyAreaBbox = bbox;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
