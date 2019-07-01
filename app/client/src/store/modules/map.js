const state = {
  map: null,
  messages: {
    interaction: {
      calculateIsochrone: "Click for calculation"
    }
  },
  helpTooltip: {
    pointerMoveEvent: null,
    overlay: null,
    element: null
  }
};

const getters = {
  map: state => state.map,
  helpTooltip: state => state.helpTooltip,
  messages: state => state.messages
};

const actions = {};

const mutations = {
  SET_HELP_TOOLTIP(state, payload) {
    state.overlay = payload.overlay;
    state.element = payload.element;
  },
  SET_MAP(state, map) {
    state.map = map;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
