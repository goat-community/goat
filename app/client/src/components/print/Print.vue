<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-subheader>
        <span class="title">{{ $t("appBar.printMap.title") }}</span>
      </v-subheader>

      <v-card-text class="pr-16 pl-16 pt-0 pb-0">
        <v-divider></v-divider>
      </v-card-text>
      <template
        v-if="
          isState('CAPABILITIES_NOT_LOADED') !== true &&
            isState('ERROR_ON_GETCAPABILITIES') !== true
        "
      >
        <v-card-text>
          <v-form ref="form" lazy-validation>
            <template v-for="(item, index) in layoutInfo.simpleAttributes">
              <span :key="index">
                <v-text-field
                  v-if="
                    item.type === 'text' &&
                      item.name != 'crsDescription' &&
                      item.name != 'attributions'
                  "
                  v-model="item.value"
                  :label="$t(`appBar.printMap.form.${item.name}.label`)"
                  type="text"
                  required
                ></v-text-field>
                <v-textarea
                  v-if="item.type === 'textarea'"
                  v-model="item.value"
                  rows="2"
                  auto-grow
                  :label="humanize(item.name)"
                ></v-textarea>
              </span>
            </template>

            <v-select
              v-model="layoutInfo.layout"
              :items="layoutInfo.layouts"
              item-text="name"
              item-value="name"
              prepend-icon="map"
              :label="$t('appBar.printMap.form.layout.label')"
              :rules="rules.required"
              @change="setLayout"
              required
            ></v-select>
            <v-select
              v-model="layoutInfo.scale"
              :items="layoutInfo.scales"
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
              v-model="layoutInfo.dpi"
              :items="layoutInfo.dpis"
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
                  v-model="layoutInfo.legend"
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
          <v-progress-circular
            indeterminate
            color="#30C2FF"
            class="mr-2"
            v-if="isState('PRINTING')"
          ></v-progress-circular>
          <v-btn
            class="white--text"
            v-if="isState('PRINTING')"
            color="error"
            @click="abort()"
          >
            <v-icon left>clear</v-icon
            >{{ $t("appBar.printMap.form.abort") }}</v-btn
          >
          <v-btn
            class="white--text"
            color="green"
            :disabled="isState('PRINTING')"
            @click="print('pdf')"
          >
            <v-icon left>print</v-icon
            >{{ $t("appBar.printMap.form.submit") }}</v-btn
          >
        </v-card-actions>
      </template>
      <v-card-text
        class="pr-16 pl-16 pt-2 pb-0"
        v-if="isState('CAPABILITIES_NOT_LOADED')"
      >
        <p class="subtitle-2">{{ $t("appBar.printMap.connectionMsg") }}</p>
      </v-card-text>
      <v-card-text
        class="pr-16 pl-16 pt-2 pb-0"
        v-if="isState('ERROR_ON_GETCAPABILITIES')"
      >
        <p class="subtitle-2">
          {{ $t("appBar.printMap.unavailableMsg") }}
        </p>
      </v-card-text>
    </v-card>
  </v-flex>
</template>

<script>
import { Mapable } from "../../mixins/Mapable";
import MaskLayer from "../../utils/PrintMask";

import PrintUtils, {
  INCHES_PER_METER,
  DOTS_PER_INCH
} from "../../utils/PrintUtils";
import PrintService from "../../controls/print/Service";
import {
  getFlatLayers,
  getWMTSLegendURL,
  getWMSLegendURL,
  getActiveBaseLayer
} from "../../utils/Layer";

import { humanize, numberWithCommas } from "../../utils/Helpers";
import axios from "axios";
import { mapMutations } from "vuex";
import * as olEvents from "ol/events.js";
import * as olMath from "ol/math.js";
import olLayerImage from "ol/layer/Image.js";
import olLayerTile from "ol/layer/Tile.js";
import olLayerGroup from "ol/layer/Group.js";
import olMap from "ol/Map.js";
import ImageWMS from "ol/source/ImageWMS.js";
import olSourceXYZ from "ol/source/XYZ";

var FileSaver = require("file-saver");
import { getCurrentDate, getCurrentTime } from "../../utils/Helpers";

