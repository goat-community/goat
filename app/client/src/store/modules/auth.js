import ApiService from "../../services/api.service";
import JwtService from "../../services/jwt.service";

import { GET_USER, LOGIN, LOGOUT } from "../actions.type";
import { SET_AUTH, PURGE_AUTH, SET_ERROR, SET_USER } from "../mutations.type";
import { errorMessage } from "../../utils/Helpers";
import { getField, updateField } from "vuex-map-fields";

const state = {
  errors: null,
  user: {},
  isAuthenticated: !!JwtService.getToken()
};

const getters = {
  currentUser(state) {
    return state.user;
  },
  isAuthenticated(state) {
    return state.isAuthenticated;
  },
  getField
};

const actions = {
  [LOGIN](context, credentials) {
    return new Promise((resolve, reject) => {
      ApiService.post("/login/access-token", credentials)
        .then(response => {
          context.commit(SET_AUTH, response.data);
          resolve(response.data);
        })
        .catch(({ response }) => {
          errorMessage(context, response, SET_ERROR);
          reject(response);
        });
    });
  },
  [GET_USER](context) {
    return new Promise((resolve, reject) => {
      ApiService.get("/users/me")
        .then(response => {
          context.commit(SET_USER, response.data);
          resolve(response.data);
        })
        .catch(({ response }) => {
          errorMessage(context, response, SET_ERROR);
          reject(response);
        });
    });
  },
  [LOGOUT](context) {
    context.commit(PURGE_AUTH);
  }
};

const mutations = {
  [SET_ERROR](state, error) {
    state.errors = error;
  },
  [SET_AUTH](state, data) {
    state.isAuthenticated = true;
    state.errors = "";
    JwtService.saveToken(data.access_token);
    ApiService.setHeader();
  },
  [SET_USER](state, user) {
    state.user = user;
  },
  [PURGE_AUTH](state) {
    state.isAuthenticated = false;
    state.user = {};
    state.errors = "";
    JwtService.destroyToken();
  },
  updateField
};

export default {
  namespaced: true,
  state,
  actions,
  mutations,
  getters
};
