<template>
  <v-app
    id="wg-app"
    data-app
    :class="{ 'wg-app': true, 'wg-app-embedded': isEmbedded }"
  >
    <v-content>
      <v-container id="ol-map-container" fluid fill-height style="padding: 0">
        <app-map :color="baseColor" />
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import Vue from "vue";
import { EventBus } from "./EventBus.js";
import appMap from "./components/ol/Map";
export default {
  name: "wg-app",
  components: {
    appMap
  },
  data() {
    return {
      isEmbedded: false,
      baseColor: Vue.prototype.$appConfig.baseColor
    };
  },
  mounted() {
    // apply the isEmbedded state to the member var
    this.isEmbedded = this.$isEmbedded;

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
  },
  methods: {}
};
</script>
