const state = {
  isNetworkBusy: false
};

const getters = {
  isNetworkBusy: state => state.isNetworkBusy
};

const actions = {};

const mutations = {
  START_LOADING: state => (state.isNetworkBusy = true),
  FINISH_LOADING: state => (state.isNetworkBusy = false)
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
