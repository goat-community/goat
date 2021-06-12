// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from "vue";

import vuetify from "@/plugins/vuetify";
// eslint-disable-next-line no-unused-vars
import http from "./services/http";
import "./plugins/vuescroll";
// Plugins
import i18n from "./plugins/i18n";
import CountryFlag from "vue-country-flag";
Vue.component("country-flag", CountryFlag);

// Application imports
import App from "./App";
import UrlUtil from "./utils/Url";
import store from "./store/index";
import axios from "axios";
import { geobufToFeatures } from "./utils/MapUtils";
import { buffer } from "ol/extent";
import { getCenter } from "ol/extent";
import { EventBus } from "./EventBus";

require("../node_modules/ol/ol.css");
require("./assets/scss/app.scss");

Vue.config.productionTip = false;

// Detect isEmbedded state by attribute embedded and
// make accessible for all components
// recommended by https://vuejs.org/v2/cookbook/adding-instance-properties.html
const appEl = document.querySelector("#app");
Vue.prototype.$isEmbedded = appEl.hasAttribute("embedded");

// Detect an URL parameter for a custom app context
const appCtx = UrlUtil.getQueryParam("appCtx");
let appCtxFile = "";
if (appCtx) {
  // simple approach to avoid path traversal
  appCtxFile = "-" + appCtx.replace(/(\.\.[/])+/g, "");
}

function getAppConf() {
  return axios.get("static/app-conf" + appCtxFile + ".json");
}

function getStudyAreaBbox() {
  return axios.post(
    "/api/map/layer_read",
    {
      table_name: "study_area_union",
      return_type: "geobuf"
    },
    {
      responseType: "arraybuffer"
    }
  );
}

function getLayerStyleTranslation() {
  return axios.get("static/layer-styles/translations/translations.json");
}

axios.all([getAppConf(), getStudyAreaBbox(), getLayerStyleTranslation()]).then(
  axios.spread(function(config, studyArea, layerStyleTranslations) {
    //1- Make app config accessible for all components
    Vue.prototype.$appConfig = config.data;
    //2- Get study area bbox
    if (studyArea.data) {
      const f = geobufToFeatures(studyArea.data, {
        dataProjection: "EPSG:4326",
        featureProjection: "EPSG:3857"
      });
      const originalExtent = f[0].getGeometry().getExtent();
      //Buffer study area extent to not be very strict.
      const bufferedExtent = buffer(originalExtent, 8000);
      //Make extent available in $appConf so the map can use it.
      Vue.prototype.$appConfig.map.originalExtent = originalExtent;
      Vue.prototype.$appConfig.map.extent = bufferedExtent;

      if (!Vue.prototype.$appConfig.map.center) {
        Vue.prototype.$appConfig.map.center = getCenter(originalExtent);
      }
      Vue.prototype.$appConfig.map.studyAreaFeature = f;
    }

    //3- Fetch all layer styles here.

    let promiseArray = [];
    const mapLayers = config.data.map.layers;
    const osmLayer = config.data.map.osmMappingLayers;
    const layers = [...mapLayers, ...osmLayer];
    layers.forEach(layer => {
      const layerName = layer.name;

      if (layer.style && layer.style.format) {
        promiseArray.push(
          axios
            .get(layer.style.url, {
              data: { layerName, format: layer.style.format }
            })
            .catch(() => null)
        );
      }
    });
    if (promiseArray.length > 0) {
      axios.all(promiseArray).then(function(results) {
        const stylesObj = {};
        results.forEach(response => {
          if (response && response.config) {
            const data = JSON.parse(response.config.data);
            const { layerName, format } = data;
            stylesObj[layerName] = {
              format,
              style: response.data,
              translation: layerStyleTranslations.data[layerName]
            };
          }
        });
        EventBus.$emit("inject-styles", stylesObj);
        Vue.prototype.$appConfig.stylesObj = stylesObj;
      });
    }

    /* eslint-disable no-new */
    new Vue({
      el: "#app",
      i18n,
      store,
      vuetify,
      render: h => h(App)
    });
  })
);
