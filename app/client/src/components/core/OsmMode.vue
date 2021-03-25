<template>
  <v-layout justify-space-between column fill-height style="overflow-y: auto;">
    <vue-scroll>
      <!-- ACTIVE TASK LIST  -->
      <div v-if="!activeLayer">
        <div v-for="(layer, index) in this.osmMappingLayers" :key="index">
          <v-list max-width="350" two-line class="py-0 mb-0">
            <v-divider></v-divider>
            <v-list-item class="elevation-2" @click="setActiveLayer(layer)">
              <v-list-item-icon v-if="layer.get('otherProps')">
                <v-icon>{{ layer.get("otherProps").icon }}</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title class="subtitle-1 font-weight-medium">
                  {{ getTitle(layer.get("name")) }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ getShortDesc(layer.get("name")) }}
                </v-list-item-subtitle>
              </v-list-item-content>
              <v-list-item-action>
                <v-icon>fas fa-chevron-right</v-icon>
              </v-list-item-action>
              <!-- <v-progress-linear
                v-if="layer.get('currentNumberOfFeatures')"
                style="position:absolute;bottom:0px;left:0px;"
                :value="getProgresPercentage(layer)"
              >
              </v-progress-linear> -->
            </v-list-item>
          </v-list>
        </div>
      </div>

      <!-- ACTIVE TASK -->
      <div v-if="activeLayer">
        <v-layout>
          <v-btn
            text
            icon
            class="mt-1 ml-1"
            light
            @click="setActiveLayer(null)"
          >
            <v-icon color="rgba(0,0,0,0.54)">fas fa-arrow-left</v-icon>
          </v-btn>
          <v-subheader class="ml-1 pb-1 pl-0">
            <span class="title">{{ getTitle(activeLayer.get("name")) }}</span>
          </v-subheader>
        </v-layout>
        <v-divider></v-divider>

        <v-alert
          border="left"
          colored-border
          class="mb-0 mt-2 mx-1 elevation-2"
          icon="info"
          :color="activeColor.primary"
          dense
        >
          <span v-html="getLongDesc(activeLayer.get('name'))"></span>
        </v-alert>

        <v-subheader>
          <v-icon small class="mr-2">fas fa-tasks</v-icon>
          <h3>{{ $t(`map.osmMode.steps`) }}</h3>
        </v-subheader>
        <v-divider class="mx-4 mt-0 pt-0"></v-divider>

        <ul class="ml-3 mt-2" id="steps">
          <!-- FOR LAYER THAT DON'T HAVE SPECIFIC STEPS DEFINED -->
          <template v-if="!activeLayer.get('otherProps').stepsOrdersKeys">
            <li
              v-for="(value, key, index) in $t(`map.osmMode.stepsDesc`)"
              :key="index"
              v-html="getTranslatedDesc(value)"
            ></li>
          </template>
          <!-- IT OVERWRITES THE DEFAULT STEPS -->
          <template v-else>
            <li
              v-for="(value, key, index) in activeLayer.get('otherProps')
                .stepsOrdersKeys"
              :key="index"
              v-html="getTranslatedDesc(value)"
            ></li>
          </template>
        </ul>

        <v-divider class="mx-4 mt-2 pt-0"></v-divider>
        <div class="red--text mx-3 pt-3">
          <i>{{ getNoteMessage(activeLayer.get("name")) }}</i>
        </div>
        <v-divider class="mx-4 mt-2 pt-0"></v-divider>
        <div class="mx-3 pt-3 text-right">
          <a
            v-if="activeLayer.get('otherProps').wikiUrl"
            style="text-decoration:none;"
            :href="activeLayer.get('otherProps').wikiUrl"
            target="_blank"
            title=""
          >
            <i class="fas fa-passport"></i> OSM Wiki</a
          >
        </div>
      </div>
    </vue-scroll>
    <v-layout align-end>
      <v-bottom-navigation
        :background-color="activeColor.primary"
        flat
        horizontal
        dark
        grow
        value="true"
        height="50"
      >
        <div class="pt-3">
          <v-icon>fas fa-tasks</v-icon>
          <span class="ml-2 subtitle-1" style="font-size: 0.85rem;">
            {{ $t("map.osmMode.tasks") }}
          </span>
        </div>
      </v-bottom-navigation>
    </v-layout>
  </v-layout>
</template>

<script>
import { mapGetters, mapMutations, mapActions } from "vuex";
import { EventBus } from "../../EventBus";

