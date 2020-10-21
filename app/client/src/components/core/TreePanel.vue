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
    width="350"
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
        <v-app-bar
          flat
          class="toolbar"
          :color="activeColor.primary"
          height="50"
        >
          <img :src="logo" width="35px" />
          <img :src="logoText" class="pt-1" width="95px" />
          <v-spacer></v-spacer>
          <v-btn text icon light @click.stop="mini = !mini">
            <v-icon color="white">fas fa-chevron-left</v-icon>
          </v-btn>
        </v-app-bar>
        <toolbar v-show="!osmMode"></toolbar>
        <vue-scroll v-show="!osmMode" ref="vs">
          <v-layout
            v-show="!osmMode"
            justify-space-between
            column
            fill-height
            style="overflow-y: auto;"
          >
            <keep-alive>
              <component v-bind:is="activeComponent"></component>
            </keep-alive>
          </v-layout>
        </vue-scroll>

        <v-layout v-show="!osmMode" align-end>
          <v-bottom-navigation
            :background-color="activeColor.primary"
            flat
            horizontal
            dark
            grow
            value="true"
            v-model="activeComponent"
            height="50"
          >
            <v-btn text value="map-isochrones">
              <span style="font-size: 0.85rem;">{{
                $t("isochrones.title")
              }}</span>
              <v-icon>fas fa-bullseye</v-icon>
            </v-btn>
            <v-btn text value="map-layertree">
              <span style="font-size: 0.85rem;">{{
                $t("layerTree.title")
              }}</span>
              <v-icon>fas fa-layer-group</v-icon>
            </v-btn>
          </v-bottom-navigation>
        </v-layout>

        <!-- OSM MODE TASKS -->
        <osm-mode v-if="osmMode"></osm-mode>
      </template>
    </v-layout>
  </v-navigation-drawer>
</template>

<script>
// Utilities
import IsochronesComponent from "../isochrones/Isochrones";
import LayerTree from "../layers/layerTree/LayerTree";
import Toolbar from "./Toolbar";
import OsmMode from "./OsmMode";
import { mapGetters, mapMutations } from "vuex";
import { Isochrones } from "../../mixins/Isochrones";

export default {
  components: {
    "map-isochrones": IsochronesComponent,
    "map-layertree": LayerTree,
    toolbar: Toolbar,
    "osm-mode": OsmMode
  },
  mixins: [Isochrones],
  name: "tree-panel",
  data: () => ({
    activeComponent: "map-isochrones",
    logo: "img/logo.png",
    logoText: "img/logo_text.png",
    drawer: true,
    mini: false,
    responsive: false
  }),
  computed: {
    getColor() {
      return this.mini === true ? this.activeColor.primary : "";
    },
    ...mapGetters("isochrones", {
      selectedThematicData: "selectedThematicData",
      calculations: "calculations"
    }),
    ...mapGetters("map", {
      osmMode: "osmMode"
    }),
    ...mapGetters("app", {
      activeColor: "activeColor"
    })
  },
  mounted() {},
  beforeDestroy() {},
  methods: {
    ...mapMutations("isochrones", {
      init: "INIT"
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
    }
  },
  created() {
    this.init(this.$appConfig.componentData.isochrones);
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
