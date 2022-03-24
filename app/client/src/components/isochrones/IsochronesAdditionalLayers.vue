<template>
  <v-dialog v-model="show" max-width="350px">
    <v-card>
      <v-app-bar :color="appColor.primary" dark>
        <v-app-bar-nav-icon
          ><v-icon>fas fa-layer-group</v-icon></v-app-bar-nav-icon
        >
        <v-toolbar-title>{{
          $t("isochrones.results.additionalLayers")
        }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>

      <v-card-title primary-title v-if="calculation">
        <v-flex v-if="calculation.calculationType === 'single'" xs12>
          <v-checkbox
            class="mt-2"
            :input-value="_getState('Default') && calculation.isVisible"
            @change="_toggleRoadNetwork($event, 'Default')"
            v-show="groupedCalculationData.hasOwnProperty('Default')"
            :label="$t('isochrones.additionalLayers.defaultNetwork')"
          ></v-checkbox>
          <v-checkbox
            class="mt-2"
            :input-value="_getState('Input') && calculation.isVisible"
            @change="_toggleRoadNetwork($event, 'Input')"
            v-show="groupedCalculationData.hasOwnProperty('Input')"
            :label="$t('isochrones.additionalLayers.inputNetwork')"
          ></v-checkbox>
        </v-flex>
        <v-flex v-else-if="calculation.calculationType === 'multiple'">
          <v-checkbox
            class="mt-2"
            :input-value="
              isochroneOverlayFeatures.studyAreaFeatures.length > 0 &&
                calculation.isVisible
            "
            :label="$t('isochrones.additionalLayers.studyArea')"
            @change="
              _toggleMultiIsochroneOverlayFeatures(
                isochroneOverlayFeatures.studyAreaFeatures
              )
            "
          ></v-checkbox>
          <v-checkbox
            class="mt-2"
            :label="$t('isochrones.additionalLayers.startingPoints')"
            :input-value="
              isochroneOverlayFeatures.startingPointFeatures.length > 0 &&
                calculation.isVisible
            "
            @change="
              _toggleMultiIsochroneOverlayFeatures(
                isochroneOverlayFeatures.startingPointFeatures
              )
            "
          ></v-checkbox>
        </v-flex>
      </v-card-title>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters, mapActions } from "vuex";
import { getNestedProperty } from "../../utils/Helpers";

export default {
  props: {
    calculation: { type: Object, required: false },
    visible: { type: Boolean, required: true }
  },
  computed: {
    ...mapGetters("isochrones", {
      getGroupedCalculationData: "getGroupedCalculationData",
      isochroneOverlayLayer: "isochroneOverlayLayer"
    }),
    ...mapGetters("app", {
      appColor: "appColor"
    }),
    show: {
      get() {
        return this.visible;
      },
      set(value) {
        if (!value) {
          this.$emit("close");
        }
      }
    },
    groupedCalculationData: {
      get() {
        return this.getGroupedCalculationData(this.calculation.id);
      }
    },
    isochroneOverlayFeatures() {
      const features = {
        studyAreaFeatures: [],
        startingPointFeatures: []
      };

      this.isochroneOverlayLayer
        .getSource()
        .getFeatures()
        .forEach(feature => {
          if (
            feature.get("calculationNumber") === this.calculation.id &&
            feature.get("isVisible") !== false
          ) {
            if (feature.getGeometry().getType() === "Point") {
              features.startingPointFeatures.push(feature);
            } else {
              features.studyAreaFeatures.push(feature);
            }
          }
        });
      return features;
    }
  },
  methods: {
    ...mapActions("isochrones", {
      toggleRoadNetwork: "toggleRoadNetwork"
    }),
    _getState(type) {
      const state = getNestedProperty(
        this.calculation.additionalData,
        `${type}.state`
      );
      return !!state;
    },
    _toggleRoadNetwork(state, type) {
      const groupedData = this.getGroupedCalculationData(this.calculation.id);
      this.toggleRoadNetwork({
        calculation: this.calculation,
        groupedData: groupedData,
        state: !!state,
        type: type
      });

      //Toggle isVisible if other features are not visible
      const visibleFeatures = this.calculation.data.filter(
        feature => feature.isVisible === true
      );
      this.calculation.isVisible = true;
      if (visibleFeatures.length === 0) {
        let isNetworkVisible = false;
        Object.keys(this.calculation.additionalData).forEach(key => {
          if (this.calculation.additionalData[key].state === true) {
            isNetworkVisible = true;
          }
        });
        if (!isNetworkVisible) {
          // Change calculation is visible
          this.calculation.isVisible = false;
        }
      }
    }, //
    _toggleMultiIsochroneOverlayFeatures(features) {
      features.forEach(feature => {
        const isVisible =
          feature.get("isVisible") === undefined
            ? true
            : feature.get("isVisible");
        feature.set("isVisible", !isVisible);
      });
    }
  }
};
</script>
