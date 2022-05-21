<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-subheader>
        <span class="title">{{ $t("appBar.printMap.title") }}</span>
      </v-subheader>

      <v-card-text class="pr-16 pl-16 pt-0 pb-0">
        <v-divider></v-divider>
      </v-card-text>
      <template>
        <v-card-text>
          <v-form ref="form" lazy-validation>
            <v-text-field
              v-model="print.title"
              :label="$t(`appBar.printMap.form.title.label`)"
              type="text"
              maxlength="50"
              :counter="50"
            ></v-text-field>
            <v-select
              v-model="print.layout"
              :items="print.layouts"
              item-text="name"
              item-value="name"
              prepend-icon="map"
              :label="$t('appBar.printMap.form.layout.label')"
              :rules="rules.required"
              return-object
              required
            ></v-select>
            <v-select
              v-model="print.selectedCrs"
              :items="print.crs"
              prepend-icon="language"
              item-text="display"
              item-value="value"
              :label="$t('appBar.printMap.form.crs.label')"
              :rules="rules.required"
              required
            ></v-select>

            <v-select
              v-model="print.selectedFormat"
              :items="print.outputFormats"
              prepend-icon="description"
              item-text="display"
              item-value="value"
              :label="$t('appBar.printMap.form.outputFormat.label')"
              :rules="rules.required"
              required
            ></v-select>

            <v-layout row class="ml-0">
              <v-flex xs9 class="pr-3">
                <v-slider
                  class="pt-4"
                  prepend-icon="rotate_right"
                  :value="print.rotation"
                  @input="changeRotation"
                  :track-color="appColor.secondary"
                  :color="appColor.secondary"
                  :min="-180"
                  :max="180"
                ></v-slider>
              </v-flex>

              <v-flex xs3>
                <v-text-field
                  :value="print.rotation"
                  @input="changeRotation"
                  suffix="°"
                  class="mt-0"
                  type="number"
                ></v-text-field>
              </v-flex>
            </v-layout>
            <v-layout row class="ml-0 mt-2">
              <v-flex xs6>
                <v-checkbox
                  :color="appColor.secondary"
                  class="ml-1"
                  v-model="print.legend"
                  :label="$t('appBar.printMap.form.legend')"
                ></v-checkbox>
              </v-flex>
              <v-flex xs6>
                <v-checkbox
                  :color="appColor.secondary"
                  class="ml-1"
                  v-model="print.grid"
                  :label="$t('appBar.printMap.form.grid')"
                ></v-checkbox>
              </v-flex>
            </v-layout>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            class="white--text"
            :color="appColor.primary"
            @click="printMap"
          >
            <v-icon left>print</v-icon
            >{{ $t("appBar.printMap.form.submit") }}</v-btn
          >
        </v-card-actions>
      </template>
    </v-card>
  </v-flex>
</template>

<script>
import { Mapable } from "../../mixins/Mapable";
import * as olEvents from "ol/events.js";
import * as olMath from "ol/math.js";
// import { getPointResolution } from "ol/proj";
import { humanize, numberWithCommas } from "../../utils/Helpers";
import { mapGetters, mapMutations } from "vuex";
import { mapFields } from "vuex-map-fields";
import { getCurrentDate, getCurrentTime } from "../../utils/Helpers";
import Graticule from "ol/layer/Graticule";
import olScaleLine from "ol/control/ScaleLine";
import Stroke from "ol/style/Stroke";
import OlRotate from "ol/control/Rotate";
import OlAttribution from "ol/control/Attribution";
import OlMouseWheelZoom from "ol/interaction/MouseWheelZoom";

