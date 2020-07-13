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
  helpTooltip: {
    isActive: false,
    currentMessage: ""
  },
  contextmenu: null
};

const getters = {
  map: state => state.map,
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
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