export default {
  data: () => ({
    activeLayer: null,
    osmMappingLayers: {}
  }),
  created() {
    this.osmMapMode = this.$appConfig.componentData.osmMapMode;
    this.toggleNodeState({
      excluded: this.disabledPoisOnMappingMode,
      nodeState: "activate"
    });
  },
  beforeDestroy() {
    this.setActiveLayer(null);
    this.toggleNodeState({
      excluded: this.disabledPoisOnMappingMode,
      nodeState: "deactivate"
    });
  },
  computed: {
    ...mapGetters("map", {
      layers: "layers",
      map: "map"
    }),
    ...mapGetters("pois", {
      selectedPois: "selectedPois",
      disabledPoisOnMappingMode: "disabledPoisOnMappingMode"
    }),
    ...mapGetters("app", {
      activeColor: "activeColor"
    })
  },
  methods: {
    setActiveLayer(layer) {
      // Turn off all other layers.
      const osmLayerKeys = Object.keys(this.osmMappingLayers);
      osmLayerKeys.forEach(layerKey => {
        this.osmMappingLayers[layerKey].setVisible(false);
      });
      // Close popup
      EventBus.$emit("close-popup");
      if (layer) {
        layer.setVisible(true);
      }

      this.activeLayer = layer;
      // (Workaround) Watch is not accessible on component destory so are forced to add this here
      if (
        this.selectedPois.length === 0 &&
        this.poisLayer.getVisible() === true
      ) {
        this.toggleSnackbar({
          type: "error",
          message: "selectAmenities",
          timeout: 8000,
          state: true
        });
      } else {
        this.toggleSnackbar({
          type: "error",
          message: "selectAmenities",
          state: false,
          timeout: 0
        });
      }
    },
    getTitle(layerName) {
      const path = `map.osmMode.layers.${layerName}`;
      const canTranslate = this.$te(`${path}.layerName`);
      if (canTranslate) {
        return (
          this.$t(`${path}.layerName`) +
          " - " +
          this.$t(`${path}.missingKeyWord`)
        );
      } else {
        return layerName;
      }
    },
    getDesc(descPath, layerName) {
      const missingDataKeywordPath = `map.osmMode.layers.${layerName}.missingKeyWord`;
      const layerNameVar = `map.osmMode.layers.${layerName}.layerName`;
      const canTranslateDesc = this.$te(descPath);
      const canTranslateMissingKeyword = this.$te(missingDataKeywordPath);
      const canTranslateLayerName = this.$te(layerNameVar);

      if (
        canTranslateDesc &&
        canTranslateMissingKeyword &&
        canTranslateLayerName
      ) {
        return this.$t(descPath, {
          missingVar: this.$t(missingDataKeywordPath),
          layerNameVar: this.$t(layerNameVar)
        });
      } else {
        return ``;
      }
    },
    getShortDesc(layerName) {
      const descPath = `map.osmMode.shortDesc`;
      return this.getDesc(descPath, layerName);
    },
    getLongDesc(layerName) {
      const longDesc = `map.osmMode.shortDesc`;
      return this.getDesc(longDesc, layerName);
    },
    getNoteMessage(layerName) {
      const noteMessagePath = `map.osmMode.note`;
      return this.$t(noteMessagePath, {
        layerNameVar: this.$t(`map.osmMode.layers.${layerName}.layerName`)
      });
    },
    getProgresPercentage(layer) {
      const currentNumberOfFeatures = layer.get("currentNumberOfFeatures");
      const initialNumberOfFeatures =
        layer.get("initialNumberOfFeatures") || currentNumberOfFeatures;
      const value =
        (parseFloat(currentNumberOfFeatures) /
          parseFloat(initialNumberOfFeatures)) *
        100;
      return value;
    },
    updatePoisQueryParams() {
      if (this.selectedPois.length > 0) {
        this.toggleSnackbar({
          type: "error",
          message: "selectAmenities",
          state: false,
          timeout: 0
        });
      }
      EventBus.$emit("updateLayer", this.poisLayer);
    },
    getTranslatedDesc(descKey) {
      const layerName = this.activeLayer.get("name");
      const layerTranslateDescKey = `map.osmMode.layers.${layerName}.stepsDesc.${descKey}`;
      const defaultTranslateDescKey = `map.osmMode.stepsDesc.${descKey}`;
      if (this.$te(layerTranslateDescKey)) {
        return this.$t(layerTranslateDescKey, {
          missingVar: this.$t(`map.osmMode.layers.${layerName}.missingKeyWord`)
        });
      } else if (this.$te(defaultTranslateDescKey)) {
        return this.$t(defaultTranslateDescKey, {
          missingVar: this.$t(`map.osmMode.layers.${layerName}.missingKeyWord`)
        });
      } else {
        return descKey;
      }
    },
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
    }),
    ...mapMutations("pois", {
      toggleNodeState: "TOGGLE_NODE_STATE"
    }),
    ...mapActions("pois", {
      updateSelectedPoisForThematicData: "updateSelectedPoisForThematicData"
    })
  },
  watch: {
    selectedPois() {
      this.updatePoisQueryParams();
    },
    activeLayer() {}
  },
  mounted() {
    // Turn off other layers.
    const allLayerKeys = Object.keys(this.layers);
    allLayerKeys.forEach(layerKey => {
      const layer = this.layers[layerKey];
      if (
        layer.get("group") !== "backgroundLayers" &&
        layer.get("displayInLayerList") === true
      ) {
        layer.setVisible(false);
      }
      if (layer.get("group") === "osmMappingLayers") {
        this.osmMappingLayers[layer.get("name")] = layer;
      }
    });

    // Update pois layer params.
    if (this.osmMappingLayers["mapping_pois_opening_hours"]) {
      this.poisLayer = this.osmMappingLayers["mapping_pois_opening_hours"];
      // Update query params
      this.updatePoisQueryParams();
    }
    this.$forceUpdate();
  },
  destroyed() {
    // Turn off all other layers.
    const osmLayerKeys = Object.keys(this.osmMappingLayers);
    osmLayerKeys.forEach(layerKey => {
      this.osmMappingLayers[layerKey].setVisible(false);
    });
    this.updateSelectedPoisForThematicData([]);
  }
};
</script>

<style></style>
