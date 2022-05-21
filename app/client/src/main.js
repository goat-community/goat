// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from "vue";

import router from "./router";
import vuetify from "@/plugins/vuetify";
import * as Sentry from "@sentry/vue";
import { BrowserTracing } from "@sentry/tracing";
// eslint-disable-next-line no-unused-vars
import http from "./services/http";
import "./plugins/vuescroll";
// Plugins
import i18n from "./plugins/i18n";
import CountryFlag from "vue-country-flag";
Vue.component("country-flag", CountryFlag);

import ApiService from "./services/api.service";
import ErrorFilter from "./services/error.filter";
import DateFilter from "./services/date.filter";

Vue.filter("date", DateFilter);
Vue.filter("error", ErrorFilter);
ApiService.init();

// Application imports
import App from "./App";
import store from "./store/index";

require("../node_modules/ol/ol.css");
require("./assets/scss/app.scss");

Vue.config.productionTip = false;

/* eslint-disable no-new */
new Vue({
  el: "#app",
  router,
  i18n,
  store,
  vuetify,
  render: h => h(App)
});

Sentry.init({
  Vue,
  dsn:
    "https://2a9bae546fdd4394875e04a3bd7c8c9b@o956694.ingest.sentry.io/6301652",
  integrations: [new BrowserTracing()],
  tracesSampleRate: 0.2
});
