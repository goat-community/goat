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
            <v-select
              v-model="layout"
              :items="layouts"
              item-text="name"
              item-value="name"
              prepend-icon="map"
              :label="$t('appBar.printMap.form.layout.label')"
              :rules="rules.required"
              @change="setLayout"
              return-object
              required
            ></v-select>
            <v-select
              v-model="scale"
              :items="scales"
              prepend-icon="fas fa-ruler-horizontal"
              :label="$t('appBar.printMap.form.scale.label')"
              :rules="rules.required"
              @change="getSetScale"
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
              v-model="dpi"
              :items="dpis"
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
            </v-select>
            <v-select
              v-model="selectedCrs"
              :items="crs"
              prepend-icon="language"
              item-text="display"
              item-value="value"
              :label="$t('appBar.printMap.form.crs.label')"
              :rules="rules.required"
              required
            ></v-select>

            <v-select
              v-model="selectedFormat"
              :items="outputFormats"
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
                  :value="rotation"
                  @input="changeRotation"
                  track-color="#30C2FF"
                  color="#30C2FF"
                  :min="-180"
                  :max="180"
                ></v-slider>
              </v-flex>

              <v-flex xs3>
                <v-text-field
                  :value="rotation"
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
                  v-model="legend"
                  :label="$t('appBar.printMap.form.legend')"
                ></v-checkbox>
              </v-flex>
              <v-flex xs6>
                <v-checkbox
                  class="ml-1"
                  v-model="showGrid"
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
            @click="print('pdf')"
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
import MaskLayer from "../../utils/PrintMask";
import Graticule from "ol/layer/Graticule";
import { ScaleLine } from "ol/control";
import Stroke from "ol/style/Stroke";
import * as olEvents from "ol/events.js";
import * as olMath from "ol/math.js";
import { getPointResolution } from "ol/proj";
import PrintUtils from "../../utils/PrintUtils";
import { humanize, numberWithCommas } from "../../utils/Helpers";
import { mapGetters, mapMutations } from "vuex";
import { getCurrentDate, getCurrentTime } from "../../utils/Helpers";
import PrintService from "../../controls/print/Service";
import { jsPDF } from "jspdf";
import html2canvas from "html2canvas";
import { EventBus } from "../../EventBus";
export default {
  mixins: [Mapable],
  data: () => ({
    active: false,
    rules: {
      required: [v => !!v || "Field is required"]
    },
    crs: [{ display: "Web Mercator", value: "EPSG:3857" }],
    selectedCrs: "EPSG:3857",
    outputFormats: [{ display: "PDF", value: "pdf" }],
    selectedFormat: "pdf",
    rotation: 0,
    showGrid: false,
    gridLayer: undefined,
    dpi: 120,
    dpis: [254, 200, 120, 72],
    layout: {
      name: "A4 portrait",
      format: "a4",
      orientation: "portrait",
      size: [210, 297] // Get the size dynamically
    },
    layouts: [
      {
        name: "A4 portrait",
        format: "a4",
        orientation: "portrait",
        size: [210, 297]
      },
      {
        name: "A4 landscape",
        format: "a4",
        orientation: "landscape",
        size: [297, 210]
      }
    ],
    legend: true,
    scale: null,
    scales: [500000, 100000, 50000, 25000, 10000, 5000, 2500, 500, 250, 100],
    maskLayer_: null,
    rotateMask: false,
    baseUrl: "./print",
    /**
     * Events
     */
    pointerDragListenerKey_: null,
    mapViewResolutionChangeKey_: null,
    onDragPreviousMousePosition_: null,
    rotationTimeoutPromise_: null
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
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      if (!this.map) {
        throw new Error("Missing map");
      }
      this.printUtils_ = new PrintUtils();
      this.maskLayer_ = new MaskLayer();
      this.printService = new PrintService(this.baseUrl);

      olEvents.listen(this.map.getView(), "change:rotation", event => {
        this.updateRotation_(
          Math.round(olMath.toDegrees(event.target.getRotation()))
        );
      });

      const getSizeFn = () => this.layout.size;
      let getRotationFn;
      if (this.rotateMask) {
        /**
         * @return {number} rotation to apply.
         */
        getRotationFn = () => this.rotation;
      }

      this.maskLayer_.getSize = getSizeFn;
      this.maskLayer_.getScale = this.getScaleFn.bind(this);
      this.maskLayer_.getRotation = getRotationFn;
      this.updateFields_();
    },

    /**
     * Create a print report based on the values of the 'layoutInfo' values.
     * @param {string} format An output format corresponding to one format in the
     *     capabilities document ('pdf', 'png', etc).
     */
    print() {
      if (this.$refs.form.validate()) {
        if (!this.map) {
          throw new Error("Missing map");
        }
        if (this.legend) {
          EventBus.$emit("openLegend");
        }
        const map = this.map;
        const layout = this.layout;
        const dpi = this.dpi;
        const scale =
          this.scale || this.getOptimalScale_(mapSize, viewResolution);
        const mapView = map.getView();
        const format = layout.format;
        const orientation = layout.orientation;
        const paperSize = layout.size;
        const mapProjection = mapView.getProjection();
        const mapSize = map.getSize();
        const currZoom = mapView.getZoom();
        const viewResolution = map.getView().getResolution();
        const viewCenter = mapView.getCenter();

        const mapPointResolution = getPointResolution(
          mapProjection,
          viewResolution,
          viewCenter
        );
        var mapResolutionFactor = viewResolution / mapPointResolution;

        const width = Math.round((paperSize[0] * dpi) / 25.4); // in px
        const height = Math.round((paperSize[1] * dpi) / 25.4); // in px
        console.log(format, orientation, width, height);
        map.once("rendercomplete", async event => {
          console.log(event);
          var mapCanvas = document.createElement("canvas");
          mapCanvas.width = width;
          mapCanvas.height = height;
          var mapContext = mapCanvas.getContext("2d");
          Array.prototype.forEach.call(
            document.querySelectorAll(".ol-layer canvas"),
            function(canvas) {
              if (canvas.width > 0) {
                var opacity = canvas.parentNode.style.opacity;
                mapContext.globalAlpha = opacity === "" ? 1 : Number(opacity);
                var transform = canvas.style.transform;
                // Get the transform parameters from the style's transform matrix
                var matrix = transform
                  .match(/^matrix\(([^\(]*)\)$/)[1]
                  .split(",")
                  .map(Number);
                // Apply the transform to the export map context
                CanvasRenderingContext2D.prototype.setTransform.apply(
                  mapContext,
                  matrix
                );
                mapContext.drawImage(canvas, 0, 0);
              }
            }
          );
          var pdf = new jsPDF(orientation, undefined, format);
          pdf.addImage(mapCanvas, "JPEG", 0, 0, paperSize[0], paperSize[1]);

          // Reset size.
          map.setSize(mapSize);
          mapView.setZoom(currZoom);

          // Legend
          if (this.legend) {
            const legendEl = document.getElementById("legend");
            legendEl.style.paddingLeft = "10px";
            await this.timeout(300);
            const legendCanvas = await html2canvas(
              document.getElementById("legend"),
              { allowTaint: true }
            );
            legendEl.style.paddingLeft = "0px";
            const legendWidth = this.printUtils_.pix2mm(
              legendCanvas.width,
              dpi
            );
            const legendHeight = this.printUtils_.pix2mm(
              legendCanvas.height,
              dpi
            );
            pdf.addImage(
              legendCanvas,
              "JPEG",
              paperSize[0] - legendWidth,
              paperSize[1] - legendHeight,
              legendWidth,
              legendHeight
            );
          }

          // Save map
          const fileName = `goat_print_${this.getCurrentDate()}_${this.getCurrentTime()}.${
            this.selectedFormat
          }`;
          pdf.save(fileName);

          // Reset original map size
          map.setSize(mapSize);
          map.getView().setResolution(viewResolution);
        });

        var printPointResolution = (scale * 25.4) / (dpi * 1000); // edit1: corrected
        var printResolutionAtEquator =
          mapResolutionFactor * printPointResolution;
        var printZoom = mapView.getZoomForResolution(printResolutionAtEquator);

        map.setSize([width, height]);
        mapView.setZoom(printZoom);
      }
    },

    /**
     * Update layout information with the user values if there are always available in the
     * current layout otherwise use the defaults values of the layout.
     * If a field doesn't exist in the current layout, set it to undefined so the
     * view can hide it. Update also the paper size.
     * custom print templates).
     */
    updateFields_() {
      if (!this.map) {
        throw new Error("Missing map");
      }

      const mapSize = this.map.getSize();
      const viewResolution = this.map.getView().getResolution();
      this.scale = this.getOptimalScale_(mapSize, viewResolution);

      this.dpi =
        this.dpi && this.dpis.indexOf(this.dpi) > 0 ? this.dpi : this.dpis[0];

      // Force the update of the mask
      this.map.render();
    },

    /**
     * Calculate the angle and the sense of rotation between two lines. One from the
     * center of the map and the point of the last call to this function and one
     * from the same center and the point of the current call.
     * @param {import("ol/MapBrowserPointerEvent.js").default} e An ol map browser pointer event.
     * @private
     */
    onPointerDrag_(e) {
      const originalEvent = /** @type {KeyboardEvent} */ (e.originalEvent);
      const mapCenter = this.map.getView().getCenter();
      if (
        this.active &&
        originalEvent.altKey &&
        originalEvent.shiftKey &&
        mapCenter
      ) {
        const center = this.map.getPixelFromCoordinate(mapCenter);
        const pixel = e.pixel;
        // Reset previous position between two different sessions of drags events.
        if (this.rotationTimeoutPromise_ === null) {
          this.onDragPreviousMousePosition_ = null;
        } else {
          const p0x = this.onDragPreviousMousePosition_[0] - center[0];
          const p0y = this.onDragPreviousMousePosition_[1] - center[1];
          const p1x = pixel[0] - center[0];
          const p1y = pixel[1] - center[1];
          const centerToP0 = Math.sqrt(Math.pow(p0x, 2) + Math.pow(p0y, 2));
          const centerToP1 = Math.sqrt(Math.pow(p1x, 2) + Math.pow(p1y, 2));
          const sense = p0x * p1y - p0y * p1x > 0 ? 1 : -1;
          let angle = (p0x * p1x + p0y * p1y) / (centerToP0 * centerToP1);
          angle = angle <= 1 ? sense * Math.acos(angle) : 0;
          const boost = centerToP1 / 200;
          const increment = Math.round(olMath.toDegrees(angle) * boost);

          this.setRotation(this.rotation + increment);
        }

        this.onDragPreviousMousePosition_ = pixel;
      }
    },

    /**
     * Get the optimal scale to display the print mask. Return the first scale if
     * no scale matches.
     * @param {import("ol/size.js").Size|undefined} mapSize Size of the map on the screen (px).
     * @param {number|undefined} viewResolution Resolution of the map on the screen.
     * @return {number} The best scale. -1 is returned if there is no optimal
     *     scale, that is the optimal scale is lower than or equal to the first
     *     value in printMapScales.
     * @private
     */
    getOptimalScale_(mapSize, viewResolution) {
      const scales = this.scales.slice();
      if (mapSize !== undefined && viewResolution !== undefined) {
        return this.printUtils_.getOptimalScale(
          mapSize,
          viewResolution,
          this.layout.size,
          scales.reverse()
        );
      }
      return this.scales[0];
    },
    /**
     * @param {import('ol/PluggableMap.js').FrameState} frameState Frame state.
     * @return {number} Scale of the map to print.
     */
    getScaleFn(frameState) {
      // Don't compute an optimal scale if the user manually choose a value not in
      // the pre-defined scales. (`scaleInput` in `gmfPrintOptions`).
      if (this.scale === undefined) {
        throw new Error("Missing scale");
      }
      if (!this.scales) {
        throw new Error("Missing scales");
      }
      if (
        !this.scaleManuallySelected_ &&
        (this.scale === -1 || this.scales.includes(this.scale))
      ) {
        const mapSize = frameState.size;
        const viewResolution = frameState.viewState.resolution;
        this.scale = this.getOptimalScale_(mapSize, viewResolution);
      }
      return this.scale;
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
      // Render the map to update the postcompose mask or rotate the map.
      if (this.rotateMask) {
        this.map.render();
      } else {
        this.map.getView().setRotation(olMath.toRadians(this.rotation));
      }
    },

    /**
     * Set the current rotation value.
     * @param {number} rotation The optional new rotation value in degrees.
     */
    updateRotation_(rotation) {
      this.rotation = olMath.clamp(rotation, -180, 180);
    },

    /**
     * Set the current layout and update all layout information with this new layout parameters.
     * @param {string} layoutName A layout name as existing in the list of
     *     existing layouts.
     */
    setLayout(layoutName) {
      console.log(layoutName);
    },

    /**
     * Get or set the print scale value and adapt the zoom to match with this new scale.
     * @param {number=} opt_scale A scale value as existing in the scales list field.
     * @return {number|undefined} New scale.
     */
    getSetScale(opt_scale) {
      if (opt_scale !== undefined) {
        if (!this.map) {
          throw new Error("Missing map");
        }
        const mapSize = this.map.getSize() || [0, 0];
        this.scale = opt_scale;
        const res = this.printUtils_.getOptimalResolution(
          mapSize,
          this.layout.size,
          opt_scale
        );

        const view = this.map.getView();
        const contrainRes = view.getConstraints().resolution(res, 1, mapSize);
        view.setResolution(contrainRes);

        // Render the map to update the postcompose mask manually
        this.map.render();
        this.scaleManuallySelected_ = true;
      }
      return this.scale;
    },

    /**
     * Set the print dpi value.
     * @param {number} dpi A dpi value as existing in the dpis list field.
     */
    setDpi(dpi) {
      this.dpi = dpi;
    },
    timeout(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
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
      showLabels: true,
      wrapX: false
    });
    this.scaleLine = new ScaleLine({ bar: true, text: true, minWidth: 125 });
  },
  activated: function() {
    this.active = true;
    // this.map.addLayer(this.maskLayer_);
    this.pointerDragListenerKey_ = olEvents.listen(
      this.map,
      "pointerdrag",
      this.onPointerDrag_,
      this
    );
    this.mapViewResolutionChangeKey_ = olEvents.listen(
      this.map.getView(),
      "change:resolution",
      () => {
        this.scaleManuallySelected_ = false;
      }
    );
    // this.map.addControl(this.scaleLine);
    this.map.render();
  },
  deactivated: function() {
    this.active = false;
    if (!this.map) {
      throw new Error("Missing map");
    }
    // this.map.removeLayer(this.maskLayer_);
    if (this.pointerDragListenerKey_) {
      olEvents.unlistenByKey(this.pointerDragListenerKey_);
    }
    if (this.mapViewResolutionChangeKey_) {
      olEvents.unlistenByKey(this.mapViewResolutionChangeKey_);
    }
    this.setRotation(0);
    // this.map.removeControl(this.scaleLine);
    this.map.render(); // Redraw (remove) post compose mask;
  },
  computed: {
    ...mapGetters("app", {
      activeColor: "activeColor"
    })
  },
  watch: {
    showGrid(value) {
      if (value && this.gridLayer) {
        this.map.addLayer(this.gridLayer);
      }
      if (!value && this.gridLayer) {
        this.removeLayer(this.gridLayer);
      }
    }
  }
};
</script>
