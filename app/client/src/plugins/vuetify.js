// if (process.env.VUE_APP_FONTAWESOME_NPM_AUTH_TOKEN) {
//   require("@fortawesome/fontawesome-pro/css/all.css");
// } else {
// }
require("@fortawesome/fontawesome-free/css/all.css");

import Vue from "vue";
import Vuetify from "vuetify/lib";
import VueI18n from "./i18n";
Vue.use(Vuetify);

export default new Vuetify({
  icons: {
    iconfont: "md" // default - only for display purposes
  },
  lang: {
    t: (key, ...params) => VueI18n.t(key, params)
  }
});
