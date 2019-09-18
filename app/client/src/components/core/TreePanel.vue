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
    <v-layout v-bind:class="getColor" justify-space-between column fill-height>
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
        <v-app-bar flat class="toolbar green" height="50">
          <img :src="logo" width="40px" />
          <v-toolbar-title class="white--text">GOAT</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn text icon light @click.stop="mini = !mini">
            <v-icon color="white">fas fa-chevron-left</v-icon>
          </v-btn>
        </v-app-bar>

        <vue-scroll>
          <v-layout
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

        <v-layout align-end>
          <v-bottom-navigation
            background-color="green"
            flat
            dark
            grow
            value="true"
            v-model="activeComponent"
            height="50"
          >
            <v-btn color="#30C2FF" text value="map-isochrones">
              <span>{{ $t("isochrones.title") }}</span>
              <v-icon>fas fa-bullseye</v-icon>
            </v-btn>
            <v-btn color="#30C2FF" text value="map-layertree">
              <span>{{ $t("layerTree.title") }}</span>
              <v-icon>fas fa-layer-group</v-icon>
            </v-btn>
          </v-bottom-navigation>
        </v-layout>
      </template>
    </v-layout>
  </v-navigation-drawer>
</template>

<script>
// Utilities
import Isochrones from "../isochrones/Isochrones";
import LayerTree from "../layers/layerTree/LayerTree";
export default {
  components: {
    "map-isochrones": Isochrones,
    "map-layertree": LayerTree
  },
  name: "tree-panel",
  data: () => ({
    activeComponent: "map-isochrones",
    logo: "img/logo.png",
    drawer: true,
    mini: false,
    responsive: false
  }),
  computed: {
    getColor() {
      return this.mini === true ? "green" : "";
    }
  },
  mounted() {},
  beforeDestroy() {},
  methods: {}
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
