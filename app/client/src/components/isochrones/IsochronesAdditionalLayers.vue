<template>
  <v-dialog v-model="show" max-width="350px">
    <v-card>
      <v-app-bar color="green" dark>
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
        <v-flex xs12>
          <v-checkbox
            :disabled="!calculation.isVisible"
            class="mt-2"
            :input-value="_getState('Default')"
            @change="_toggleRoadNetwork($event, 'Default')"
            v-show="groupedCalculationData.hasOwnProperty('Default')"
            :label="$t('isochrones.additionalLayers.defaultNetwork')"
          ></v-checkbox>
          <v-checkbox
            :disabled="!calculation.isVisible"
            class="mt-2"
            :input-value="_getState('Input')"
            @change="_toggleRoadNetwork($event, 'Input')"
            v-show="groupedCalculationData.hasOwnProperty('Input')"
            :label="$t('isochrones.additionalLayers.inputNetwork')"
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
      getGroupedCalculationData: "getGroupedCalculationData"
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
    }
  }
};
</script>
