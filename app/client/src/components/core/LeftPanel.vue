<template>
  <v-navigation-drawer
    id="tree-panel"
    v-model="drawer"
    :mini-variant.sync="mini"
    app
    persistent
    permanent
    left
    hide-overlay
    mini-variant-width="50"
    width="360"
    class="right-shadow"
  >
    <v-layout
      :style="`background-color:${getColor};`"
      justify-space-between
      column
      fill-height
    >
      <template v-if="mini">
        <v-btn
          class="ml-3 mt-2"
          text
          small
          icon
          light
          @click.stop="mini = !mini"
        >
          <v-icon color="white">fas fa-chevron-right</v-icon>
        </v-btn>
      </template>
      <template v-show="!mini">
        <v-app-bar
          v-show="!mini"
          flat
          class="toolbar"
          :color="appColor.primary"
          height="50"
        >
          <img id="app-logo" :src="logoText" width="120px" />
          <v-spacer></v-spacer>
          <v-btn text icon light @click.stop="mini = !mini">
            <v-icon small color="white">fas fa-chevron-left</v-icon>
          </v-btn>
        </v-app-bar>
        <v-tabs
          v-show="!mini"
          grow
          :color="appColor.secondary"
          class="elevation-3"
          v-model="topTabIndex"
          :key="tabKey"
        >
          <v-tab class="px-0">
            {{ $t("appBar.buttons.isochrones") }}
          </v-tab>
          <v-tab class="px-0">
            {{ $t("appBar.buttons.heatmaps") }}
          </v-tab>
          <v-tab class="px-0">
            {{ $t("appBar.buttons.staticLayers") }}
          </v-tab>
        </v-tabs>
        <v-tabs
          :color="appColor.secondary"
          v-show="componentNames[topTabIndex] === 'map-layertree'"
          grow
          v-model="layerTabIndex"
        >
          <v-tab>
            <v-badge>
              <b>{{ $t("appBar.buttons.allLayers") }}</b>
            </v-badge>
          </v-tab>
          <v-tab>
            <v-badge>
              <b>{{ $t("appBar.buttons.activeLayers") }}</b>
            </v-badge>
          </v-tab>
        </v-tabs>

        <vue-scroll v-show="!mini" ref="vs">
          <v-layout
            v-show="!mini"
            justify-space-between
            column
            fill-height
            style="overflow-y: auto;"
          >
            <keep-alive>
              <component v-bind:is="componentNames[topTabIndex]"></component>
            </keep-alive>
          </v-layout>
        </vue-scroll>
      </template>
    </v-layout>
  </v-navigation-drawer>
</template>

<script>
// Utilities
import IsochronesComponent from "../isochrones/Isochrones";
import HeatmapsComponent from "../heatmaps/Heatmaps";
import LayerTree from "../layers/layerTree/LayerTree";
import { mapGetters } from "vuex";
import { mapFields } from "vuex-map-fields";
import { Isochrones } from "../../mixins/Isochrones";

export default {
  components: {
    "map-isochrones": IsochronesComponent,
    "map-heatmaps": HeatmapsComponent,
    "map-layertree": LayerTree
  },
  mixins: [Isochrones],
  name: "left-panel",
  data: () => ({
    logo: "img/logo.png",
    logoText: "img/goat_white.svg",
    drawer: true,
    mini: false,
    responsive: false,
    topTabIndex: 0,
    componentNames: ["map-isochrones", "map-heatmaps", "map-layertree"],
    tabKey: 0
  }),
  computed: {
    getColor() {
      return this.mini === true ? this.appColor.primary : "";
    },
    ...mapGetters("isochrones", {
      selectedThematicData: "selectedThematicData",
      calculations: "calculations"
    }),
    ...mapGetters("app", {
      appColor: "appColor",
      calculationMode: "calculationMode"
    }),
    ...mapFields("app", {
      calculationMode: "calculationMode",
      layerTabIndex: "layerTabIndex"
    })
  },
  watch: {
    selectedThematicData(calculation) {
      if (calculation) {
        this.calculations.forEach(value => {
          if (value.id !== calculation.calculationId) {
            value.isExpanded = false;
          } else {
            value.isExpanded = true;
          }
        });
        const scrollEl = this.$refs["vs"];
        setTimeout(() => {
          scrollEl.scrollIntoView(`#result-${calculation.calculationId}`, 300);
        }, 100);
      }
    },
    mini() {
      this.$nextTick(() => {
        setTimeout(() => {
          this.tabKey = this.tabKey + 1;
        }, 150);
      });
    }
  }
};
</script>
<style lang="css">
.toolbar {
  font-weight: bold;
  font-size: 18px;
}
.toolbar .text {
  color: white;
  text-decoration: none;
}

.rotate {
  transform: rotate(-90deg);
}

.right-shadow {
  box-shadow: rgba(0, 0, 0, 0.3) 0px 0px 20px;
}
</style>
