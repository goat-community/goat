<template>
  <v-flex xs12>
    <!-- Isochrone Options -->
    <v-card-text class="pr-16 pl-16 pt-0 pb-0">
      <v-divider></v-divider>
    </v-card-text>
    <v-subheader
      class="clickable"
      @click="isOptionsElVisible = !isOptionsElVisible"
    >
      <v-icon
        :style="isOptionsElVisible === true ? { color: '#30c2ff' } : {}"
        small
        class="mr-2"
        >fas fa-sliders-h</v-icon
      >
      <h3>{{ $t("isochrones.options.title") }}</h3>
    </v-subheader>
    <div v-if="isOptionsElVisible">
      <v-subheader
        class="clickable isochroneOptionsHeader ml-1 py-1 mb-2 "
        @click="isIsochroneOptionsVisible = !isIsochroneOptionsVisible"
      >
        <v-icon
          small
          class="mr-2"
          v-html="
            isIsochroneOptionsVisible
              ? 'fas fa-chevron-down'
              : 'fas fa-chevron-right'
          "
        ></v-icon>
        <h4>{{ $t("isochrones.options.subOptions") }}</h4>
      </v-subheader>
      <v-expand-transition>
        <v-flex
          xs12
          class="mx-4 isochroneOptions"
          v-if="isIsochroneOptionsVisible"
        >
          <v-slider
            min="1"
            max="20"
            inverse-label
            v-model="minutes"
            prepend-icon="fas fa-clock"
            :label="minutes + ' min'"
            color="#30C2FF"
          >
          </v-slider>
          <v-slider
            min="1"
            max="25"
            inverse-label
            v-model="speed"
            prepend-icon="fas fa-tachometer-alt"
            :label="speed + ' km/h'"
            color="#30C2FF"
          >
          </v-slider>

          <v-slider
            class="mb-1"
            v-model="steps"
            min="1"
            max="4"
            inverse-label
            prepend-icon="fas fa-sort-numeric-up"
            :label="`${$t('isochrones.isochrones')} (${steps})`"
            color="#30C2FF"
          >
          </v-slider>
        </v-flex>
      </v-expand-transition>
    </div>
  </v-flex>
</template>
<script>
import { mapGetters, mapMutations } from "vuex";
import { mapFields } from "vuex-map-fields";
import { EventBus } from "../../EventBus";
import { Isochrones } from "../../mixins/Isochrones";

export default {
  name: "isochrone-options",
  mixins: [Isochrones],
  data: () => ({
    isOptionsElVisible: true,
    isIsochroneOptionsVisible: true
  }),
  computed: {
    ...mapGetters("isochrones", {
      options: "options",
      scenarioDataTable: "scenarioDataTable",
      activeScenario: "activeScenario",
      activeRoutingProfile: "activeRoutingProfile"
    }),
    ...mapGetters("map", {
      layers: "layers"
    }),
    ...mapGetters("pois", {
      selectedPois: "selectedPois"
    }),
    ...mapFields("isochrones", {
      minutes: "options.minutes",
      speed: "options.speed",
      steps: "options.steps",
      calculationModes: "options.calculationModes.active",
      alphaShapeParameter: "options.alphaShapeParameter.active"
    })
  },
  mounted() {
    EventBus.$on("updateHeatmapPois", this.updateLayersParam("pois"));
  },
  methods: {
    filterCalcModeValues() {
      return this.options.calculationModes.values;
    },
    updateLayersParam(param) {
      let pois = "";
      if (param === "pois") {
        pois = this.selectedPois.reduce((filtered, item) => {
          const { value, weight, sensitivity } = item;
          if (value != "undefined" && weight != undefined) {
            filtered[`${value}`] = { sensitivity, weight };
          }
          return filtered;
        }, {});
      }
      Object.keys(this.layers).forEach(key => {
        // Change style
        const stylesRefs = this.layers[key].get("styles");
        if (stylesRefs && stylesRefs[this.calculationModes]) {
          const STYLES = stylesRefs[this.calculationModes];
          this.layers[key].getSource().updateParams({
            STYLES
          });
          this.layers[key].getSource().refresh();
        }
        // Change view params
        if (this.layers[key].get("viewparamsDynamicKeys")) {
          const layerParams = this.layers[key].getSource().getParams();
          let viewparams = layerParams.viewparams;
          if (!viewparams) {
            viewparams = ``;
          }

          // Add/update modus
          if (
            this.layers[key].get("viewparamsDynamicKeys").includes("modus") &&
            ["modus", undefined].includes(param)
          ) {
            const value = this.calculationModes;
            if (this.layers[key].getSource().getParams()) {
              if (!viewparams.includes("modus")) {
                viewparams += `modus:'${value}';`;
              } else {
                viewparams = viewparams.replace(
                  /modus:(.*?)(?=;)/i,
                  `modus:'${value}'`
                );
              }
            }
          }

          // Add/update scenario_id
          if (
            this.layers[key]
              .get("viewparamsDynamicKeys")
              .includes("scenario_id") &&
            ["scenario_id", undefined].includes(param) &&
            this.activeScenario
          ) {
            const value = parseInt(this.activeScenario);
            if (!viewparams.includes("scenario_id")) {
              viewparams += `scenario_id:${value};`;
            } else {
              viewparams = viewparams.replace(
                /scenario_id:(.*?)(?=;)/i,
                `scenario_id:${value}`
              );
            }
          }

          // Add/update routing_profile
          if (
            this.layers[key]
              .get("viewparamsDynamicKeys")
              .includes("routing_profile") &&
            ["routing_profile", undefined].includes(param)
          ) {
            const value = this.activeRoutingProfile;
            if (!viewparams.includes("routing_profile")) {
              viewparams += `routing_profile:'${value}';`;
            } else {
              viewparams = viewparams.replace(
                /routing_profile:(.*?)(?=;)/i,
                `routing_profile:'${value}'`
              );
            }
          }

          // Add/update pois
          if (
            this.layers[key].get("viewparamsDynamicKeys").includes("pois") &&
            ["pois", undefined].includes(param)
          ) {
            if (!viewparams.includes("amenities")) {
              viewparams += `amenities:'${btoa(JSON.stringify(pois))}';`;
            } else {
              viewparams = viewparams.replace(
                /amenities:(.*?)(?=;)/i,
                `amenities:'${btoa(JSON.stringify(pois))}'`
              );
            }
            if (
              this.layers[key].getVisible() === true &&
              viewparams.length === 0
            ) {
              this.toggleSnackbar({
                type: "error",
                message: "selectAmenities",
                timeout: 60000,
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
          }

          // Update view params
          this.layers[key].getSource().updateParams({
            viewparams
          });
          if (param === "pois") {
            this.layers[key].getSource().refresh();
          }
        }
      });
    },
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
    })
  },
  watch: {
    calculationModes() {
      this.updateLayersParam("modus");
    },
    activeScenario() {
      this.updateLayersParam("scenario_id");
    },
    selectedPois() {
      this.updateLayersParam("pois");
    },
    activeRoutingProfile() {
      this.updateLayersParam("routing_profile");
    }
  },
  created() {
    setTimeout(() => {
      // Add/update all
      this.updateLayersParam(undefined);
    }, 500);
  }
};
</script>
<style lang="css">
.isochroneOptionsHeader {
  height: auto;
}
.isochroneOptions .v-input--slider .v-label {
  font-weight: bold !important;
}
.isochroneOptions .v-icon {
  font-size: 18px;
}

.isochroneOptions .v-input--slider {
  margin-top: 0px;
}
</style>
