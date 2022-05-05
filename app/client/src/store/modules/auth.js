import ApiService from "../../services/api.service";
import JwtService from "../../services/jwt.service";

import {
  ACTIVATE_ACCOUNT,
  CREATE_USER,
  FORGOT_PASSWORD,
  GET_USER,
  LOGIN,
  LOGOUT,
  RESET_PASSWORD,
  TEST_TOKEN
} from "../actions.type";
import {
  SET_AUTH,
  PURGE_AUTH,
  SET_ERROR,
  SET_USER,
  SET_MESSAGE
} from "../mutations.type";
import { errorMessage } from "../../utils/Helpers";
import { getField, updateField } from "vuex-map-fields";

const state = {
  errors: null,
  message: "",
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
  [FORGOT_PASSWORD](context, payload) {
    return new Promise((resolve, reject) => {
      ApiService.post(`/password-recovery/${payload.get("email")}`)
        .then(response => {
          context.commit(SET_MESSAGE, response.data.msg);
          resolve(response.data);
        })
        .catch(({ response }) => {
          errorMessage(context, response, SET_ERROR);
          reject(response);
        });
    });
  },
  [RESET_PASSWORD](context, payload) {
    return new Promise((resolve, reject) => {
      ApiService.post("/reset-password", payload)
        .then(response => {
          context.commit(SET_MESSAGE, response.data.msg);
          resolve(response.data);
        })
        .catch(({ response }) => {
          errorMessage(context, response, SET_ERROR);
          reject(response);
        });
    });
  },
  [CREATE_USER](context, payload) {
    return new Promise((resolve, reject) => {
      ApiService.post("/users/demo", payload)
        .then(response => {
          resolve(response.data);
        })
        .catch(({ response }) => {
          errorMessage(context, response, SET_ERROR);
          reject(response);
        });
    });
  },
  [TEST_TOKEN](context) {
    return new Promise((resolve, reject) => {
      ApiService.post("/login/test-token")
        .then(response => {
          resolve(response.data);
        })
        .catch(({ response }) => {
          //Token not valid. Logout and reload.
          context.commit(PURGE_AUTH);
          window.location.reload();
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
  [ACTIVATE_ACCOUNT](context, payload) {
    return new Promise((resolve, reject) => {
      ApiService.post(`/users/demo/activate?token=${payload["token"]}`)
        .then(response => {
          resolve(response.data);
          console.log(response);
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
  [SET_MESSAGE](state, message) {
    state.message = message;
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
