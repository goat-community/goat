<template>
  <v-app
    id="wg-app"
    data-app
    :class="{ 'wg-app': true, 'wg-app-embedded': isEmbedded }"
  >
    <tree-panel />
    <v-content>
      <v-container
        style="height: 100vh; max-height: 100%;"
        id="ol-map-container"
        fluid
        fill-height
        class="pa-0"
      >
        <app-map :color="controlsColor" />
        <map-loading-progress-status />
        <snackbar />
        <background-switcher />
        <Legend />
      </v-container>
    </v-content>
    <app-sidebar />
  </v-app>
</template>

<script>
import Vue from "vue";
import { EventBus } from "./EventBus.js";

import appSidebar from "./components/core/SideDrawer";
import treePanel from "./components/core/TreePanel";
import Snackbar from "./components/other/Snackbar";

import appMap from "./components/ol/Map";
import MapLoadingProgressStatus from "./components/ol/MapLoadingProgressStatus";
import Legend from "./components/ol/Legend";
import BackgroundSwitcher from "./components/ol/BackgroundSwitcher";

import { mapMutations } from "vuex";

export default {
  name: "wg-app",
  components: {
    appMap,
    appSidebar,
    treePanel,
    MapLoadingProgressStatus,
    Snackbar,
    Legend,
    BackgroundSwitcher
  },
  data() {
    return {
      isEmbedded: false,
      baseColor: Vue.prototype.$appConfig.baseColor,
      controlsColor: Vue.prototype.$appConfig.controlsColor
    };
  },
  mounted() {
    // apply the isEmbedded state to the member var
    this.isEmbedded = this.$isEmbedded;
    ///
    // make the refs (floating module window, which are not connected to their
    // related components, e.g. buttons to toggle them)
    const refs = this.$refs;
    let cmpLookup = {};
    for (const key of Object.keys(refs)) {
      cmpLookup[key] = refs[key][0];
    }
    Vue.prototype.cmpLookup = cmpLookup;
    // inform registered cmps that the app is mounted and the dynamic
    // components are available
    EventBus.$emit("app-mounted");

    //Generate UserId
    const userid = Math.floor(Math.random() * 10000000);
    this.setUserId(userid);
  },
  methods: {
    ...mapMutations("user", {
      setUserId: "SET_USER_ID"
    })
  }
};
</script>
