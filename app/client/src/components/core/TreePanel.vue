<template>
  <v-navigation-drawer
    id="tree-panel"
    v-model="drawer"
    :mini-variant.sync="mini"
    app
    persistent
    left
    hide-overlay
    mini-variant-width="50"
    width="350"
  >
    <v-layout v-bind:class="getColor" justify-space-between column fill-height>
      <template v-if="mini">
        <v-btn flat icon light @click.stop="mini = !mini">
          <v-icon color="white">fas fa-chevron-right</v-icon>
        </v-btn>
      </template>
      <template v-if="!mini">
        <v-toolbar flat class="toolbar green" height="50">
          <img :src="logo" width="40px" />
          <v-toolbar-title class="white--text">GOAT</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn flat icon light @click.stop="mini = !mini">
            <v-icon color="white">fas fa-chevron-left</v-icon>
          </v-btn>
        </v-toolbar>

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

        <v-layout align-end>
          <v-bottom-nav
            color="green"
            flat
            value="true"
            :active.sync="activeComponent"
            height="50"
            dark
          >
            <v-btn color="#30C2FF" flat value="map-isochrones">
              <span>Isochrones</span>
              <v-icon>fas fa-bullseye</v-icon>
            </v-btn>
            <v-btn color="#30C2FF" flat value="map-layertree">
              <span>Layers</span>
              <v-icon>fas fa-layer-group</v-icon>
            </v-btn>
          </v-bottom-nav>
        </v-layout>
      </template>
    </v-layout>
  </v-navigation-drawer>
</template>

<script>
// Utilities
import Isochrones from "../isochrones/isochrones";
import LayerTree from "../layers/layerTree/layerTree";
export default {
  components: {
    "map-isochrones": Isochrones,
    "map-layertree": LayerTree
  },
  name: "tree-panel",
  data: () => ({
    activeComponent: "map-isochrones",
    logo: "logo.png",
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
<style>
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
</style>
