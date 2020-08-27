<template>
  <div>
    <!-- TOGGLE STREET VIEW -->
    <v-tooltip right>
      <template v-slot:activator="{ on }">
        <v-btn
          v-show="!miniViewerVisible"
          v-if="isMapillaryButtonActive"
          class="mx-2 miniviewer-button"
          fab
          dark
          small
          :color="activeColor.primary"
          @click="showMiniViewer"
          :loading="isMapillaryBtnDisabled"
          v-on="on"
        >
          <v-icon dark>streetview</v-icon>
        </v-btn>
      </template>
      <span>{{ $t(`map.tooltips.toggleStreetView`) }}</span>
    </v-tooltip>

    <!-- ISOCHRONES-THEMATIC-DATA -->
    <isochrone-thematic-data v-show="!miniViewOlMap" />

    <!-- MAPILLARY-->
    <div
      v-if="miniViewerVisible"
      class="elevation-4"
      :class="miniViewOlMap ? 'fullscreen' : 'miniview'"
    >
      <div v-if="!miniViewOlMap" id="close-miniview" @click="closeMiniView()">
        <v-icon dark class="close-icon">close</v-icon>
      </div>
      <div v-if="!miniViewOlMap" id="switch-triangle" @click="switchViews()">
        <v-icon large dark class="swap-icon">swap_horiz</v-icon>
      </div>
      <app-mapillary
        ref="mapillary"
        class="fullscreen"
        v-if="miniViewerVisible"
        :startImageKey="mapillaryStartImageKey"
        :startSequenceKey="mapillarySequenceKey"
        :organization_key="mapillaryOrganizationKey"
        :clientId="mapillaryClientId"
        :baseLayerExtent="mapillaryTileBaseLayerExtent"
      ></app-mapillary>
    </div>

    <!-- OL MAP -->
    <div :class="miniViewOlMap ? 'miniview' : 'fullscreen'">
      <div v-if="miniViewOlMap" id="close-miniview" @click="closeMiniView()">
        <v-icon dark class="close-icon">close</v-icon>
      </div>
      <div v-if="miniViewOlMap" id="switch-triangle" @click="switchViews()">
        <v-icon large dark class="swap-icon">swap_horiz</v-icon>
      </div>
      <app-ol-map
        :miniViewOlMap="miniViewOlMap"
        class="fullscreen"
        ref="olmap"
      ></app-ol-map>
    </div>
  </div>
</template>

<script>
import appMap from "./ol/Map";
import appMapillary from "./mapillary/Mapillary";
import IsochronThematicData from "./others/IsochroneThematicData";
import { toLonLat } from "ol/proj";
import { mapGetters } from "vuex";
import axios from "axios";
import { getCenter } from "ol/extent";

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
      miniViewOlMap: false,
      // Mapillary Keys
      mapillaryClientId: "V1Qtd0JKNGhhb1J1cktMbmhFSi1iQTo5ODMxOWU3NmZlMjEyYTA3",
      mapillaryOrganizationKey: "RmTboeISWnkEaYaSdtVRHp",
      mapillaryImgAPI: "https://a.mapillary.com/v3/images",
      mapillaryTileBaseLayerExtent: this.$appConfig.map.originalExtent,
      mapillaryStartImageKey: null,
      mapillarySequenceKey: null,
      isMapillaryBtnDisabled: true,
      isMapillaryButtonActive: true
    };
  },
  computed: {
    ...mapGetters("app", {
      activeColor: "activeColor"
    })
  },
  mounted() {
    if (this.$appConfig.map.center) {
      const coordinates = toLonLat(getCenter(this.$appConfig.map.extent));
      axios
        .get(this.mapillaryImgAPI, {
          params: {
            client_id: this.mapillaryClientId,
            closeto: [coordinates[0], coordinates[1]].toString(),
            radius: 150
          }
        })
        .then(response => {
          if (response.data) {
            this.isMapillaryBtnDisabled = false;
            const closestFeature = response.data.features[0];
            this.mapillaryStartImageKey = closestFeature.properties.key;
            this.mapillarySequenceKey = closestFeature.properties.sequence_key;
          }
        })
        .catch(() => {
          this.isMapillaryButtonActive = false;
        });
    }
  },
  methods: {
    showMiniViewer() {
      this.miniViewerVisible = true;
    },
    switchViews() {
      this.miniViewOlMap = !this.miniViewOlMap;
      this.updateViews();
    },
    updateViews() {
      setTimeout(() => {
        const mapillaryRef = this.$refs["mapillary"];
        const olMapRef = this.$refs["olmap"];
        if (mapillaryRef) {
          mapillaryRef.mapillary.resize();
        }
        if (olMapRef) {
          olMapRef.map.updateSize();
        }
      }, 90);
    },
    closeMiniView() {
      this.miniViewerVisible = false;
      this.miniViewOlMap = false;
      this.updateViews();
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

.fullscreen {
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
  z-index: 10;
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
  z-index: 20;
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
  z-index: 20;
  cursor: pointer;
}

.close-icon {
  position: absolute;
}
</style>
