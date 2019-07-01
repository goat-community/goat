import Vue from "vue";
import Vuex from "vuex";
import isochrones from "./modules/isochrones";
import map from "./modules/map";
import loader from "./modules/loader";

Vue.use(Vuex);

// Create a new store
const store = new Vuex.Store({
  modules: { isochrones, map, loader }
});

export default store;