import { jsPDF } from "jspdf";
import html2canvas from "html2canvas";
export default {
  mixins: [Mapable],
  data: () => ({
    rules: {
      required: [v => !!v || "Field is required"]
    },
    rotationListenerKey: null,
    scaleLineControl: null,
    gridLineControl: null,
    defaultOlRotateControl: null,
    defaultOlAttributionControl: null,
    defaultOlMouseWheelZoom: null
  }),
  methods: {
    humanize,
    numberWithCommas,
    getCurrentDate,
    getCurrentTime,
    changeRotation(rotation) {
      this.setRotation(rotation);
    },

    /**
     * Create a print report based on the values of the 'layoutInfo' values.
     * @param {string} format An output format corresponding to one format in the
     *     capabilities document ('pdf').
     */
    async printMap() {
      const orientation = this.print.layout.orientation;
      const format = this.print.layout.format;
      const paperSize = this.print.layout.size;
      // Convert html to canvas
      const printCanvas = await html2canvas(
        document.getElementById("map-print-wrapper"),
        {
          scale: 5,
          allowTaint: true,
          useCORS: true
        }
      );
      const fileName = `goat_print_${this.getCurrentDate()}_${this.getCurrentTime()}.${
        this.print.selectedFormat
      }`;
      if (this.print.selectedFormat === "png") {
        var a = document.createElement("a");
        // toDataURL defaults to png, so we need to request a jpeg, then convert for file download.
        a.href = printCanvas
          .toDataURL("image/png")
          .replace("image/png", "image/octet-stream");
        a.download = fileName;
        a.click();
      } else {
        var pdf = new jsPDF(orientation, undefined, format);
        // Add image to pdf
        pdf.addImage(printCanvas, "JPEG", 0, 0, paperSize[0], paperSize[1]);
        // Save map
        pdf.save(fileName);
      }
    },
    /**
     * Set the current rotation value.
     * Updating the rotation will redraw the mask or rotate the map (depending on the configuration).
     * @param {number} rotation The optional new rotation value in degrees.
     */
    setRotation(rotation) {
      if (!this.map) {
        throw new Error("Missing map");
      }
      this.updateRotation_(rotation);

      this.map.getView().setRotation(olMath.toRadians(this.print.rotation));
    },

    /**
     * Set the current rotation value.
     * @param {number} rotation The optional new rotation value in degrees.
     */
    updateRotation_(rotation) {
      this.print.rotation = olMath.clamp(rotation, -180, 180);
    },

    /**
     * Set the print dpi value.
     * @param {number} dpi A dpi value as existing in the dpis list field.
     */
    setDpi(dpi) {
      this.print.dpi = dpi;
    },
    timeout(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
    })
  },
  activated: function() {
    this.print.active = true;
    this.rotationListenerKey = olEvents.listen(
      this.map.getView(),
      "change:rotation",
      event => {
        this.updateRotation_(
          Math.round(olMath.toDegrees(event.target.getRotation()))
        );
      }
    );

    if (this.defaultOlRotateControl) {
      this.defaultOlRotateControl.setMap(null);
    }
    if (this.defaultOlAttributionControl) {
      this.defaultOlAttributionControl.setCollapsed(false);
      this.defaultOlAttributionControl.setCollapsible(false);
    }
    if (this.defaultOlMouseWheelZoom) {
      this.defaultOlMouseWheelZoom.setActive(false);
    }
    this.map.addControl(this.scaleLineControl);
    this.isochroneLayer
      .getSource()
      .getFeatures()
      .forEach(feature => {
        feature.set("showLabel", true);
      });
    this.isochroneLayer.getSource().changed();
  },
  deactivated: function() {
    this.print.active = false;
    this.print.grid = false;
    if (!this.map) {
      throw new Error("Missing map");
    }
    if (this.gridLayer) {
      this.map.removeLayer(this.gridLayer);
    }
    if (this.rotationListenerKey) {
      olEvents.unlistenByKey(this.rotationListenerKey);
    }
    this.map.removeControl(this.scaleLineControl);
    if (this.defaultOlRotateControl) {
      this.defaultOlRotateControl.setMap(this.map);
    }
    if (this.defaultOlAttributionControl) {
      this.defaultOlAttributionControl.setCollapsed(true);
      this.defaultOlAttributionControl.setCollapsible(true);
    }
    if (this.defaultOlMouseWheelZoom) {
      this.defaultOlMouseWheelZoom.setActive(true);
    }
    this.isochroneLayer
      .getSource()
      .getFeatures()
      .forEach(feature => {
        feature.set("showLabel", false);
      });
    this.isochroneLayer.getSource().changed();
    this.setRotation(0);
    this.map.render();
  },
  computed: {
    ...mapGetters("app", {
      appColor: "appColor"
    }),
    ...mapFields("map", {
      print: "print"
    }),
    ...mapGetters("isochrones", {
      isochroneLayer: "isochroneLayer"
    })
  },
  created() {
    this.gridLayer = new Graticule({
      // the style to use for the lines, optional.
      strokeStyle: new Stroke({
        color: "rgba(255,120,0,0.9)",
        width: 2,
        lineDash: [0.5, 4]
      }),
      zIndex: 1000,
      showLabels: true,
      wrapX: false
    });
    this.scaleLineControl = new olScaleLine({
      steps: 2,
      bar: true,
      text: true
    });
    this.map
      .getControls()
      .getArray()
      .forEach(control => {
        if (control instanceof OlRotate) {
          this.defaultOlRotateControl = control;
        }
        if (control instanceof OlAttribution) {
          this.defaultOlAttributionControl = control;
        }
        if (control instanceof OlMouseWheelZoom) {
          this.defaultOlMouseWheelZoom = control;
        }
      });
  },
  watch: {
    "print.grid": function(state) {
      if (state && this.gridLayer) {
        this.map.addLayer(this.gridLayer);
      }
      if (!state && this.gridLayer) {
        this.map.removeLayer(this.gridLayer);
      }
    }
  }
};
</script>
