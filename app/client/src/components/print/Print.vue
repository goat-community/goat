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
              maxlength="40"
              :counter="40"
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
            <!-- <v-select
              v-model="print.scale"
              :items="print.scales"
              prepend-icon="fas fa-ruler-horizontal"
              :label="$t('appBar.printMap.form.scale.label')"
              :rules="rules.required"
              required
            >
              <template slot="selection" slot-scope="{ item }">
                1 : {{ numberWithCommas(item) }}
              </template>
              <template slot="item" slot-scope="{ item }">
                1 : {{ numberWithCommas(item) }}
              </template>
            </v-select>
            <v-select
              v-model="print.dpi"
              :items="print.dpis"
              prepend-icon="aspect_ratio"
              :label="$t('appBar.printMap.form.resolution.label')"
              :rules="rules.required"
              @change="setDpi"
              required
            >
              <template slot="selection" slot-scope="{ item }">
                {{ item }} dpi
              </template>
              <template slot="item" slot-scope="{ item }">
                {{ item }} dpi
              </template>
            </v-select> -->
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
                  track-color="#30C2FF"
                  color="#30C2FF"
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
                  class="ml-1"
                  v-model="print.legend"
                  :label="$t('appBar.printMap.form.legend')"
                ></v-checkbox>
              </v-flex>
              <v-flex xs6>
                <v-checkbox
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
            :color="activeColor.primary"
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
    // print() {
    //   if (this.$refs.form.validate()) {
    //     if (!this.map) {
    //       throw new Error("Missing map");
    //     }
    //     if (this.legend) {
    //       EventBus.$emit("openLegend");
    //     }
    //     const map = this.map;
    //     const layout = this.layout;
    //     const dpi = this.dpi;
    //     const scale = this.scale;
    //     const mapView = map.getView();
    //     const format = layout.format;
    //     const orientation = layout.orientation;
    //     const paperSize = layout.size;
    //     const mapProjection = mapView.getProjection();
    //     const mapSize = map.getSize();
    //     const currZoom = mapView.getZoom();
    //     const viewResolution = map.getView().getResolution();
    //     const viewCenter = mapView.getCenter();

    //     const mapPointResolution = getPointResolution(
    //       mapProjection,
    //       viewResolution,
    //       viewCenter
    //     );
    //     var mapResolutionFactor = viewResolution / mapPointResolution;

    //     const width = Math.round((paperSize[0] * dpi) / 25.4); // in px
    //     const height = Math.round((paperSize[1] * dpi) / 25.4); // in px
    //     console.log(format, orientation, width, height);
    //     map.once("rendercomplete", async event => {
    //       console.log(event);
    //       var mapCanvas = document.createElement("canvas");
    //       mapCanvas.width = width;
    //       mapCanvas.height = height;
    //       var mapContext = mapCanvas.getContext("2d");
    //       Array.prototype.forEach.call(
    //         document.querySelectorAll(".ol-layer canvas"),
    //         function(canvas) {
    //           if (canvas.width > 0) {
    //             var opacity = canvas.parentNode.style.opacity;
    //             mapContext.globalAlpha = opacity === "" ? 1 : Number(opacity);
    //             var transform = canvas.style.transform;
    //             // Get the transform parameters from the style's transform matrix
    //             var matrix = transform
    //               .match(/^matrix\(([^\(]*)\)$/)[1]
    //               .split(",")
    //               .map(Number);
    //             // Apply the transform to the export map context
    //             CanvasRenderingContext2D.prototype.setTransform.apply(
    //               mapContext,
    //               matrix
    //             );
    //             mapContext.drawImage(canvas, 0, 0);
    //           }
    //         }
    //       );
    //       var pdf = new jsPDF(orientation, undefined, format);
    //       pdf.addImage(mapCanvas, "JPEG", 0, 0, paperSize[0], paperSize[1]);

    //       // Reset size.
    //       map.setSize(mapSize);
    //       mapView.setZoom(currZoom);

    //       // Legend
    //       if (this.legend) {
    //         const legendEl = document.getElementById("legend");
    //         legendEl.style.paddingLeft = "10px";
    //         await this.timeout(300);
    //         const legendCanvas = await html2canvas(
    //           document.getElementById("legend"),
    //           { allowTaint: true, useCORS: true }
    //         );
    //         legendEl.style.paddingLeft = "0px";
    //         const legendWidth = this.printUtils_.pix2mm(
    //           legendCanvas.width,
    //           dpi
    //         );
    //         const legendHeight = this.printUtils_.pix2mm(
    //           legendCanvas.height,
    //           dpi
    //         );
    //         pdf.addImage(
    //           legendCanvas,
    //           "JPEG",
    //           paperSize[0] - legendWidth,
    //           paperSize[1] - legendHeight,
    //           legendWidth,
    //           legendHeight
    //         );
    //       }

    //       // Save map
    //       const fileName = `goat_print_${this.getCurrentDate()}_${this.getCurrentTime()}.${
    //         this.selectedFormat
    //       }`;
    //       pdf.save(fileName);

    //       // Reset original map size
    //       map.setSize(mapSize);
    //       map.getView().setResolution(viewResolution);
    //     });

    //     var printPointResolution = (scale * 25.4) / (dpi * 1000); // edit1: corrected
    //     var printResolutionAtEquator =
    //       mapResolutionFactor * printPointResolution;
    //     var printZoom = mapView.getZoomForResolution(printResolutionAtEquator);

    //     map.setSize([width, height]);
    //     mapView.setZoom(printZoom);
    //   }
    // },

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
  },
  deactivated: function() {
    this.print.active = false;
    if (!this.map) {
      throw new Error("Missing map");
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
    this.setRotation(0);
    this.map.render();
  },
  computed: {
    ...mapGetters("app", {
      activeColor: "activeColor"
    }),
    ...mapFields("map", {
      print: "print"
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
