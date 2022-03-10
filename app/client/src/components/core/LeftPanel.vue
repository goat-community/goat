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
      <template v-if="!mini">
        <v-app-bar flat class="toolbar" :color="appColor.primary" height="50">
          <img id="app-logo" :src="logoText" width="120px" />
          <v-spacer></v-spacer>
          <v-btn text icon light @click.stop="mini = !mini">
            <v-icon small color="white">fas fa-chevron-left</v-icon>
          </v-btn>
        </v-app-bar>
        <v-tabs
          grow
          :color="appColor.secondary"
          class="elevation-3"
          v-model="topTabIndex"
        >
          <v-tab>
            Isochrones
          </v-tab>
          <v-tab>
            Heatmaps
          </v-tab>
          <v-tab>
            Static Layers
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
              <b>All Layers</b>
            </v-badge>
          </v-tab>
          <v-tab>
            <v-badge>
              <b>Active Layers</b>
            </v-badge>
          </v-tab>
        </v-tabs>

        <vue-scroll ref="vs">
          <v-layout
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

        <v-layout align-end>
          <div class="text-center elevation-5 py-2" style="width:100%;">
            <v-chip
              v-for="(item, index) in calculationMode.values"
              style="cursor:pointer;width:100px;justify-content:center;"
              :color="calculationMode.active === item ? appColor.primary : ''"
              @click="selectCalculationMode(item)"
              :key="index"
              :class="{
                'subtitle-2 ma-2': true,
                'white--text': calculationMode.active === item
              }"
            >
              {{
                $te(`isochrones.options.${item}`)
                  ? $t(`isochrones.options.${item}`)
                  : item
              }}
            </v-chip>
          </div>
        </v-layout>
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
    logoText: "img/logo_white.png",
    drawer: true,
    mini: false,
    responsive: false,
    topTabIndex: 0,
    componentNames: ["map-isochrones", "map-heatmaps", "map-layertree"]
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
  mounted() {},
  beforeDestroy() {},
  methods: {
    selectCalculationMode(mode) {
      this.calculationMode.active = mode;
      this.canCalculateScenario(mode);
    }
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