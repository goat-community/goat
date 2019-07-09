<template>
  <v-flex xs12>
    <!-- Isochrone Options -->
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

    <v-flex
      xs-12
      class="mx-4 isochroneOptions"
      v-show="isIsochroneOptionsVisible"
    >
      <v-slider
        min="1"
        max="20"
        inverse-label
        v-model="minutes"
        prepend-icon="fas fa-clock"
        :label="minutes + ' min'"
      >
      </v-slider>

      <v-slider
        min="1"
        max="10"
        inverse-label
        v-model="speed"
        prepend-icon="fas fa-tachometer-alt"
        :label="speed + ' km/h'"
      >
      </v-slider>

      <v-slider
        class="mb-1"
        v-model="steps"
        min="1"
        max="8"
        inverse-label
        prepend-icon="fas fa-sort-numeric-up"
        :label="'Isochrones (' + steps + ')'"
      >
      </v-slider>

      <v-select
        item-text="display"
        item-value="value"
        v-model="concavityIsochrones"
        :value="concavityIsochrones"
        :items="options.concavityIsochrones.values"
        :label="$t('isochrones.options.calcType')"
      ></v-select>

      <v-select
        item-text="display"
        item-value="value"
        v-model="calculationModes"
        :value="concavityIsochrones"
        :items="options.calculationModes.values"
        :label="$t('isochrones.options.calcModus')"
      ></v-select>
    </v-flex>
  </v-flex>
</template>
<script>
import { mapGetters } from "vuex";
import { mapFields } from "vuex-map-fields";

export default {
  name: "isochrone-options",
  data: () => ({
    isIsochroneOptionsVisible: true
  }),
  computed: {
    ...mapGetters("isochrones", { options: "options" }),

    ...mapFields("isochrones", {
      minutes: "options.minutes",
      speed: "options.speed",
      steps: "options.steps",
      concavityIsochrones: "options.concavityIsochrones.active",
      calculationModes: "options.calculationModes.active"
    })
  },
  methods: {}
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
