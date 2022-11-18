<template>
  <!-- <v-toolbar-title>{{
          $t("isochrones.pickColor.title")
        }}</v-toolbar-title> -->
  <div>
    <v-tabs grow v-model="tab" style="width: 400px; margin:auto;">
      <v-tab :key="1">
        <v-badge>
          <b>{{ $t("isochrones.styling.fillColor") }}</b>
        </v-badge>
      </v-tab>
      <v-tab :key="2">
        <v-badge>
          <b>{{ $t("isochrones.styling.StrokeColor") }}</b>
        </v-badge>
      </v-tab>
    </v-tabs>
    <v-tabs-items v-model="tab">
      <v-tab-item :key="1">
        <v-color-picker
          class="elevation-0"
          canvas-height="100"
          width="400"
          style="margin: auto; margin-bottom: 20px; margin-top: 10px;"
          :mode.sync="hexa"
          v-model="fillColor"
          @input="onFillColorChange($event)"
        >
        </v-color-picker>
        <v-btn
          color="warning"
          dark
          @click="resetStyle(selectedCalculationChangeColor)"
          :style="
            `width: 100%; background-color: ${appColor.primary} !important`
          "
        >
          Reset Style
        </v-btn>
      </v-tab-item>
      <v-tab-item>
        <div>
          <v-row style="width: 424px; margin: auto;" align="center">
            <v-col cols="6" class="py-0">
              <v-text-field
                outlined
                dense
                label="Stroke Width"
                v-model="strokeWidth"
                @input="changeWidth"
                style="margin: auto; margin-bottom: 10px; margin-top: 10px; width:400px;"
              ></v-text-field>
            </v-col>
            <v-col cols="6" class="py-0">
              <v-select
                v-model="strokeStyle"
                :items="strokeStyles"
                label="Stroke style"
                dense
                outlined
              ></v-select>
            </v-col>
          </v-row>
          <!-- <v-row style="width: 424px; margin: auto;" align="center">
            <v-col cols="6" class="py-0">
              <v-text-field
                outlined
                dense
                v-if="strokeStyle === 'dashed'"
                label="Dash Width"
                :rules="rules"
                v-model="dashWidth"
                @input="changeDash"
                type="number"
              ></v-text-field>
            </v-col>
            <v-col cols="6" class="py-0">
              <v-text-field
                outlined
                dense
                v-if="strokeStyle === 'dashed'"
                label="Spacing"
                :rules="rules"
                v-model="dashSpacing"
                @input="changeDash"
                type="number"
              ></v-text-field>
            </v-col>
          </v-row> -->
          <v-color-picker
            class="elevation-0"
            canvas-height="100"
            width="400"
            style="margin: auto; margin-bottom: 20px; margin-top: 10px;"
            :mode.sync="hexa"
            v-model="strokeColor"
            @input="onStrokeColorChange($event)"
            @change="onStrokeColorChange($event)"
          >
          </v-color-picker>
          <v-btn
            color="warning"
            dark
            @click="resetStyle(selectedCalculationChangeColor)"
            :style="
              `width: 100%; background-color: ${appColor.primary} !important`
            "
          >
            Reset Style
          </v-btn>
        </div>
      </v-tab-item>
    </v-tabs-items>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { mapFields } from "vuex-map-fields";
import IsochroneUtils from "../../utils/IsochroneUtils";
import { Draggable } from "draggable-vue-directive";

