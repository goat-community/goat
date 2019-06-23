import Vue from "vue";
import Vuex from "vuex";
import isochrones from "./modules/isochrones";

Vue.use(Vuex);

// Create a new store
const store = new Vuex.Store({
  modules: { isochrones }
});

export default store;
