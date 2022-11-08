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
      class="isochrone-color-picker"
      v-draggable="draggableValue"
    >
      <v-app-bar
        :ref="handleId"
        style="cursor: grab"
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
      <vue-scroll
        class="color-wrapper"
        :style="[isExpanded ? {} : { visibility: 'hidden' }]"
      >
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
              style="width: 100%; background-color: #2bb381 !important"
            >
              Reset Style
            </v-btn>
          </v-tab-item>
          <v-tab-item>
            <v-text-field
              label="Stroke Width"
              :rules="rules"
              v-model="strokeWidth"
              @input="changeWidth"
              type="number"
              style="margin: auto; margin-bottom: 10px; margin-top: 10px; width:400px;"
            ></v-text-field>
            <v-radio-group
              style="margin: auto; width:400px;"
              v-model="strokeStyle"
              column
            >
              <p>Stroke Style</p>
              <v-radio label="Solid" value="solid"></v-radio>
              <v-radio label="Dashed" value="dashed"></v-radio>
            </v-radio-group>
            <div v-if="strokeStyle === 'dashed'">
              <v-row style="margin: -5px auto; width:400px;">
                <v-col
                  style="padding: 0; padding-right: 12px;"
                  cols="12"
                  sm="6"
                >
                  <v-text-field
                    label="Dash Width"
                    :rules="rules"
                    v-model="dashWidth"
                    @input="changeDash"
                    type="number"
                  ></v-text-field>
                </v-col>
                <v-col
                  style="padding: 0; padding-right: 12px;"
                  cols="12"
                  sm="6"
                >
                  <v-text-field
                    label="Spacing"
                    :rules="rules"
                    v-model="dashSpacing"
                    @input="changeDash"
                    type="number"
                  ></v-text-field>
                </v-col>
              </v-row>
            </div>
            <v-color-picker
              class="elevation-0"
              canvas-height="100"
              width="400"
              style="margin: auto; margin-bottom: 20px; margin-top: 10px;"
              :mode.sync="hexa"
              v-model="strokeColor"
              @input="onStrokeColorChange($event)"
            >
            </v-color-picker>
          </v-tab-item>
        </v-tabs-items>
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
  props: ["temporaryColors"],
  watch: {
    strokeStyle(value) {
      if (value === "solid") {
        let newObj = {
          color: this.calculationSrokeObjects[
            this.selectedCalculationChangeColor.id - 1
          ].color,
          width: this.calculationSrokeObjects[
            this.selectedCalculationChangeColor.id - 1
          ].width,
          dashWidth: 0,
          dashSpace: 0
        };
        this.updateStrokeStyling(newObj);
        this.dashWidth = 0;
        this.dashSpacing = 0;
      } else {
        let newObj = {
          color: this.calculationSrokeObjects[
            this.selectedCalculationChangeColor.id - 1
          ].color,
          width: this.calculationSrokeObjects[
            this.selectedCalculationChangeColor.id - 1
          ].width,
          dashWidth:
            this.calculationSrokeObjects[
              this.selectedCalculationChangeColor.id - 1
            ].dashWidth === 0
              ? 10
              : this.calculationSrokeObjects[
                  this.selectedCalculationChangeColor.id - 1
                ].dashWidth,
          dashSpace:
            this.calculationSrokeObjects[
              this.selectedCalculationChangeColor.id - 1
            ].dashSpace === 0
              ? 10
              : this.calculationSrokeObjects[
                  this.selectedCalculationChangeColor.id - 1
                ].dashSpace
        };
        this.updateStrokeStyling(newObj);
        this.dashWidth = newObj.dashWidth;
        this.dashSpacing = newObj.dashSpace;
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
    rules: [value => !!value || "Required."],
    isExpanded: true,
    strokeWidth: 0,
    dialog: true,
    dashWidth: 0,
    dashSpacing: 0,
    fillColor: null,
    strokeColor: "#ffffff00",
    handleId: "handle",
    hexa: "hexa",
    tab: null,
    strokeStyle: "solid",
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
    ].width;

    this.strokeColor = this.calculationSrokeObjects[
      this.selectedCalculationChangeColor.id - 1
    ].color;

    if (
      this.calculationSrokeObjects[this.selectedCalculationChangeColor.id - 1]
        .dashWidth &&
      this.calculationSrokeObjects[this.selectedCalculationChangeColor.id - 1]
        .dashSpace
    ) {
      this.strokeStyle = "dashed";
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
    changeDash() {
      let newObj = {
        color: this.calculationSrokeObjects[
          this.selectedCalculationChangeColor.id - 1
        ].color,
        width: this.strokeWidth,
        dashWidth: this.dashWidth,
        dashSpace: this.dashSpacing
      };
      this.updateStrokeStyling(newObj);
    },
    changeWidth() {
      let newObj = {
        color: this.calculationSrokeObjects[
          this.selectedCalculationChangeColor.id - 1
        ].color,
        width: this.strokeWidth,
        dashWidth: this.calculationSrokeObjects[
          this.selectedCalculationChangeColor.id - 1
        ].dashWidth,
        dashSpace: this.calculationSrokeObjects[
          this.selectedCalculationChangeColor.id - 1
        ].dashSpace
      };
      this.updateStrokeStyling(newObj);
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
      let newObj = {
        color: value,
        width: this.strokeWidth,
        dashWidth: this.calculationSrokeObjects[
          this.selectedCalculationChangeColor.id - 1
        ].dashWidth,
        dashSpace: this.calculationSrokeObjects[
          this.selectedCalculationChangeColor.id - 1
        ].dashSpace
      };
      this.updateStrokeStyling(newObj);
      this.strokeColor = value;
    },
    resetStyle(calculation) {
      let tempArray = this.calculationColors;
      tempArray[calculation.id - 1] = this.temporaryColors[calculation.id - 1];
      this.calculationColors = [...tempArray];
      this.fillColor = this.temporaryColors[calculation.id - 1];
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
