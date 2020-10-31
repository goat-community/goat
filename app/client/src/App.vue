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
        fluid
        fill-height
        class="pa-0"
      >
        <app-viewer />
        <snackbar />
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
import Viewer from "./components/viewer/viewer";
import { mapActions } from "vuex";
import { mapFields } from "vuex-map-fields";

import "@/globalComponents";

export default {
  name: "wg-app",
  components: {
    Snackbar,
    appSidebar,
    treePanel,
    "app-viewer": Viewer
  },
  data() {
    return {
      isEmbedded: false
    };
  },
  created() {
    this.activeColor = this.$appConfig.baseColor;
  },
  computed: {
    ...mapFields("app", {
      activeColor: "activeColor"
    })
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

    this.setUserId();
  },
  methods: {
    ...mapActions("user", {
      setUserId: "setUserId"
    })
  }
};
</script>
