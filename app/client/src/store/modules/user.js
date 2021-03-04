import http from "../../services/http";

const state = {
  status: "",
  token: localStorage.getItem("token") || "",
  user: {},
  userId: null
};

const getters = {
  userId: state => state.userId
};

const actions = {
  setUserId({ commit }) {
    http
      .post("./api/userdata", {
        mode: "insert"
      })
      .then(function(response) {
        if (response.status === 200) {
          if (response.data.userid) {
            commit("SET_USER_ID", response.data.userid);
          }
        }
      })
      .catch(function(error) {
        throw new Error(error);
      });
  }
};

const mutations = {
  SET_USER_ID(state, id) {
    state.userId = parseInt(id);
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
