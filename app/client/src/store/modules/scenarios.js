import { getField, updateField } from "vuex-map-fields";

const state = {
  //Scenarios
  scenarios: {},
  activeScenario: null,
  scenarioDataTable: []
};

const getters = {
  scenarios: state => state.scenarios,
  activeScenario: state => state.activeScenario,
  scenarioDataTable: state => state.scenarioDataTable,
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
