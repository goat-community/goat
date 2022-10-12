<template>
  <v-dialog
    width="300"
    overlay-opacity="0"
    persistent
    no-click-animation
    hide-overlay
    v-model="dialog"
    content-class="v-dialog"
  >
    <v-card
      :style="[isExpanded ? { height: 'auto' } : { height: '50px' }]"
      style="position:fixed;top:10px;left:360px;z-index:2;min-width:350px;max-width:450px;max-height:450px;overflow:hidden;"
      v-draggable="draggableValue"
      ondragstart="return false;"
    >
      <v-app-bar
        style="cursor:grab;"
        height="50"
        :color="appColor.primary"
        dark
      >
        <v-app-bar-nav-icon><v-icon>fas fa-palette</v-icon></v-app-bar-nav-icon>
        <v-toolbar-title>{{
          $t("isochrones.pickColor.title")
        }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-icon @click="expand" class="toolbar-icons mr-2">
          {{ isExpanded ? "fas fa-chevron-up" : "fas fa-chevron-down" }}
        </v-icon>
        <v-app-bar-nav-icon @click.stop="closeDialog"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
      <vue-scroll style="padding-top:25px;">
        <v-color-picker
          class="elevation-0"
          canvas-height="100"
          width="400"
          style="margin:auto; margin-bottom: 20px;"
          mode.sync="hexa"
          v-model="fillColor"
          @input="onFillColorChange($event)"
        >
        </v-color-picker>
        <v-btn
          color="warning"
          dark
          @click="resetStyle(selectedCalculationChangeColor)"
          style="width:100%;background-color: #2bb381 !important;"
        >
          Reset Style
        </v-btn>
      </vue-scroll>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";
import { mapFields } from "vuex-map-fields";
import IsochroneUtils from "../../utils/IsochroneUtils";
import { Draggable } from "draggable-vue-directive";

//!Right way
export default {
  watch: {
    selectedCalculationChangeColor(value) {
      if (value) {
        this.dialog = true;
        let colorHex = this.calculationColors[
          this.selectedCalculationChangeColor.id - 1
        ];

        this.fillColor = colorHex;
      }
    }
  },
  directives: {
    Draggable
  },
  data: () => ({
    isExpanded: true,
    dialog: false,
    fillColor: null,
    draggableValue: {
      handle: undefined,
      boundingElement: undefined,
      resetInitialPos: undefined
    },
    temporaryColors: null
  }),
  mounted() {
    if (this.selectedCalculationChangeColor) {
      this.dialog = true;
    }
    const element = document.getElementById("ol-map-container");
    this.draggableValue.resetInitialPos = false;
    this.draggableValue.boundingElement = element;
    this.draggableValue.handle = this.$refs[this.handleId];
    this.temporaryColors = this.calculationColors;
  },
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
      calculationColors: "calculationColors",
      colors: "colors",
      selectedCalculationChangeColor: "selectedCalculationChangeColor"
    }),
    ...mapFields("isochrones", {
      calculationColors: "calculationColors",
      selectedCalculationChangeColor: "selectedCalculationChangeColor"
    }),
    ...mapGetters("app", {
      appColor: "appColor"
    })
  },
  methods: {
    resetStyle(calculation) {
      let tempArray = this.calculationColors;
      tempArray[calculation.id - 1] = this.temporaryColors[calculation.id - 1];
      this.calculationColors = [...tempArray];
    },
    closeDialog() {
      this.selectedCalculationChangeColor = null;
      this.dialog = false;
    },
    expand() {
      this.isExpanded = !this.isExpanded;
    },
    onFillColorChange(e) {
      let newColors = [
        ...this.calculationColors.map((elem, idx) =>
          this.selectedCalculationChangeColor.id - 1 === idx ? e : elem
        )
      ];
      this.calculationColors = newColors;
      // this.calculationColors[this.selectedCalculationChangeColor.id - 1] = rgba;
    },
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
