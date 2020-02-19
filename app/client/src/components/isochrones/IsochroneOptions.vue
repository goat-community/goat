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
          <v-select
            v-if="options.calculationType"
            item-value="value"
            outlined
            return-object
            v-model="routingProfile"
            :value="routingProfile"
            :items="options.routingProfile.values"
            :label="$t('isochrones.options.routingProfile')"
            @change="routingProfileChanged"
          >
            <template slot="selection" slot-scope="{ item }">
              {{
                $te(`isochrones.options.${item.value}`)
                  ? $t(`isochrones.options.${item.value}`)
                  : item.display
              }}
            </template>
            <template slot="item" slot-scope="{ item }">
              <v-tooltip top>
                <template v-slot:activator="{ on }">
                  <v-icon class="mr-2" color="rgba(0, 0, 0, 0.54)" v-on="on"
                    >info</v-icon
                  >
                </template>
                <span>{{
                  $t(`map.tooltips.routingProfiles.${item.value}`)
                }}</span>
              </v-tooltip>
              {{
                $te(`isochrones.options.${item.value}`)
                  ? $t(`isochrones.options.${item.value}`)
                  : item.display
              }}
            </template>
          </v-select>
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
            max="10"
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
            max="8"
            inverse-label
            prepend-icon="fas fa-sort-numeric-up"
            :label="`${$t('isochrones.isochrones')} (${steps})`"
            color="#30C2FF"
          >
          </v-slider>

          <v-select
            v-if="options.calculationType"
            item-text="display"
            item-value="value"
            outlined
            v-model="concavityIsochrones"
            :value="concavityIsochrones"
            :items="options.concavityIsochrones.values"
            :label="$t('isochrones.options.calcType')"
          ></v-select>

          <v-select
            item-value="value"
            v-model="calculationModes"
            outlined
            :value="calculationModes"
            :items="filterCalcModeValues()"
            :label="$t('isochrones.options.calcModus')"
          >
            <template slot="selection" slot-scope="{ item }">
              {{ $t(`isochrones.options.${item.name}`) }}
            </template>
            <template slot="item" slot-scope="{ item }">
              {{ $t(`isochrones.options.${item.name}`) }}
            </template>
          </v-select>
        </v-flex>
      </v-expand-transition>
    </div>
  </v-flex>
</template>
<script>
import { mapGetters } from "vuex";
import { mapFields } from "vuex-map-fields";

export default {
  name: "isochrone-options",
  data: () => ({
    isOptionsElVisible: true,
    isIsochroneOptionsVisible: true
  }),
  computed: {
    ...mapGetters("isochrones", { options: "options" }),
    ...mapFields("isochrones", {
      minutes: "options.minutes",
      speed: "options.speed",
      steps: "options.steps",
      concavityIsochrones: "options.concavityIsochrones.active",
      calculationModes: "options.calculationModes.active",
      alphaShapeParameter: "options.alphaShapeParameter.active",
      routingProfile: "options.routingProfile.active"
    })
  },
  methods: {
    filterCalcModeValues() {
      return this.options.calculationModes.values;
    },
    routingProfileChanged(selectedType) {
      //Reset speed slider value based on routing profile default speed
      this.speed = selectedType.defaultSpeed;
    }
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
