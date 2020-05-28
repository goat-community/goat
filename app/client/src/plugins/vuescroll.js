import Vue from "vue";
import vuescroll from "vuescroll/dist/vuescroll-native";

// You can set global config here.
Vue.use(vuescroll, {
  ops: {
    // The global config
  },
  name: "vue-scroll" // customize component name, default -> vueScroll
});

/**
 * or
 */
Vue.prototype.$vuescrollConfig = {
  bar: {
    background: "#cecece",
    onlyShowBarOnScroll: false,
    keepShow: true
  },
  rail: {
    gutterOfSide: "0px"
  }
};
