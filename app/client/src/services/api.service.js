import Vue from "vue";
import axios from "axios";
import VueAxios from "vue-axios";
import JwtService from "./jwt.service";

const ApiService = {
  init() {
    Vue.use(VueAxios, axios);
    console.log(process.env);
    Vue.axios.defaults.baseURL = process.env.VUE_APP_API_URL;
    if (JwtService.getToken()) {
      this.setHeader();
    }
  },

  setHeader() {
    Vue.axios.defaults.headers.common[
      "Authorization"
    ] = `Bearer ${JwtService.getToken()}`;
  },

  query(resource, params) {
    return Vue.axios.get(resource, params).catch(error => {
      throw new Error(`[GOAT] ApiService ${error}`);
    });
  },

  get(resource, slug = "", config = {}) {
    return Vue.axios.get(`${resource}/${slug}`, config).catch(error => {
      throw new Error(`[GOAT] ApiService ${error}`);
    });
  },

  get_(resource, config = {}) {
    return Vue.axios.get(`${resource}`, config).catch(error => {
      throw new Error(`[GOAT] ApiService ${error}`);
    });
  },

  post(resource, params, config = {}) {
    return Vue.axios.post(`${resource}`, params, config);
  },

  update(resource, slug, params) {
    return Vue.axios.put(`${resource}/${slug}`, params);
  },
  put(resource, params) {
    return Vue.axios.put(`${resource}`, params);
  },
  patch(resource, params) {
    return Vue.axios.patch(`${resource}`, params);
  },
  delete(resource) {
    return Vue.axios.delete(resource).catch(error => {
      throw new Error(`[GOAT] ApiService ${error}`);
    });
  }
};

export default ApiService;