//!Right way
export default {
  props: ["temporaryColors"],
  watch: {
    strokeColor(value) {
      let { width, dashWidth, dashSpace } = this.calculationSrokeObjects[
        this.selectedCalculationChangeColor.id - 1
      ];
      this.newObjectCreation(value, width, dashWidth, dashSpace);
    },
    strokeStyle(value) {
      if (value === "Solid") {
        if (this.strokeColor[7] === "0" && this.strokeColor[8] === "0") {
          this.turnOnStroke();
        }
        let { color, width } = this.calculationSrokeObjects[
          this.selectedCalculationChangeColor.id - 1
        ];
        this.newObjectCreation(color, width, 0, 0);
        this.dashWidth = 0;
        this.dashSpacing = 0;
      } else if (value === "Dashed") {
        if (this.strokeColor[7] === "0" && this.strokeColor[8] === "0") {
          this.turnOnStroke();
        }
        let {
          color,
          width,
          dashWidth,
          dashSpace
        } = this.calculationSrokeObjects[
          this.selectedCalculationChangeColor.id - 1
        ];
        this.newObjectCreation(
          color,
          width,
          dashWidth === 0 ? 10 : dashWidth,
          dashSpace === 0 ? 10 : dashSpace
        );
        this.dashWidth = dashWidth === 0 ? 10 : dashWidth;
        this.dashSpacing = dashSpace === 0 ? 10 : dashSpace;
      } else {
        this.turnOffStroke();
      }
    },
    selectedCalculationChangeColor(value) {
      if (value) {
        this.dialog = true;
      }
    }
  },
  directives: {
    Draggable
  },
  data: () => ({
    isExpanded: true,
    strokeWidth: null,
    dialog: true,
    dashWidth: null,
    dashSpacing: null,
    fillColor: null,
    strokeColor: "#ffffff00",
    handleId: "handle",
    hexa: "hexa",
    tab: null,
    strokeStyle: "No Stroke",
    strokeStyles: ["No Stroke", "Solid", "Dashed"],
    strokeStatus: false,
    draggableValue: {
      handle: undefined,
      boundingElement: undefined,
      resetInitialPos: undefined
    }
  }),
  mounted() {
    const element = document.getElementById("ol-map-container");
    this.draggableValue.resetInitialPos = false;
    this.draggableValue.boundingElement = element;
    this.draggableValue.handle = this.$refs[this.handleId];
  },
  created() {
    let colorHex = this.calculationColors[
      this.selectedCalculationChangeColor.id - 1
    ];

    this.strokeWidth = this.calculationSrokeObjects[
      this.selectedCalculationChangeColor.id - 1
    ].width.toString();

    this.strokeColor = this.calculationSrokeObjects[
      this.selectedCalculationChangeColor.id - 1
    ].color;

    if (
      this.calculationSrokeObjects[this.selectedCalculationChangeColor.id - 1]
        .dashWidth &&
      this.calculationSrokeObjects[this.selectedCalculationChangeColor.id - 1]
        .dashSpace
    ) {
      this.strokeStyle = "Dashed";
    } else if (this.strokeColor[7] === "0" && this.strokeColor[8] === "0") {
      this.strokeStyle = "No Stroke";
    } else {
      this.strokeStyle = "Solid";
    }

    this.dashWidth = this.calculationSrokeObjects[
      this.selectedCalculationChangeColor.id - 1
    ].dashWidth;

    this.dashSpacing = this.calculationSrokeObjects[
      this.selectedCalculationChangeColor.id - 1
    ].dashSpace;

    this.fillColor = colorHex;
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
      preDefCalculationColors: "preDefCalculationColors",
      colors: "colors",
      calculationColors: "calculationColors",
      calculationSrokeObjects: "calculationSrokeObjects",
      selectedCalculationChangeColor: "selectedCalculationChangeColor"
    }),
    ...mapFields("isochrones", {
      preDefCalculationColors: "preDefCalculationColors",
      calculations: "calculations",
      calculationColors: "calculationColors",
      calculationSrokeObjects: "calculationSrokeObjects",
      selectedCalculationChangeColor: "selectedCalculationChangeColor"
    }),
    ...mapGetters("app", {
      appColor: "appColor"
    })
  },
  methods: {
    newObjectCreation(color, width, dashWidth, dashSpace) {
      let newObj = {
        color: color,
        width: width,
        dashWidth: dashWidth,
        dashSpace: dashSpace
      };
      this.updateStrokeStyling(newObj);
    },
    updateStrokeStyling(stylingObject) {
      let newStrokes = [
        ...this.calculationSrokeObjects.map((elem, idx) => {
          if (idx === this.selectedCalculationChangeColor.id - 1) {
            return stylingObject;
          } else {
            return elem;
          }
        })
      ];
      this.calculationSrokeObjects = newStrokes;
    },
    findTheRightPreDefIndex(calc) {
      if (calc.id <= 10) {
        return calc.id;
      } else {
        let remain = calc.id % 10;
        return remain;
      }
    },
    // changeDash() {
    //   let { color } = this.calculationSrokeObjects[
    //     this.selectedCalculationChangeColor.id - 1
    //   ];
    //   this.newObjectCreation(
    //     color,
    //     this.strokeWidth,
    //     this.dashWidth,
    //     this.dashSpacing
    //   );
    // },
    changeWidth() {
      let newWidth = parseInt(this.strokeWidth);
      let { color, dashWidth, dashSpace } = this.calculationSrokeObjects[
        this.selectedCalculationChangeColor.id - 1
      ];
      this.newObjectCreation(color, newWidth, dashWidth, dashSpace);
    },
    onFillColorChange(value) {
      if (value[7] === "F" && value[8] === "F") {
        let newModColor = value.slice(0, -2) + "80";
        this.fillColor = newModColor;
        let newColors = [
          ...this.calculationColors.map((elem, idx) =>
            this.selectedCalculationChangeColor.id - 1 === idx
              ? newModColor
              : elem
          )
        ];
        this.calculationColors = newColors;
      } else {
        let newColors = [
          ...this.calculationColors.map((elem, idx) =>
            this.selectedCalculationChangeColor.id - 1 === idx ? value : elem
          )
        ];
        this.calculationColors = newColors;
      }
    },
    onStrokeColorChange(value) {
      let { dashWidth, dashSpace } = this.calculationSrokeObjects[
        this.selectedCalculationChangeColor.id - 1
      ];
      this.newObjectCreation(
        value,
        parseInt(this.strokeWidth),
        dashWidth,
        dashSpace
      );
      this.strokeColor = value;
    },
    resetStyle(calculation) {
      this.strokeStyle = "No Stroke";
      let tempArray = this.calculationColors;
      tempArray[calculation.id - 1] = this.temporaryColors[
        this.findTheRightPreDefIndex(calculation) - 1
      ];
      this.calculationColors = [...tempArray];
      this.fillColor = this.temporaryColors[calculation.id - 1];
      this.newObjectCreation("#00000000", 2, 0, 0);
    },
    closeDialog() {
      this.selectedCalculationChangeColor = null;
      this.dialog = false;
    },
    expand() {
      this.isExpanded = !this.isExpanded;
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
    },
    turnOnStroke() {
      this.strokeColor =
        this.calculationSrokeObjects[
          this.selectedCalculationChangeColor.id - 1
        ].color
          .slice(0, -1)
          .slice(0, -1) + "ff";
    },
    turnOffStroke() {
      this.strokeColor =
        this.calculationSrokeObjects[
          this.selectedCalculationChangeColor.id - 1
        ].color
          .slice(0, -1)
          .slice(0, -1) + "00";
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

.isochrone-color-picker {
  position: fixed;
  z-index: 1;
  top: 20px;
  /** Drawer width + 70px margin */
  left: calc(360px + 70px);
  max-width: 450px;
  min-width: 370px;
  height: fit-content;
}

.color-wrapper {
  margin-top: 20px;
}
</style>