export default {
  mixins: [Mapable],
  data: () => ({
    active: false,
    rules: {
      required: [v => !!v || "Field is required"]
    },
    printStateEnum: {
      NOT_IN_USE: "notInUse",
      PRINTING: "printing",
      ERROR_ON_REPORT: "errorOnReport",
      CAPABILITIES_NOT_LOADED: "capabilitiesNotLoaded",
      ERROR_ON_GETCAPABILITIES: "errorOnGetCapabilities"
    },
    printState: "capabilitiesNotLoaded",
    crs: [{ display: "Web Mercator", value: "EPSG:3857" }],
    selectedCrs: "EPSG:3857",
    outputFormats: [
      { display: "PDF", value: "pdf" },
      { display: "PNG", value: "png" }
    ],
    selectedFormat: "pdf",
    rotation: 0,
    showGrid: false,
    layoutInfo: {
      attributes: [],
      dpi: 120,
      dpis: [],
      layout: "",
      layouts: [],
      legend: true,
      scale: null,
      scales: [],
      simpleAttributes: []
    },
    maskLayer_: null,
    capabilities: null,
    currentJob: null,
    formats_: [],
    layouts_: [],
    layout_: null,
    fieldValues: {},
    paperSize_: [],
    rotateMask: false,
    legendOptions: {
      useBbox: true,
      label: {},
      params: {}
    },
    baseUrl: "./print",
    /**
     * Events
     */
    pointerDragListenerKey_: null,
    mapViewResolutionChangeKey_: null,
    onDragPreviousMousePosition_: null,
    rotationTimeoutPromise_: null,
    notPrintableTileSources: []
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

      const getSizeFn = () => this.paperSize_;
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
    },

    /**
     * Create a print report based on the values of the 'layoutInfo' values.
     * @param {string} format An output format corresponding to one format in the
     *     capabilities document ('pdf', 'png', etc).
     */
    print(format) {
      if (this.$refs.form.validate()) {
        if (!this.map) {
          throw new Error("Missing map");
        }

        // Do not print if a print task is already processing.
        if (this.printState === this.printStateEnum.PRINTING) {
          return;
        }
        this.printState = this.printStateEnum.PRINTING;

        const mapSize = this.map.getSize();
        const viewResolution = this.map.getView().getResolution() || 0;
        const scale =
          this.layoutInfo.scale ||
          this.getOptimalScale_(mapSize, viewResolution);
        const datasource = [];
        /** @type {Object<string, *>} */
        const customAttributes = {};
        if (this.layoutInfo.attributes.includes("datasource")) {
          customAttributes.datasource = datasource;
        }
        if (this.layoutInfo.simpleAttributes) {
          this.layoutInfo.simpleAttributes.forEach(field => {
            customAttributes[field.name] = field.value;
          });
        }

        if (this.layoutInfo.legend) {
          const center = this.map.getView().getCenter();
          if (!center) {
            throw new Error("Missing center");
          }
          const deltaX =
            (this.paperSize_[0] * scale) / 2 / INCHES_PER_METER / DOTS_PER_INCH;
          const deltaY =
            (this.paperSize_[1] * scale) / 2 / INCHES_PER_METER / DOTS_PER_INCH;
          const bbox = [
            center[0] - deltaX,
            center[1] - deltaY,
            center[0] + deltaX,
            center[1] + deltaY
          ];
          const legend = this.getLegend_(scale, this.layoutInfo.dpi, bbox);
          if (legend !== null) {
            customAttributes.legend = legend;
          }
        }
        if (typeof this.layoutInfo.dpi != "number") {
          throw new Error("Wrong layoutInfo.dpi type");
        }
        if (typeof this.layoutInfo.layout != "string") {
          throw new Error("Wrong layoutInfo.layout type");
        }

        //Add crs description
        customAttributes.crsDescription = this.selectedCrs;

        //Get Baselayer description\
        let attributions = "";
        const activeBaselayer = getActiveBaseLayer(this.map);
        if (activeBaselayer.length > 0) {
          const activeBaseLayerName = activeBaselayer[0].get("name");
          attributions = this.$appConfig.map.layers.filter(
            layerConf => layerConf.name === activeBaseLayerName
          )[0].attributions;
        }

        customAttributes.attributions = attributions;

        // convert the WMTS layers to WMS
        const map = new olMap({});
        map.setView(this.map.getView());
        const ol_layers = getFlatLayers(this.map.getLayerGroup());
        const new_ol_layers = [];
        let print_native_angle = true;
        for (let i = 0, ii = ol_layers.length; i < ii; i++) {
          let layer = ol_layers[i];

          // Get the print native angle parameter for WMS layers when set to not use default value
          // Is applied only once when the value is overridden with a metadata from administration
          if (
            layer instanceof olLayerImage &&
            layer.get("printNativeAngle") === false
          ) {
            print_native_angle = false;
          }

          new_ol_layers.push(layer);
        }
        const group = new olLayerGroup({
          layers: new_ol_layers
        });
        group.set("printNativeAngle", print_native_angle);
        map.setLayerGroup(group);

        const email =
          this.smtpSupported && this.smtpEmail && this.smtpEnabled
            ? this.smtpEmail
            : undefined;

        const spec = this.printService.createSpec(
          map,
          scale,
          this.layoutInfo.dpi,
          this.layoutInfo.layout,
          format,
          customAttributes,
          email
        );

        if (this.showGrid === true) {
          spec.attributes.map.layers.unshift(this.printService.getGridLayer());
        }

        // Add feature overlay layer to print spec.
        /** @type {import('print/mapfish-print-v3.js').MapFishPrintLayer[]} */
        const layers = [];
        this.printService.encodeLayer(
          layers,
          this.featureOverlayLayer_,
          viewResolution
        );
        if (layers.length > 0) {
          spec.attributes.map.layers.unshift(layers[0]);
        }

        //Print Overlays (for measure label)
        this.map.getOverlays().forEach(overlay => {
          // spec.attributes.map.layers.unshift(this.printService.encodeOverlay(overlay));
          const encodedOverlay = this.printService.encodeOverlay(overlay);
          if (encodedOverlay) {
            spec.attributes.map.layers.unshift(encodedOverlay);
          }
        });

        // Specify output format
        this.tempFormatValue = this.selectedFormat;
        spec.format = this.selectedFormat;

        this.printService
          .createReport(spec)
          .then(response => {
            if (response.status === 200) {
              this.currentJob = response.data;
              //Starts a interval timer every 1 second to check for the print job status
              this.getJobStatus();
            }
          })
          .catch(() => {
            this.printState = this.printStateEnum.NOT_IN_USE;
            this.currentJob = null;
            throw new Error("A server eror happened ");
          });

        // remove temporary map
        map.setTarget("");
      }
    },

    /**
     * Aborts the ongoing print job..
     * @private
     */
    abort() {
      const me = this;
      if (me.currentJob) {
        const refId = me.currentJob.ref;
        this.printService.cancelReportJob(refId);
        this.printState = this.printStateEnum.NOT_IN_USE;
      }

      if (me.polling) {
        clearInterval(me.polling);
      }

      me.currentJob = null;
    },

    /**
     * Download the report using reference id.
     * @param {string} refId The report reference id
     * @private
     */
    download(refId) {
      this.printService
        .downloadReport(refId)
        .then(response => {
          this.printState = this.printStateEnum.NOT_IN_USE;
          if (response.status === 200) {
            FileSaver.saveAs(
              response.data,
              `goat_print_${this.getCurrentDate()}_${this.getCurrentTime()}.${
                this.tempFormatValue
              }`
            );
          }
        })
        .catch(() => {
          this.printState = this.printStateEnum.NOT_IN_USE;
          throw new Error("A server eror happened ");
        });
    },

    getJobStatus() {
      const me = this;
      const jobRef = this.currentJob.ref;
      if (!jobRef) return;
      me.polling = setInterval(() => {
        if (me.currentJob) {
          me.printService.getStatus(jobRef).then(response => {
            const status = response.data.status;
            if (status === "finished" && me.currentJob) {
              clearInterval(me.polling);
              me.currentJob = null;
              me.download(jobRef);
            }
          });
        }
      }, 1500);
    },

    /**
     * Gets the print capabilities.
     * @param {string} roleId The roles ids.
     * @private
     */
    getCapabilities() {
      this.capabilities = axios.get(`${this.baseUrl}/goat/capabilities.json`);
    },

    /**
     * Create the list of layouts, get the formats, get the first layout in
     * gmf print v3 capabilities and then update the print panel layout information.
     * @param {axios} resp Response.
     */
    parseCapabilities_(resp) {
      const data = resp["data"];
      this.formats_ = data["formats"] || [];
      this.layouts_ = data["layouts"];
      this.layout_ = data["layouts"][1];

      this.layoutInfo.layouts = [];
      this.layouts_.forEach(layout => {
        this.layoutInfo.layouts.push(layout.name);
      });

      this.updateFields_();
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

      if (!this.layout_) {
        throw new Error("Missing layout");
      }
      this.layoutInfo.layout = this.layout_.name;

      const mapInfo = this.isAttributeInCurrentLayout_("map");
      if (!mapInfo) {
        throw new Error("Missing mapInfo");
      }
      const clientInfo = mapInfo.clientInfo;
      if (!clientInfo) {
        throw new Error("Missing clientInfo");
      }
      this.paperSize_ = [clientInfo.width, clientInfo.height];

      this.updateCustomFields_();

      const hasLegend = this.layoutInfo.attributes.includes("legend");
      if (hasLegend) {
        this.fieldValues.legend = this.fieldValues.legend;
      } else {
        delete this.fieldValues.legend;
      }
      this.layoutInfo.scales = clientInfo.scales || [];
      this.layoutInfo.dpis = clientInfo.dpiSuggestions || [];

      const mapSize = this.map.getSize();
      const viewResolution = this.map.getView().getResolution();
      this.layoutInfo.scale = this.getOptimalScale_(mapSize, viewResolution);

      this.layoutInfo.dpi =
        this.layoutInfo.dpi &&
        this.layoutInfo.dpis.indexOf(this.layoutInfo.dpi) > 0
          ? this.layoutInfo.dpi
          : this.layoutInfo.dpis[0];

      this.layoutInfo.formats = {};
      this.formats_.forEach(format => {
        this.layoutInfo.formats[format] = true;
      });

      this.attributesOut = this.layoutInfo.simpleAttributes;

      // Force the update of the mask
      this.map.render();
    },

    /**
     * Update simple attributes information with Customfield to be able to generate a form
     * from a custom GMF print v3 configuration.
     * @private
     */
    updateCustomFields_() {
      if (!this.layout_) {
        throw new Error("Missing layout");
      }
      if (!this.layoutInfo.simpleAttributes) {
        this.layoutInfo.simpleAttributes = [];
      }
      this.layoutInfo.attributes = [];

      const simpleAttributes = this.layoutInfo.simpleAttributes;
      const previousAttributes = simpleAttributes.splice(
        0,
        simpleAttributes.length
      );

      // The attributes without 'clientParams' are the custom layout information (defined by end user).
      this.layout_.attributes.forEach(attribute => {
        this.layoutInfo.attributes.push(attribute.name);
        if (!attribute.clientParams) {
          const name = `${attribute.name}`;
          const defaultValue = attribute.default;
          /** @type {string} */
          let value =
            defaultValue !== undefined && defaultValue !== ""
              ? `${defaultValue}`
              : name in this.fieldValues
              ? `${this.fieldValues[name]}`
              : "";

          // Try to use existing form field type
          const rawType = `${attribute.type}`;
          /** @type {string} */
          let type;
          switch (rawType) {
            case "String": {
              type = name === "comments" ? "textarea" : "text";
              break;
            }
            case "Boolean": {
              type = "checkbox";
              break;
            }
            case "Number": {
              type = "number";
              const numberValue = parseFloat(value);
              value = isNaN(numberValue) ? "0" : `${value}`;
              break;
            }
            default: {
              type = rawType;
            }
          }

          // If it exists use the value of previous same field.
          previousAttributes.forEach(c => {
            if (c.name === name && c.type === type) {
              value = c.value;
              return value;
            }
          });

          this.layoutInfo.simpleAttributes.push({
            name,
            type,
            value: value
          });
        }
      });
    },

    /**
     * Return a capabilities 'attribute' object corresponding to the given name.
     * @param {string} name Name of the attribute to get.
     * @return {?Object} corresponding attribute or null.
     * @private
     */
    isAttributeInCurrentLayout_(name) {
      if (!this.layout_) {
        throw new Error("Missing layout");
      }
      let attr = null;
      this.layout_.attributes.forEach(attribute => {
        if (attribute.name === name) {
          attr = attribute;
          return attribute;
        }
      });
      return attr;
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
      const scales = this.layoutInfo.scales.slice();
      if (mapSize !== undefined && viewResolution !== undefined) {
        return this.printUtils_.getOptimalScale(
          mapSize,
          viewResolution,
          this.paperSize_,
          scales.reverse()
        );
      }
      return this.layoutInfo.scales[0];
    },
    /**
     * @param {import('ol/PluggableMap.js').FrameState} frameState Frame state.
     * @return {number} Scale of the map to print.
     */
    getScaleFn(frameState) {
      // Don't compute an optimal scale if the user manually choose a value not in
      // the pre-defined scales. (`scaleInput` in `gmfPrintOptions`).
      if (this.layoutInfo.scale === undefined) {
        throw new Error("Missing layoutInfo.scale");
      }
      if (!this.layoutInfo.scales) {
        throw new Error("Missing layoutInfo.scales");
      }
      if (
        !this.scaleManuallySelected_ &&
        (this.layoutInfo.scale === -1 ||
          this.layoutInfo.scales.includes(this.layoutInfo.scale))
      ) {
        const mapSize = frameState.size;
        const viewResolution = frameState.viewState.resolution;
        this.layoutInfo.scale = this.getOptimalScale_(mapSize, viewResolution);
      }
      return this.layoutInfo.scale;
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
     * @param {number} scale The scale to get the legend (for wms layers only).
     * @param {number} dpi The DPI.
     * @param {number[]} bbox The bbox.
     * @return {Object?} Legend object for print report or null.
     * @private
     */
    getLegend_(scale, dpi, bbox) {
      if (!this.map) {
        throw new Error("Missing map");
      }
      /** @type {import('print/mapfish-print-v3').MapFishPrintLegend} */
      const legend = { classes: [] };

      // Get layers from layertree only.
      // const dataLayerGroup = getGroupFromMap(this.map, "group");
      const layers = getFlatLayers(this.map.getLayerGroup());

      // For each visible layer in reverse order, get the legend url.
      layers.reverse().forEach(layer => {
        if (!this.map) {
          throw new Error("Missing map");
        }
        /** @type {import('print/mapfish-print-v3').MapFishPrintLegendClass[]} */
        const classes = [];
        if (layer.getVisible() && layer.getSource()) {
          let icon_dpi;
          // For WMTS layers.
          if (layer instanceof olLayerTile) {
            const layerName = `${layer.get("layerNodeName")}`;

            const url = getWMTSLegendURL(layer);
            if (url) {
              icon_dpi = {
                url: url,
                dpi: 72
              };
            }

            // Don't add classes without legend url.
            if (icon_dpi) {
              classes.push({
                name: this.$te(`map.layerName.${layerName}`)
                  ? this.$t(`map.layerName.${layerName}`)
                  : layerName,
                icons: [icon_dpi.url]
              });
            }
          } else {
            const source = layer.getSource();
            if (source instanceof ImageWMS) {
              // For each name in a WMS layer.
              const layerNames = /** @type {string} */ source
                .getParams()
                .LAYERS.split(",");
              const _layerLegend = {
                name: this.$te(`map.layerName.${layer.get("name")}`)
                  ? this.$t(`map.layerName.${layer.get("name")}`)
                  : layer.get("name"),
                icons: []
              };
              layerNames.forEach(name => {
                if (!this.map) {
                  throw new Error("Missing map");
                }
                if (!source.serverType_) {
                  throw new Error("Missing source.serverType_");
                }

                let layerUrl = source.getUrl();
                if (layerUrl.startsWith("/")) {
                  layerUrl = window.location.origin + layerUrl;
                }

                const url = getWMSLegendURL(
                  layerUrl,
                  name,
                  scale,
                  undefined,
                  undefined,
                  undefined,
                  source.serverType_,
                  dpi,
                  this.legendOptions.useBbox ? bbox : undefined,
                  this.map
                    .getView()
                    .getProjection()
                    .getCode(),
                  this.legendOptions.params[source.serverType_],
                  this.$i18n.locale,
                  source.getParams().STYLES
                );
                if (!url) {
                  throw new Error("Missing url");
                }
                _layerLegend.icons.push(url);
              });
              classes.push(_layerLegend);
            }
          }
        }

        // Add classes object only if it contains something.
        if (classes.length > 0) {
          legend.classes = legend.classes.concat(classes);
        }
      });

      return legend.classes.length > 0 ? legend : null;
    },

    /**
     * Set the current layout and update all layout information with this new layout parameters.
     * @param {string} layoutName A layout name as existing in the list of
     *     existing layouts.
     */
    setLayout(layoutName) {
      /** @type {?import('print/mapfish-print-v3').MapFishPrintCapabilitiesLayout} */
      let layout = null;
      this.layouts_.forEach(l => {
        if (l.name === layoutName) {
          layout = l;
          return true; // break;
        }
      });
      this.layout_ = layout;
      this.updateFields_();
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
        this.layoutInfo.scale = opt_scale;
        const res = this.printUtils_.getOptimalResolution(
          mapSize,
          this.paperSize_,
          opt_scale
        );

        const view = this.map.getView();
        const contrainRes = view.getConstraints().resolution(res, 1, mapSize);
        view.setResolution(contrainRes);

        // Render the map to update the postcompose mask manually
        this.map.render();
        this.scaleManuallySelected_ = true;
      }
      return this.layoutInfo.scale;
    },

    /**
     * Set the print dpi value.
     * @param {number} dpi A dpi value as existing in the dpis list field.
     */
    setDpi(dpi) {
      this.layoutInfo.dpi = dpi;
    },

    /**
     * Check the current state of the print.
     * @param {string} stateEnumKey An enum key
     * @return {boolean} True if the given state matches with the current print
     *     state. False otherwise.
     */
    isState(stateEnumKey) {
      return this.printState === this.printStateEnum[stateEnumKey];
    },

    /**
     * Toggle alert message
     * @param {evt} Evt
     */
    toggleMessage(evt) {
      this.toggleSnackbar({
        type: "error",
        message: "cantPrintBaseLayer",
        timeout: 60000,
        state: !evt.oldValue
      });
    },
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
    })
  },
  activated: function() {
    this.active = true;
    if (!this.capabilities) {
      this.getCapabilities();
    }
    if (!this.capabilities) {
      throw new Error("Missing capabilities");
    }

    this.capabilities.then(
      resp => {
        if (!this.map) {
          throw new Error("Missing map");
        }

        // make sure the panel is still open
        if (!this.active) {
          return;
        }

        // Get capabilities - On success
        this.printState = this.printStateEnum.NOT_IN_USE;
        this.parseCapabilities_(resp);
        this.map.addLayer(this.maskLayer_);

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
        this.map.render();

        const ol_layers = getFlatLayers(this.map.getLayerGroup());

        ol_layers.forEach(layer => {
          if (
            layer instanceof olLayerTile &&
            !(layer.getSource() instanceof olSourceXYZ)
          ) {
            layer.on("change:visible", this.toggleMessage);
            this.notPrintableTileSources.push(layer);
            if (layer.getVisible() === true) {
              this.toggleSnackbar({
                type: "error",
                message: "cantPrintBaseLayer",
                timeout: 60000,
                state: true
              });
            }
          }
        });
      },
      () => {
        // Get capabilities - On error
        this.printState = this.printStateEnum.ERROR_ON_GETCAPABILITIES;
        this.capabilities_ = null;
      }
    );
  },
  deactivated: function() {
    this.active = false;
    if (!this.map) {
      throw new Error("Missing map");
    }
    this.map.removeLayer(this.maskLayer_);
    if (this.pointerDragListenerKey_) {
      olEvents.unlistenByKey(this.pointerDragListenerKey_);
    }
    if (this.mapViewResolutionChangeKey_) {
      olEvents.unlistenByKey(this.mapViewResolutionChangeKey_);
    }
    this.setRotation(0);
    this.map.render(); // Redraw (remove) post compose mask;
    this.abort();

    this.notPrintableTileSources.forEach(layer => {
      layer.un("change:visible", this.toggleMessage);
    });
    this.notPrintableTileSources = [];
    this.toggleSnackbar({
      type: "error",
      message: "cantPrintBaseLayer",
      timeout: 60000,
      state: false
    });
  }
};
</script>
