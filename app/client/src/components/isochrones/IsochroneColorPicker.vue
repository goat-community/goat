<template>
  <v-dialog v-model="show" scrollable max-width="330" v-if="calculation">
    <v-card>
      <v-app-bar :color="appColor.primary" dark>
        <v-app-bar-nav-icon><v-icon>fas fa-palette</v-icon></v-app-bar-nav-icon>
        <v-toolbar-title>{{
          $t("isochrones.pickColor.title")
        }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
      <vue-scroll>
        <v-container class="pb-0">
          <v-alert
            border="left"
            colored-border
            class="mb-0 mt-2 mx-1 elevation-2"
            icon="info"
            :color="appColor.primary"
            dense
          >
            <span v-html="$t('isochrones.results.colorMessage')"></span>
          </v-alert>
          <v-radio-group
            @change="colorChanged"
            class="ml-3 mt-3  mb-0"
            v-model="calculation[`${selectedMode}ColorPalette`]"
          >
            <v-layout
              row
              wrap
              align-center
              class="mb-3"
              v-for="(color, key, index) in colors"
              :key="index"
            >
              <v-radio :value="key">
                <template v-slot:label>
                  <div
                    class="colorPalettePicker"
                    :style="{
                      backgroundImage: `linear-gradient(to right, ${getPaletteColor(
                        color
                      )})`
                    }"
                  ></div>
                </template>
              </v-radio>
            </v-layout>
          </v-radio-group>
        </v-container>
      </vue-scroll>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";
import IsochroneUtils from "../../utils/IsochroneUtils";

export default {
  props: {
    selectedMode: { type: String, required: false },
    calculation: { type: Object, required: false },
    visible: { type: Boolean, required: true }
  },
  data: () => ({}),
  methods: {
    getPaletteColor(color) {
      return Object.values(color).toString();
    },
    colorChanged() {
      const color = this.colors[
        this.calculation[`${this.selectedMode}ColorPalette`]
      ];

      // Update isochrone color
      this.calculation.data.forEach(obj => {
        const isochroneFeature = this.isochroneLayer
          .getSource()
          .getFeatureById(obj.id);
        if (this.selectedMode == isochroneFeature.get("modus")) {
          console.log(this.selectedMode);
          const step = isochroneFeature.get("step");
          const interpolatedColor = IsochroneUtils.getInterpolatedColor(
            1,
            20,
            parseInt(step / 60),
            color
          );
          isochroneFeature.set("color", interpolatedColor);
          // legend el color
          obj.color = interpolatedColor;
        }
      });

      // Update network color
      if (!this.calculation.additionalData[this.selectedMode]) return;
      this.calculation.additionalData[this.selectedMode].features.forEach(
        feature => {
          const cost = feature.get("cost");
          const lowestCostValue = 0; // TODO: Find lowest and highest based on response data
          const highestCostValue = 1200;
          const interpolatedColor = IsochroneUtils.getInterpolatedColor(
            lowestCostValue,
            highestCostValue,
            cost,
            color
          );
          feature.set("color", interpolatedColor);
        }
      );
    }
  },
  watch: {},
  computed: {
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
    ...mapGetters("isochrones", {
      isochroneLayer: "isochroneLayer",
      colors: "colors"
    }),
    ...mapGetters("app", {
      appColor: "appColor"
    })
  }
};
</script>
<style lang="css" scoped>
.colorPalettePicker {
  height: 20px;
  border-radius: 5px;
  width: 265px;
}
</style>
