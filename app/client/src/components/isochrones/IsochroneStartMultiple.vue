<template>
  <v-flex xs12>
    <v-card-text class="pr-16 pl-16 pt-0 pb-0">
      <v-divider></v-divider>
    </v-card-text>
    <v-subheader
      @click="isIsochroneStartElVisible = !isIsochroneStartElVisible"
      class="clickable"
    >
      <v-icon
        :class="{
          activeIcon: isIsochroneStartElVisible,
          'mr-3': true
        }"
        style="margin-right: 2px;"
        small
        >fas fa-map-marker-alt</v-icon
      >
      <h3>Start</h3>
    </v-subheader>
    <v-flex
      xs12
      v-show="isIsochroneStartElVisible"
      style="overflow: hidden;"
      class="mx-4"
    >
      <v-select
        item-text="display"
        item-value="value"
        class="select-method-height mx-1 my-1"
        v-model="activeMultiIsochroneMethod"
        :items="multiIsochroneCalculationMethods.values"
        label="Select Method"
        solo
      ></v-select>

      <v-alert
        v-if="isReady"
        border="left"
        colored-border
        class="mb-0 mt-2 mx-1 elevation-2"
        icon="info"
        color="green"
        dense
      >
        Select zones for the calculation.
      </v-alert>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          v-if="isReady"
          outlined
          class="white--text"
          color="red"
          @click="clear"
        >
          Clear
        </v-btn>
        <v-btn
          v-if="isReady"
          disabled
          outlined
          class="white--text mr-1"
          color="green"
          @click="clear"
        >
          Calculate
        </v-btn>
      </v-card-actions>
    </v-flex>
  </v-flex>
</template>
<script>
import { mapGetters } from "vuex";
import { mapFields } from "vuex-map-fields";
import { InteractionsToggle } from "../../mixins/InteractionsToggle";

export default {
  mixins: [InteractionsToggle],
  data: () => ({
    isIsochroneStartElVisible: true,
    interactionType: "isochrone-multiple-interaction"
  }),
  computed: {
    ...mapGetters("isochrones", {
      multiIsochroneCalculationMethods: "multiIsochroneCalculationMethods"
    }),
    ...mapFields("isochrones", {
      activeMultiIsochroneMethod: "multiIsochroneCalculationMethods.active"
    }),
    isReady() {
      if (this.activeMultiIsochroneMethod !== null) {
        return true;
      } else {
        return false;
      }
    }
  },
  methods: {
    clear() {
      this.activeMultiIsochroneMethod = null;
    }
  }
};
</script>
<style lang="css" scoped>
.activeIcon {
  color: #30c2ff;
}
.select-method-height >>> .v-input__control {
  height: 40px;
}
</style>
