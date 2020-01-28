<template>
  <div>
    <!-- TOGGLE STREET VIEW -->
    <v-btn
      v-if="!miniViewerVisible"
      class="mx-2 miniviewer-button"
      fab
      dark
      small
      color="green"
      @click="showMiniViewer"
    >
      <v-icon dark>streetview</v-icon>
    </v-btn>

    <!-- MINI-VIEW -->
    <v-expand-x-transition>
      <v-card v-if="miniViewerVisible" class="miniview" outlined>
        <div id="switch-triangle" @click="switchViews()">
          <v-icon large dark class="swap-icon">swap_horiz</v-icon>
        </div>
        <component
          class="strech"
          v-bind:is="activeMiniViewComponent"
        ></component> </v-card
    ></v-expand-x-transition>

    <!-- FULL-VIEW -->
    <component class="strech" v-bind:is="activeFullViewComponent"></component>
  </div>
</template>
<script>
import appMap from "./ol/Map";
import appMapillary from "./mapillary/Mapillary";
export default {
  name: "app-viewer",
  components: {
    "app-ol-map": appMap,
    "app-mapillary": appMapillary
  },
  data() {
    return {
      miniViewerVisible: false,
      activeMiniViewComponent: "app-mapillary",
      activeFullViewComponent: "app-ol-map"
    };
  },
  methods: {
    showMiniViewer() {
      this.miniViewerVisible = true;
    },
    switchViews() {}
  }
};
</script>
<style lang="css" scoped>
.switch-button {
  position: absolute;
  top: 10px;
  right: 2px;
  z-index: 1;
}

.miniviewer-button {
  position: absolute;
  top: 150px;
  left: 8px;
  z-index: 1;
}

.strech {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.miniview {
  position: absolute;
  top: 8px;
  left: 8px;
  right: 8px;

  height: 300px;
  max-height: 40%;
  max-width: 500px;

  overflow: hidden;
  opacity: 1;
  z-index: 1;
  background-color: white;
  box-shadow: 0 0 4px #00000060;
  border-radius: 8px;
  z-index: 3;
}

#switch-triangle {
  content: "";
  position: absolute;
  top: -60px;
  right: -60px;
  height: 100px;
  width: 100px;
  opacity: 0.8;
  background: #474a4e;
  transform: rotate(45deg);
  z-index: 2;
  cursor: pointer;
}

.swap-icon {
  position: absolute;
  bottom: -5px;
  right: 35px;
}
</style>
