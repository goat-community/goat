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
import { updateLayerUrlQueryParam } from "../../utils/Layer";
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
    }),
    getPois() {
      let pois = "";

      pois = this.selectedPois.reduce((filtered, item) => {
        const { value, weight, sensitivity } = item;
        if (value != "undefined" && weight != undefined) {
          filtered[`${value}`] = { sensitivity, weight };
        }
        return filtered;
      }, {});

      return pois;
    }
  },
  mounted() {
    EventBus.$on("toggleLayerVisiblity", this.updateLayer);
    EventBus.$on("updateHeatmapPois", this.updateLayersParam);
  },
  methods: {
    filterCalcModeValues() {
      return this.options.calculationModes.values;
    },
    updateLayer(layer) {
      if (!layer.getVisible()) return;
      const newQueryParams = {};
      let isValid = true;
      const pois = this.getPois;
      const queryParams = layer.get("queryParams");
      // Add/update aois_input
      // TODO: Remove hardcoded values.
      if (queryParams.includes("aois_input")) {
        newQueryParams["aois_input"] = `'{"park","river"}'`;
      }

      // Add/update amenities query params
      if (
        queryParams.includes("amenities_json") ||
        queryParams.includes("pois")
      ) {
        if (Object.keys(pois).length === 0) {
          this.toggleSnackbar({
            type: "error",
            message: "selectAmenities",
            timeout: 60000,
            state: true
          });
          isValid = false;
        } else {
          this.toggleSnackbar({
            type: "error",
            message: "selectAmenities",
            state: false,
            timeout: 0
          });
        }
        const value = `'${JSON.stringify(pois)}'`;
        //TODO: Make this consistent (remove pois or amenities_json accross all layers.)
        queryParams.includes("amenities_json")
          ? (newQueryParams["amenities_json"] = value)
          : (newQueryParams["pois"] = value);
      }

      // Add/update scenario_id
      if (queryParams.includes("scenario_id_input") && this.activeScenario) {
        const value = parseInt(this.activeScenario);
        newQueryParams["scenario_id_input"] = value;
        if (!this.activeScenario) {
          isValid = false;
        }
      }

      // Add/update modus
      if (queryParams.includes("modus_input")) {
        const value = `'${this.calculationModes}'`;
        newQueryParams["modus_input"] = value;
      }

      // Add/update routing profile.
      if (queryParams.includes("routing_profile")) {
        const value = `'${this.activeRoutingProfile}'`;
        newQueryParams["routing_profile"] = value;
      }

      // *UPDATE URL AND REFRESH LAYER*
      if (layer.getVisible() === true && isValid) {
        updateLayerUrlQueryParam(layer, newQueryParams);
        layer.getSource().refresh();
        console.log(
          layer.getSource().getUrls
            ? layer.getSource().getUrls()
            : layer.getSource().getUrl()
        );
      }
    },
    updateLayersParam() {
      Object.keys(this.layers).forEach(key => {
        if (this.layers[key].get("queryParams")) {
          this.updateLayer(this.layers[key]);
        }
      });
    },
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
    })
  },
  watch: {
    calculationModes() {
      this.updateLayersParam();
    },
    activeScenario() {
      this.updateLayersParam();
    },
    selectedPois() {
      this.updateLayersParam();
    },
    activeRoutingProfile() {
      this.updateLayersParam();
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
