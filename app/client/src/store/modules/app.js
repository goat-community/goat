import { getField, updateField } from "vuex-map-fields";

const state = {
  activeColor: {
    primary: "#4CAF50",
    secondary: "#4CAF50"
  } // Default
};

const getters = {
  activeColor: state => state.activeColor,
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
