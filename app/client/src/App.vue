<template>
  <div id="app">
    <keep-alive>
      <router-view />
    </keep-alive>
  </div>
</template>
<script>
import { mapFields } from "vuex-map-fields";
import axios from "axios";
import router from "./router";

export default {
  name: "App",
  mounted() {
    const CancelToken = axios.CancelToken;
    const axiosInstance = axios.create();
    delete axiosInstance.defaults.headers.common["Authorization"];
    axiosInstance.defaults.baseURL = "./api";
    axiosInstance
      .get("/healthz", {
        responseType: "arraybuffer",
        cancelToken: new CancelToken(c => {
          // An executor function receives a cancel function as a parameter
          this.healthZCancelToken = c;
        })
      })
      .then(() => {
        this.healthZCancelToken = null;
      })
      .catch(() => {
        router.push({ name: "maintenance" });
      });
    setTimeout(() => {
      if (this.healthZCancelToken instanceof Function) {
        this.healthZCancelToken("cancelled");
        this.healthZCancelToken = null;
      }
    }, 4000);
  },
  computed: {
    ...mapFields("app", {
      healthZCancelToken: "healthZCancelToken"
    })
  }
};
</script>
