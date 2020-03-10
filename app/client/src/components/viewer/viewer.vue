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
        <div id="close-miniview" @click="closeMiniView()">
          <v-icon dark class="close-icon">close</v-icon>
        </div>
        <div id="switch-triangle" @click="switchViews()">
          <v-icon large dark class="swap-icon">swap_horiz</v-icon>
        </div>
        <component
          class="strech"
          v-bind:is="activeMiniViewComponent"
        ></component> </v-card
    ></v-expand-x-transition>
    <isochrone-thematic-data />
    <!-- FULL-VIEW -->
    <component class="strech" v-bind:is="activeFullViewComponent"></component>
  </div>
</template>
<script>
import appMap from "./ol/Map";
import appMapillary from "./mapillary/Mapillary";
import IsochronThematicData from "./others/IsochroneThematicData";

export default {
  name: "app-viewer",
  components: {
    "app-ol-map": appMap,
    "app-mapillary": appMapillary,
    "isochrone-thematic-data": IsochronThematicData
  },
  data() {
    return {
      miniViewerVisible: false,
      activeFullViewComponent: "app-ol-map",
      activeMiniViewComponent: "app-mapillary"
    };
  },
  methods: {
    showMiniViewer() {
      this.miniViewerVisible = true;
    },
    switchViews() {
      [this.activeFullViewComponent, this.activeMiniViewComponent] = [
        this.activeMiniViewComponent,
        this.activeFullViewComponent
      ];
    },
    closeMiniView() {
      this.miniViewerVisible = false;
      this.activeFullViewComponent = "app-ol-map";
      this.activeMiniViewComponent = "app-mapillary";
    }
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
  background: rgba(0, 0, 0, 0.5);
  transform: rotate(45deg);
  z-index: 2;
  cursor: pointer;
}

.swap-icon {
  position: absolute;
  bottom: -5px;
  right: 35px;
}

#close-miniview {
  content: "";
  position: absolute;
  top: 5px;
  left: 5px;
  border-radius: 15px;
  height: 24px;
  width: 24px;
  opacity: 0.8;
  background: rgba(0, 0, 0, 0.5);
  z-index: 2;
  cursor: pointer;
}

.close-icon {
  position: absolute;
}
</style>
