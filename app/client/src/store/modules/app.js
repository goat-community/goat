import { getField, updateField } from "vuex-map-fields";

const state = {
  activeColor: {
    primary: "#2BB381",
    secondary: "#2BB381"
  }, // Default
  layerTabIndex: 0
};

const getters = {
  activeColor: state => state.activeColor,
  layerTabIndex: state => state.layerTabIndex,
  getField
};

const actions = {};

const mutations = {
  updateField
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
