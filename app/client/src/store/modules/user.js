const state = {
  status: "",
  token: localStorage.getItem("token") || "",
  user: {},
  userId: null
};

const getters = {
  userId: state => state.userId
};

const actions = {};

const mutations = {
  SET_USER_ID(state, id) {
    state.userId = id;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
