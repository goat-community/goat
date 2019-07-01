import axios from "axios";
import store from "../store/index";

const http = axios.create();

http.interceptors.request.use(
  config => {
    store.commit("loader/START_LOADING");
    return config;
  },
  error => {
    store.commit("loader/FINISH_LOADING");
    return Promise.reject(error);
  }
);

http.interceptors.response.use(
  response => {
    store.commit("loader/FINISH_LOADING");
    return response;
  },
  error => {
    store.commit("loader/FINISH_LOADING");
    return Promise.reject(error);
  }
);

export default http;
