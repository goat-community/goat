import "@fortawesome/fontawesome-free/css/all.css"; // Ensure you are using css-loader

import Vue from "vue";
import Vuetify from "vuetify/lib";
import "vuetify/src/stylus/app.styl";

Vue.use(Vuetify, {
  iconfont: "fa"
});
