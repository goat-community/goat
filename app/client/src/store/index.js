import Vue from "vue";
import Vuex from "vuex";
import isochrones from "./modules/isochrones";
import map from "./modules/map";
import loader from "./modules/loader";
import poisaois from "./modules/poisaois";
import app from "./modules/app";
import auth from "./modules/auth";
import scenarios from "./modules/scenarios";

Vue.use(Vuex);

// Create a new store
const store = new Vuex.Store({
  modules: { isochrones, map, loader, poisaois, scenarios, app, auth }
});

export default store;
