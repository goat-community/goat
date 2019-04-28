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

        <v-bottom-nav
          color="green"
          flat
          value="true"
          height="50"
          absolute
          dark
          shift
        >
          <v-btn dark>
            <span>Layers</span>
            <v-icon>fas fa-layer-group</v-icon>
          </v-btn>
          <v-btn dark>
            <span>Isochrones</span>
            <v-icon>fas fa-bullseye</v-icon>
          </v-btn>
        </v-bottom-nav>
      </template>
    </v-layout>
  </v-navigation-drawer>
</template>

<script>
// Utilities
import {} from "vuex";
export default {
  name: "tree-panel",
  data: () => ({
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
