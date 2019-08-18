<template>
  <v-flex xs12>
    <v-card-text class="pr-16 pl-16 pt-0 pb-0">
      <v-divider></v-divider>
    </v-card-text>
    <v-subheader
      @click="
        isIsochroneCalculationTypeElVisible = !isIsochroneCalculationTypeElVisible
      "
      class="clickable pb-0 mb-0"
    >
      <v-icon
        :class="{
          activeIcon: isIsochroneCalculationTypeElVisible,
          'mr-2': true
        }"
        style="margin-right: 2px;"
        small
        >fas fa-bullseye</v-icon
      >
      <h3>Isochrone Calculation</h3>
    </v-subheader>
    <v-card-text
      v-show="isIsochroneCalculationTypeElVisible"
      class="py-0 my-0 justify-center"
    >
      <v-radio-group
        class="pb-0 mb-0 justify-center radio-group-height"
        :value="calculationType"
        v-model="calculationType"
        row
      >
        <v-radio label="Single" value="single"></v-radio>
        <v-radio label="Multiple" value="multiple"></v-radio>
      </v-radio-group>
    </v-card-text>
  </v-flex>
</template>
<script>
import { mapGetters } from "vuex";
import { mapFields } from "vuex-map-fields";

export default {
  data: () => ({
    isIsochroneCalculationTypeElVisible: true
  }),
  computed: {
    ...mapGetters("isochrones", { options: "options" }),
    ...mapFields("isochrones", {
      calculationType: "options.calculationType"
    })
  }
};
</script>
<style lang="css" scoped>
.activeIcon {
  color: #30c2ff;
}
.radio-group-height >>> .v-input__control {
  height: 40px;
}
</style>
