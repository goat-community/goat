import Vue from "vue";
import axios from "axios";
import VueAxios from "vue-axios";
import JwtService from "./jwt.service";

const ApiService = {
  init() {
    Vue.use(VueAxios, axios);
    Vue.axios.defaults.baseURL = "./api/v1";
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
    let slug_url = slug ? `/${slug}` : "";
    return Vue.axios.get(`${resource}${slug_url}`, config).catch(error => {
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
    let slug_url = slug ? `/${slug}` : "";
    return Vue.axios.put(`${resource}${slug_url}`, params);
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
