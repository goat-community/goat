import { getField, updateField } from "vuex-map-fields";
import ApiService from "../../services/api.service";
import { GET_SCENARIOS } from "../actions.type";
import { SET_ERROR, SET_SCENARIOS } from "../mutations.type";
import { errorMessage } from "../../utils/Helpers";

const state = {
  //Scenarios
  scenarios: [],
  activeScenario: null,
  scenarioDataTable: []
};

const getters = {
  scenarios: state => state.scenarios,
  activeScenario: state => state.activeScenario,
  activeScenarioObj: state => {
    if (state.activeScenario) {
      return state.scenarios.find(
        scenario => scenario.id === state.activeScenario
      );
    }
    return null;
  },
  scenarioDataTable: state => state.scenarioDataTable,
  // eslint-disable-next-line no-unused-vars
  limitScenarios: (state, getters, rootState, rootGetters) => {
    return rootState.auth.user.limit_scenarios
      ? rootState.auth.user.limit_scenarios
      : 50;
  },
  getField
};

const actions = {
  [GET_SCENARIOS](context) {
    return new Promise((resolve, reject) => {
      ApiService.get("/scenarios")
        .then(response => {
          context.commit(SET_SCENARIOS, response.data);
          resolve(response.data);
        })
        .catch(({ response }) => {
          errorMessage(context, response, SET_ERROR);
          reject(response);
        });
    });
  }
};

const mutations = {
  updateField,
  [SET_SCENARIOS](state, scenarios) {
    state.scenarios = scenarios;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
