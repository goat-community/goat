<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <template>
        <!-- ISOCHRONE OPTIONS  -->
        <v-flex xs12>
          <v-card-text class="pr-16 pl-16 pt-0 pb-0">
            <v-divider></v-divider>
          </v-card-text>
          <v-subheader
            class="clickable"
            @click="isOptionsElVisible = !isOptionsElVisible"
          >
            <v-icon small class="mr-2">fas fa-sliders-h</v-icon>
            <h3>{{ $t("isochrones.options.title") }}</h3>
            <v-spacer></v-spacer>
            <v-icon
              v-html="isOptionsElVisible === true ? 'remove' : 'add'"
            ></v-icon>
          </v-subheader>
          <div v-if="isOptionsElVisible">
            <v-expand-transition>
              <v-flex
                xs12
                class="mx-4 isochroneOptions"
                v-if="isIsochroneOptionsVisible"
              >
                <v-row class="mt-n2" align="center">
                  <v-col class="d-flex mb-0 pb-0" cols="12" sm="6">
                    <v-select
                      label="Routing"
                      class="mb-2 mt-0"
                      item-value="type"
                      v-model="routing"
                      :items="appConfig.routing"
                    >
                      <template slot="selection" slot-scope="{ item }">
                        <v-row>
                          <v-col cols="3"
                            ><v-icon dense>{{ item.icon }}</v-icon></v-col
                          >
                          <v-col cols="9"
                            ><span class="cb-item">{{
                              $t(`isochrones.options.${item.type}`)
                            }}</span></v-col
                          >
                        </v-row>
                      </template>
                      <template slot="item" slot-scope="{ item }">
                        <v-row>
                          <v-col cols="3"
                            ><v-icon dense>{{ item.icon }}</v-icon></v-col
                          >
                          <v-col cols="9"
                            ><span class="cb-item">{{
                              $t(`isochrones.options.${item.type}`)
                            }}</span></v-col
                          >
                        </v-row>
                      </template>
                    </v-select>
                  </v-col>
                  <v-col class="d-flex mb-0 pb-0" cols="12" sm="6">
                    <v-text-field
                      label="Speed"
                      type="number"
                      step="any"
                      min="1"
                      max="40"
                      ref="input"
                      :rules="[speedRule]"
                      v-model="speed"
                      suffix="km/h"
                    ></v-text-field>
                  </v-col>
                  <v-col class="d-flex mt-0 pt-0" cols="12" sm="6">
                    <v-text-field
                      label="Time"
                      type="number"
                      step="any"
                      min="1"
                      max="20"
                      ref="input"
                      :rules="[timeRule]"
                      v-model="time"
                      suffix="min"
                    ></v-text-field>
                  </v-col>
                  <v-col class="d-flex mt-0 pt-0" cols="12" sm="6">
                    <v-text-field
                      label="Steps"
                      type="number"
                      step="any"
                      min="1"
                      max="4"
                      ref="input"
                      v-model="steps"
                    ></v-text-field>
                  </v-col>
                </v-row>
              </v-flex>
            </v-expand-transition>
          </div>
        </v-flex>

        <!-- ISOCHRONE TYPE -->
        <v-flex xs12>
          <v-subheader
            @click="
              isIsochroneCalculationTypeElVisible = !isIsochroneCalculationTypeElVisible
            "
            class="clickable pb-0 mb-0"
          >
            <v-icon class="mr-2" small>fas fa-bullseye</v-icon>
            <h3>{{ $t("isochrones.calculationTitle") }}</h3>
            <v-spacer></v-spacer>
            <v-icon
              v-html="
                isIsochroneCalculationTypeElVisible === true ? 'remove' : 'add'
              "
            ></v-icon>
          </v-subheader>
          <v-card-text
            v-show="isIsochroneCalculationTypeElVisible"
            class="py-0 my-0 justify-center"
          >
            <v-row>
              <v-radio-group
                class="ml-2 mt-4 radio-group-height"
                :value="type"
                v-model="type"
                row
              >
                <v-radio
                  :color="appColor.secondary"
                  :label="$t('isochrones.single.type')"
                  value="single"
                ></v-radio>
                <v-radio
                  :color="appColor.secondary"
                  :label="$t('isochrones.multiple.type')"
                  value="multiple"
                ></v-radio>
              </v-radio-group>
              <v-spacer></v-spacer>
              <span v-if="!isMapBusy && type == 'single'">
                <v-tooltip top>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      outlined
                      fab
                      v-on="on"
                      class="ml-2 mr-4"
                      depressed
                      text
                      @click="registerMapClick('isochrone')"
                    >
                      <v-icon
                        :color="mapClickListener ? appColor.secondary : 'grey'"
                        >fas fa-map-marker-alt</v-icon
                      >
                    </v-btn>
                  </template>
                  <span>{{ $t("isochrones.single.startTooltip") }}</span>
                </v-tooltip>
              </span>
            </v-row>
          </v-card-text>
        </v-flex>

        <!-- ISOCHRONE TYPE (MULTIPLE) -->
        <v-flex xs12 v-if="type === 'multiple'">
          <v-flex
            xs12
            v-show="isIsochroneStartElVisible"
            style="overflow: hidden;"
            class="mx-4"
          >
            <v-select
              item-value="value"
              :disabled="isMapBusy"
              class="select-method-height mx-1 my-1"
              v-model="activeMultiIsochroneMethod"
              :items="multiIsochroneCalculationMethods.values"
              @change="toggleInteraction"
              :label="$t('isochrones.multiple.selectMethod')"
              solo
            >
              <template slot="selection" slot-scope="{ item }">
                {{ $t(`isochrones.multiple.${item.name}`) }}
              </template>
              <template slot="item" slot-scope="{ item }">
                {{ $t(`isochrones.multiple.${item.name}`) }}
              </template>
            </v-select>
            <!-- STOP CALC -->
            <v-card-actions v-if="isMapBusy">
              <v-spacer></v-spacer>
              <v-tooltip v-if="isMapBusy" top>
                <template v-if="isMapBusy" v-slot:activator="{ on }">
                  <v-btn
                    v-show="isMapBusy"
                    v-on="on"
                    small
                    @click.stop="stopIsochroneCalc"
                    class="white--text"
                    color="error"
                  >
                    <v-icon color="white">close</v-icon
                    >{{ $t("buttonLabels.stop") }}
                  </v-btn>
                </template>
                <span>{{ $t("isochrones.stopIsochroneCalc") }}</span>
              </v-tooltip>
            </v-card-actions>

            <template v-if="this.activeMultiIsochroneMethod !== null">
              <v-alert
                border="left"
                colored-border
                class="mb-0 mt-2 mx-1 elevation-2"
                :icon="countPois > 150 ? 'warning' : 'info'"
                :color="countPois > 150 ? 'warning' : appColor.primary"
                dense
              >
                <span v-html="getInfoLabelText"></span>
              </v-alert>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn class="white--text" color="error" @click="clear">
                  {{ $t("isochrones.multiple.clear") }}
                </v-btn>
                <v-btn
                  :disabled="isCalculationDisabled"
                  class="white--text mr-1"
                  :color="activeColor.primary"
                  :loading="isMapBusy"
                  @click="calcuateBtn"
                >
                  {{ $t("isochrones.multiple.calculate") }}
                </v-btn>
              </v-card-actions>
            </template>
          </v-flex>
          <v-progress-linear
            v-if="isMapBusy"
            indeterminate
            height="1"
            class="mx-0 pb-0"
            :color="activeColor.primary"
          ></v-progress-linear>
        </v-flex>

        <!-- ISOCHRONE RESULT -->
        <v-flex id="isochroneResultsEl">
          <v-card-text class="pr-16 pl-16 pt-0 pb-0">
            <v-divider></v-divider>
          </v-card-text>
          <v-subheader
            class="clickable"
            @click="isResultsElVisible = !isResultsElVisible"
          >
            <v-icon
              class="mr-2"
              :style="
                isResultsElVisible === true ? { color: appColor.secondary } : {}
              "
              style="margin-right: 2px;"
              small
              >far fa-list-alt</v-icon
            >
            <h3>{{ $t("isochrones.results.title") }}</h3>
            <v-spacer></v-spacer>

            <v-btn
              v-show="isResultsElVisible === true && calculations.length > 1"
              small
              @click.stop="deleteAll"
              class="white--text"
              color="error"
            >
              <v-icon left>delete</v-icon
              >{{ $t("isochrones.results.deleteAll") }}
            </v-btn>
            <v-icon
              v-html="isResultsElVisible === true ? 'remove' : 'add'"
            ></v-icon>
          </v-subheader>
          <v-layout>
            <v-flex xs12 class="mx-3" v-show="isResultsElVisible">
              <template v-for="calculation in calculations">
                <v-card
                  class="mb-3 "
                  :id="`result-${calculation.id}`"
                  :key="calculation.id"
                  :class="{
                    'elevation-5': isCalculationActive(calculation)
                  }"
                >
                  <!-- Isochrone Nr -->
                  <v-chip
                    x-small
                    dark
                    label
                    :color="
                      isCalculationActive(calculation) ? '#30C2FF' : '#676767'
                    "
                    style="padding:5px;"
                    class="isochrone-nr"
                  >
                    <span
                      ><b>{{ calculation.id }}</b></span
                    >
                  </v-chip>
                  <v-card-title class="pb-0 mb-0">
                    <v-layout row wrap>
                      <v-layout align-start justify-start>
                        <v-card-text class="pa-0 ma-0 ml-3">
                          <v-chip small class="mr-1 my-1">
                            <v-avatar left>
                              <v-icon small class="text-xs-center">{{
                                routingProfiles[calculation.routing_profile]
                                  .icon
                              }}</v-icon>
                            </v-avatar>
                            {{
                              $t(
                                `isochrones.options.${calculation.routing_profile}`
                              )
                            }}
                          </v-chip>
                          <v-chip
                            v-if="calculation.scenario_id"
                            small
                            class="mr-0 my-1"
                          >
                            <v-tooltip top>
                              <template v-slot:activator="{ on }">
                                <span v-on="on" class="chip-label-custom">
                                  {{ scenarios[calculation.scenario_id].title }}
                                </span> </template
                              ><span>{{
                                scenarios[calculation.scenario_id].title
                              }}</span></v-tooltip
                            >
                          </v-chip>
                        </v-card-text>
                      </v-layout>

                      <v-layout row>
                        <v-spacer></v-spacer>
                        <v-tooltip top>
                          <template v-slot:activator="{ on }">
                            <v-icon
                              small
                              v-on="on"
                              @click="toggleIsochroneWindow(calculation)"
                              :color="
                                isCalculationActive(calculation)
                                  ? '#30C2FF'
                                  : '#676767'
                              "
                              class="result-icons mr-1"
                              >fas fa-table</v-icon
                            >
                          </template>
                          <span>{{
                            isCalculationActive(calculation)
                              ? $t("isochrones.results.hideDataTooltip")
                              : $t("isochrones.results.showDataTooltip")
                          }}</span>
                        </v-tooltip>

                        <v-tooltip top>
                          <template v-slot:activator="{ on }">
                            <v-icon
                              small
                              v-on="on"
                              @click="showAdditionalLayerDialog(calculation)"
                              class="result-icons mr-1"
                              >fas fa-layer-group</v-icon
                            >
                          </template>
                          <span>{{
                            $t("isochrones.results.additionalLayers")
                          }}</span>
                        </v-tooltip>

                        <v-tooltip top>
                          <template v-slot:activator="{ on }">
                            <v-icon
                              @click="showHideCalculation(calculation)"
                              small
                              v-on="on"
                              class="result-icons mr-1"
                              v-html="
                                calculation.isVisible
                                  ? 'fas fa-eye-slash'
                                  : 'fas fa-eye'
                              "
                            ></v-icon>
                          </template>
                          <span>{{
                            calculation.isVisible
                              ? $t("isochrones.results.hideResultsTooltip")
                              : $t("isochrones.results.showResultsTooltip")
                          }}</span>
                        </v-tooltip>

                        <v-tooltip top>
                          <template v-slot:activator="{ on }">
                            <v-icon
                              @click="toggleDownloadDialog(calculation)"
                              small
                              v-on="on"
                              class="result-icons mr-1"
                              >fas fa-download</v-icon
                            >
                          </template>
                          <span>{{
                            $t("isochrones.results.downloadTooltip")
                          }}</span>
                        </v-tooltip>

                        <v-tooltip top>
                          <template v-slot:activator="{ on }">
                            <v-icon
                              @click="deleteCalculation(calculation)"
                              small
                              v-on="on"
                              class="result-icons delete-icon mr-6"
                            >
                              fas fa-trash-alt</v-icon
                            >
                          </template>
                          <span>{{
                            $t("isochrones.results.deleteCalcTooltip")
                          }}</span>
                        </v-tooltip>
                      </v-layout>
                    </v-layout>
                    <v-card-text class="pr-0 pl-0 pt-0 pb-0">
                      <v-divider></v-divider>

                      <v-layout class="ml-0" row>
                        <v-chip small class="my-1 mr-1">
                          <v-avatar left>
                            <v-icon small class="text-xs-center"
                              >fas fa-clock</v-icon
                            >
                          </v-avatar>
                          {{ calculation.time }}
                        </v-chip>

                        <v-chip small class="my-1 ">
                          <v-avatar left>
                            <v-icon small class="text-xs-center"
                              >fas fa-tachometer-alt</v-icon
                            >
                          </v-avatar>
                          {{ calculation.speed }}
                        </v-chip>
                        <v-spacer></v-spacer>
                        <v-tooltip top>
                          <template v-slot:activator="{ on }">
                            <div
                              v-if="
                                calculation.calculationMode === 'scenario' ||
                                  calculation.calculationMode === 'comparison'
                              "
                              v-on="on"
                              @click="
                                toggleColorPickerDialog(calculation, 'scenario')
                              "
                              class="my-1 ml-1 mr-2 colorPalettePicker"
                              :style="{
                                backgroundImage: `linear-gradient(to right, ${getPaletteColor(
                                  calculation,
                                  'scenario'
                                )})`
                              }"
                            ></div>
                          </template>
                          <span>{{
                            $t(`map.tooltips.changeScenarioColorPalette`)
                          }}</span>
                        </v-tooltip>

                        <v-tooltip top>
                          <template v-slot:activator="{ on }">
                            <div
                              v-if="
                                calculation.calculationMode === 'default' ||
                                  calculation.calculationMode === 'comparison'
                              "
                              @click="
                                toggleColorPickerDialog(calculation, 'default')
                              "
                              v-on="on"
                              class="my-1 mr-2 colorPalettePicker"
                              :style="{
                                backgroundImage: `linear-gradient(to right, ${getPaletteColor(
                                  calculation,
                                  'default'
                                )})`
                              }"
                            ></div>
                          </template>
                          <span>{{
                            $t(`map.tooltips.changeDefaultColorPalette`)
                          }}</span>
                        </v-tooltip>
                      </v-layout>
                    </v-card-text>
                  </v-card-title>
                  <v-subheader
                    class="clickable subheader mt-1 pb-1"
                    @click="calculation.isExpanded = !calculation.isExpanded"
                  >
                    <v-icon
                      small
                      class="mr-2"
                      v-html="
                        calculation.isExpanded
                          ? 'fas fa-chevron-down'
                          : 'fas fa-chevron-right'
                      "
                    ></v-icon>
                    <v-tooltip
                      :disabled="
                        calculation.position === 'multiIsochroneCalculation'
                      "
                      open-delay="600"
                      max-width="300"
                      top
                    >
                      <template v-slot:activator="{ on }">
                        <h3 class="result-title" v-on="on">
                          {{
                            calculation.position === "multiIsochroneCalculation"
                              ? $t("isochrones.results.multiIsochroneHeader")
                              : calculation.position
                          }}
                        </h3>
                      </template>
                      <span>{{ calculation.position }}</span></v-tooltip
                    >
                  </v-subheader>

                  <v-card-text class="pt-0 " v-show="calculation.isExpanded">
                    <v-data-table
                      :headers="headers"
                      :items="calculation.data"
                      class="elevation-1 subtitle-1"
                      hide-default-footer
                      light
                    >
                      <template v-slot:items="props">
                        <td>{{ props.item.type }}</td>
                        <td>{{ props.item.range }}</td>
                        <td>{{ props.item.area }}</td>
                      </template>
                      <template v-slot:item.visible="{ item }">
                        <v-switch
                          :input-value="item.isVisible"
                          primary
                          hide-details
                          @change="toggleIsochroneVisibility(item, calculation)"
                        ></v-switch>
                      </template>
                      <template v-slot:item.legend="{ item }">
                        <div
                          class="legend"
                          :style="{ backgroundColor: item.color }"
                        ></div>
                      </template>
                    </v-data-table>
                  </v-card-text>
                </v-card>
              </template>
            </v-flex>
            <confirm ref="confirm"></confirm>
            <!-- DIALOG BOXES FOR ISOCHRONE RESULTS -->
            <download
              :visible="downloadDialogState"
              :calculation="selectedCalculation"
              @close="downloadDialogState = false"
            ></download>
            <additional-layers
              :visible="additionalLayersDialogState"
              :calculation="selectedCalculation"
              @close="additionalLayersDialogState = false"
            ></additional-layers>
            <isochrone-color-picker
              :visible="isochroneColorPickerState"
              :calculation="activeCalculation"
              :selectedMode="activeCalculationMode"
              @close="isochroneColorPickerState = false"
            ></isochrone-color-picker>
          </v-layout>
        </v-flex>
      </template>
      <!-- -- -->
    </v-card>
    <confirm ref="confirm"></confirm>
  </v-flex>
</template>

<script>
import { Mapable } from "../../mixins/Mapable";
import { Isochrones } from "../../mixins/Isochrones";
import { KeyShortcuts } from "../../mixins/KeyShortcuts";

//Child components
import Download from "./IsochronesDownload";
import AdditionalLayers from "./IsochronesAdditionalLayers";
import IsochroneColorPicker from "./IsochroneColorPicker";

import {
  getIsochroneStyle,
  getIsochroneNetworkStyle,
  isochroneOverlayStyle
} from "../../style/OlStyleDefs";

//Store imports
import { mapGetters, mapMutations } from "vuex";
import { mapFields } from "vuex-map-fields";

//Ol imports
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import VectorImageLayer from "ol/layer/VectorImage";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import {
  wktToFeature,
  geojsonToFeature,
  getPolygonArea
} from "../../utils/MapUtils";
import IsochroneUtils from "../../utils/IsochroneUtils";
import { getDistance } from "ol/sphere";
import { toLonLat } from "ol/proj";
import { transform } from "ol/proj.js";
import { unByKey } from "ol/Observable";
//Other
import { EventBus } from "../../EventBus";
import ApiService from "../../services/api.service";

export default {
  mixins: [Mapable, Isochrones, KeyShortcuts],
  data: () => ({
    interactionType: "isochrone-interaction",
    isOptionsElVisible: true,
    isIsochroneOptionsVisible: true,
    speedRule: val => {
      if (val < 1) return "Please enter a number greater than 0";
      if (val >= 40) return "Please enter a number no greater than 40";
      return true;
    },
    timeRule: val => {
      if (val < 1) return "Please enter a number greater than 0";
      if (val >= 20) return "Please enter a number not greater than 20";
      return true;
    },
    isIsochroneCalculationTypeElVisible: true,
    isIsochroneStartElVisible: true,
    isResultsElVisible: true,
    mapClickListener: null,
    downloadDialogState: false,
    additionalLayersDialogState: false,
    selectedCalculation: null,
    isochroneColorPickerState: false,
    activeCalculation: null, // for color palette selection
    activeCalculationMode: null, // for color palette selection,
    isThematicDataVisible: false
  }),
  components: {
    download: Download,
    additionalLayers: AdditionalLayers,
    IsochroneColorPicker
  },
  computed: {
    ...mapGetters("isochrones", {
      calculations: "calculations"
    }),
    ...mapGetters("map", {
      contextmenu: "contextmenu"
    }),
    ...mapGetters("app", {
      appColor: "appColor",
      appConfig: "appConfig",
      routingProfiles: "routingProfiles",
      calculationMode: "calculationMode"
    }),
    ...mapFields("isochrones", {
      type: "type",
      time: "time",
      speed: "speed",
      steps: "steps",
      routing: "routing",
      calculations: "calculations",
      isochroneLayer: "isochroneLayer",
      isochroneOverlayLayer: "isochroneOverlayLayer",
      isochroneRoadNetworkLayer: "isochroneRoadNetworkLayer",
      colors: "colors",
      defaultIsochroneColor: "defaultIsochroneColor",
      scenarioIsochroneColor: "scenarioIsochroneColor"
    }),
    ...mapFields("map", {
      isMapBusy: "isBusy"
    }),
    headers() {
      return [
        {
          text: this.$t("isochrones.results.table.type"),
          value: "type",
          sortable: false
        },
        {
          text: this.$t("isochrones.results.table.range"),
          value: "range",
          sortable: false
        },
        {
          text: this.$t("isochrones.results.table.area"),
          value: "area",
          sortable: false
        },
        {
          text: this.$t("isochrones.results.table.visible"),
          value: "visible",
          sortable: false
        },
        {
          text: this.$t("isochrones.results.table.legend"),
          value: "legend",
          sortable: false
        }
      ];
    }
  },
  methods: {
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR",
      startHelpTooltip: "START_HELP_TOOLTIP",
      stopHelpTooltip: "STOP_HELP_TOOLTIP"
    }),
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      this.createIsochroneLayer();
      this.createIsochroneRoadNetworkLayer();
      this.createIsochroneOverlayLayer();
      this.setUpCtxMenu();
    },
    /**
     * Creates a vector layer for the isochrone calculations results and adds it to the
     * map and store.
     */
    createIsochroneLayer() {
      const style = getIsochroneStyle();
      const vector = new VectorLayer({
        name: "isochrone_layer",
        displayInLegend: false,
        zIndex: 6,
        source: new VectorSource(),
        style: style
      });
      this.map.addLayer(vector);
      this.isochroneLayer = vector;
    },
    /**
     * Creates a vector layer for the isochrone calculations results and adds it to the
     * map and store.
     */
    createIsochroneRoadNetworkLayer() {
      const style = getIsochroneNetworkStyle();
      const vector = new VectorImageLayer({
        name: "isochrone_road_network_layer",
        displayInLegend: false,
        zIndex: 5,
        source: new VectorSource(),
        style: style
      });
      this.map.addLayer(vector);
      this.isochroneRoadNetworkLayer = vector;
    },
    /**
     * Creates a vector layer for the isochrone calculations results and adds it to the
     * map and store.
     */
    createIsochroneOverlayLayer() {
      const vector = new VectorImageLayer({
        name: "isochrone_overlayer",
        displayInLegend: false,
        zIndex: 7,
        source: new VectorSource(),
        style: isochroneOverlayStyle
      });
      this.map.addLayer(vector);
      this.isochroneOverlayLayer = vector;
    },
    /**
     * Register map click listener to calculate single isochrone.
     */
    registerMapClick() {
      //Close other interactions.
      EventBus.$emit("ol-interaction-activated", this.interactionType);
      this.mapClickListener = this.map.once("singleclick", this.onMapClick);
      this.startHelpTooltip(
        this.$t("map.tooltips.clickForIsochroneCalculation")
      );
      this.map.getTarget().style.cursor = "pointer";
      if (this.addKeyupListener) {
        this.addKeyupListener();
      }
    },
    /**
     * Handler for 'singleclick' on the map.
     * Collects data and passes it to corresponding objects.
     * @param  {ol/MapBrowserEvent} evt The OL event of 'singleclick' on the map
     */
    onMapClick(evt) {
      const projection = this.map
        .getView()
        .getProjection()
        .getCode();
      const coordinateWgs84 = transform(
        evt.coordinate,
        projection,
        "EPSG:4326"
      );
      const payloadSingle = {
        x: coordinateWgs84[0],
        y: coordinateWgs84[1]
      };
      const calculationNumber = this.calculations.length + 1;
      const isochroneMarkerFeature = new Feature({
        geometry: new Point(evt.coordinate),
        calculationNumber: calculationNumber
      });
      isochroneMarkerFeature.setId("isochrone_marker_" + calculationNumber);
      this.isochroneLayer.getSource().addFeature(isochroneMarkerFeature);
      this.calculateIsochrone(payloadSingle)
        .then(() => {})
        .catch(error => {
          console.log(error);
          this.toggleSnackbar({
            type: "error", //success or error
            message: "calculateIsochroneError",
            state: true,
            timeout: 2500
          });
        });
      this.clear();
    },
    /**
     * Calculate isochrone .
     * Collects data and passes it to corresponding objects.
     * @param  {Object} parameters The parameters for the isochrone calculation
     */
    calculateIsochrone(params) {
      const type = this.type;
      const time = this.time;
      const speed = this.speed;
      const routing = this.routing;
      const steps = this.steps;
      const modus = this.calculationMode.active;
      const scenario_id = this.scenarioId || 0; //TODO: Get scenario id from store
      const active_upload_ids = this.activeUploadIds || [0]; //TODO: Get active upload ids from store
      const baseParams = {
        minutes: time,
        speed,
        modus,
        n: steps,
        routing_profile: routing,
        scenario_id,
        active_upload_ids
      };
      const payload = { ...baseParams, ...params };
      this.isMapBusy = true;
      return new Promise((resolve, reject) => {
        ApiService.post(`/isochrones/${type}`, payload)
          .then(response => {
            this.isMapBusy = false;
            resolve(response);
            if (response.data) {
              const calculationData = [];
              const calculationNumber = this.calculations.length + 1;
              //Order features based on id
              let olFeatures = geojsonToFeature(response.data, {
                dataProjection: "EPSG:4326",
                featureProjection: "EPSG:3857"
              });
              olFeatures.sort((a, b) => {
                return a.get("step") - b.get("step");
              });
              olFeatures.forEach(feature => {
                let color = "";
                let level = feature.get("step");
                let modus = feature.get("modus");
                if (modus === "default" || modus === "comparision") {
                  color = IsochroneUtils.getInterpolatedColor(
                    1,
                    20,
                    parseInt(level / 60),
                    this.colors[this.defaultIsochroneColor]
                  );
                } else {
                  color = IsochroneUtils.getInterpolatedColor(
                    1,
                    20,
                    parseInt(level / 60),
                    this.colors[this.scenarioIsochroneColor]
                  );
                }
                let obj = {
                  id: feature.getId(),
                  type: this.$t(
                    `isochrones.mode.${feature.get("modus").toLowerCase()}`
                  ),
                  isochrone_calculation_id: feature.get(
                    "isochrone_calculation_id"
                  ),
                  modus: modus,
                  range: feature.get("step") + " min",
                  color: color,
                  area: getPolygonArea(feature.getGeometry()),
                  isVisible: true
                };
                feature.set("isVisible", true);
                feature.set("calculationNumber", calculationNumber);
                feature.set("color", color);
                feature.set("calculationType", type);
                feature.set("hoverColor", "");
                calculationData.push(obj);
              });
              let transformedData = {
                id: calculationNumber,
                calculationType: type.toLowerCase(),
                calculationMode: baseParams.modus.replace(/'/g, ""), // remove extra apostrophe in multi-isochrone
                time: baseParams.minutes + " min",
                speed: baseParams.speed + " km/h",
                routing_profile: routing,
                scenario_id,
                isExpanded: true,
                isVisible: true,
                data: calculationData,
                additionalData: {}
              };
              // Add default calculation color palette.
              if (transformedData.calculationMode === "default") {
                transformedData[
                  `defaultColorPalette`
                ] = this.defaultIsochroneColor;
              } else if (transformedData.calculationMode === "scenario") {
                transformedData[
                  `scenarioColorPalette`
                ] = this.scenarioIsochroneColor;
              } else if (transformedData.calculationMode === "comparison") {
                transformedData[
                  `defaultColorPalette`
                ] = this.defaultIsochroneColor;
                transformedData[
                  `scenarioColorPalette`
                ] = this.scenarioIsochroneColor;
              }
              if (type === "single") {
                //TODO: Get start point from response
                const startPointCoord = this.isochroneLayer
                  .getSource()
                  .getFeatureById("isochrone_marker_" + calculationNumber)
                  .getGeometry()
                  .getCoordinates();
                const wgs84Coord = toLonLat(startPointCoord);
                //Geocode
                ApiService.get(
                  `${process.env.VUE_APP_SEARCH_URL}`,
                  `reverse.php?key=${process.env.VUE_APP_SEARCH_KEY}&lat=${wgs84Coord[1]}&lon=${wgs84Coord[0]}&format=json`
                )
                  .then(response => {
                    if (response.status === 200 && response.data.display_name) {
                      const address = response.data.display_name;
                      transformedData.position = address;
                    }
                  })
                  .catch(() => {
                    transformedData.position = "Unknown";
                  });
              }
              // Add calculation to store.
              this.calculations.forEach(calculation => {
                calculation.isExpanded = false;
              });
              this.calculations.unshift(transformedData);
              // Add feature to layer.
              this.isochroneLayer.getSource().addFeatures(olFeatures);
            }
          })
          .catch(({ response }) => {
            this.isMapBusy = false;
            reject(response);
          });
      });
    },
    //TODO: Active calculation is the one that has thematic data window open.
    isCalculationActive(calculation) {
      console.log(calculation);
      return false;
    },
    /**
     * Configure right-click for isochrone.
     */
    setUpCtxMenu() {
      if (this.contextmenu) {
        this.contextmenu.on("beforeopen", evt => {
          const features = this.map.getFeaturesAtPixel(evt.pixel, {
            layerFilter: candidate => {
              if (candidate.get("name") === "isochrone_layer") {
                return true;
              }
              return false;
            }
          });
          let closestFeature;
          let closestDistance;
          const clickedCoord = toLonLat(evt.coordinate);

          features.forEach(f => {
            if (f.get("calculationType") === "single") {
              let startingPoint = wktToFeature(f.get("starting_point"));
              const distance = getDistance(
                clickedCoord,
                startingPoint.getGeometry().getCoordinates()
              );
              if (!closestDistance || closestDistance > distance) {
                closestDistance = distance;
                closestFeature = f;
              }
            }
          });

          if (!closestFeature) {
            closestFeature = features[0];
          }
          if (features.length > 0) {
            this.contextmenu.extend([
              "-", // this is a separator
              {
                text: `<i class="fa fa-trash fa-1x" aria-hidden="true"></i>&nbsp;&nbsp${this.$t(
                  "map.contextMenu.deleteIsochrone"
                )}`,
                label: "deleteIsochrone",
                callback: () => {
                  const calculation = this.calculations.filter(
                    calculation =>
                      calculation.id === closestFeature.get("calculationNumber")
                  );
                  if (calculation[0]) {
                    this.deleteCalculation(calculation[0]);
                  }
                }
              }, // this is a separator
              {
                text: `<i class="fas fa-redo fa-1x" aria-hidden="true"></i>&nbsp;&nbsp${this.$t(
                  "map.contextMenu.redoCalculation"
                )}`,
                label: "redoCalculation",
                callback: () => {
                  const calculation = this.calculations.filter(
                    calculation =>
                      calculation.id === closestFeature.get("calculationNumber")
                  );
                  if (calculation[0]) {
                    this.removeCalculation(calculation[0]);
                    if (calculation[0].calculationType === "single") {
                      this.updatePosition({
                        coordinate: wktToFeature(
                          closestFeature.get("starting_point")
                        )
                          .getGeometry()
                          .getCoordinates(),
                        placeName: ""
                      });
                    }
                    this.calculateIsochrone(calculation[0]);
                  }
                }
              }
            ]);
          }
        });
      }
    },
    // ------------RESULTS----------
    deleteAll() {
      this.$refs.confirm
        .open(
          this.$t("isochrones.deleteTitle"),
          this.$t("isochrones.deleteAllMessage"),
          { color: this.appColor.primary }
        )
        .then(confirm => {
          if (confirm) {
            this.calculations.forEach(calculation => {
              this.removeCalculation(calculation);
            });
          }
        });
    },
    removeCalculation(calculation) {
      let id = calculation.id;
      if (
        this.selectedThematicData &&
        this.selectedThematicData.calculationId === id
      ) {
        this.selectedThematicData = null;
      } else if (this.selectedThematicData) {
        this.selectedThematicData.calculationId =
          this.selectedThematicData.calculationId - 1;
      }

      this.calculations = this.calculations.filter(
        calculation => calculation.id != id
      );
      this.calculations = this.calculations.map(calculation => {
        if (calculation.id > id) {
          calculation.id = calculation.id - 1;
        }
        return calculation;
      });
      const isochroneSource = this.isochroneLayer.getSource();
      isochroneSource.getFeatures().forEach(isochroneFeature => {
        const isochroneCalculationNr = isochroneFeature.get(
          "calculationNumber"
        );
        if (isochroneCalculationNr === id) {
          isochroneSource.removeFeature(isochroneFeature);
        }
        if (isochroneCalculationNr > id) {
          const updatedNr = isochroneCalculationNr - 1;
          isochroneFeature.set("calculationNumber", updatedNr);
          isochroneFeature.setId("isochrone_marker_" + updatedNr);
        }
      });
      const isochroneRoadNetworkLayerSource = this.isochroneRoadNetworkLayer.getSource();
      Object.keys(calculation.additionalData).forEach(type => {
        const features = calculation.additionalData[type].features;
        if (isochroneRoadNetworkLayerSource && features) {
          features.forEach(feature => {
            isochroneRoadNetworkLayerSource.removeFeature(feature);
          });
        }
      });
      // Remove and update isochrone overlay features
      const isochroneOverlayerLayerSource = this.isochroneOverlayLayer.getSource();
      isochroneOverlayerLayerSource.getFeatures().forEach(feature => {
        if (feature.get("calculationNumber") === id) {
          isochroneOverlayerLayerSource.removeFeature(feature);
        } else {
          if (feature.get("calculationNumber") > id) {
            feature.set("calculationNumber", id - 1);
          }
        }
      });
      this.isochroneOverlayLayer.changed();
    },
    toggleThematicDataVisibility(isVisible) {
      this.isThematicDataVisible = isVisible;
    },
    toggleIsochroneWindow(calculation) {
      if (this.isCalculationActive(calculation)) {
        // Hide
        this.isochroneLayer
          .getSource()
          .getFeatures()
          .forEach(f => {
            f.set("highlightFeature", false);
          });
        this.toggleThematicDataVisibility(false);
      } else {
        // Show
        this.showIsochroneWindow({
          id: calculation.id,
          calculationType: calculation.calculationType
        });
      }
    },
    toggleIsochroneVisibility(feature, calculation) {
      //Get all visible calculation
      const visibleFeatures = calculation.data.filter(
        feature => feature.isVisible === true
      );

      let isNetworkVisible = false;
      Object.keys(calculation.additionalData).forEach(key => {
        if (calculation.additionalData[key].state === true) {
          isNetworkVisible = true;
        }
      });

      //If user has turned off other features, hide the result
      if (
        !isNetworkVisible &&
        visibleFeatures.length === 1 &&
        visibleFeatures[0].id === feature.id &&
        visibleFeatures[0].isVisible === true
      ) {
        this.showHideCalculation(calculation);
      } else {
        this.toggleIsochroneFeatureVisibility(feature);
      }

      if (calculation.isVisible === false && feature.isVisible === true) {
        calculation.isVisible = true;
      }
    },
    toggleIsochroneFeatureVisibility(feature) {
      let featureId = feature.id;
      feature.isVisible = !feature.isVisible;
      if (featureId) {
        let isochroneFeature = this.isochroneLayer
          .getSource()
          .getFeatureById(featureId);
        if (isochroneFeature) {
          isochroneFeature.set("isVisible", feature.isVisible);
        }
      }
    },
    toggleDownloadDialog(calculation) {
      this.downloadDialogState = true;
      this.selectedCalculation = calculation;
    },
    showHideCalculation(calculation) {
      this.showHideNetworkData(calculation);
      this.showHideIsochroneOverlayFeatures(calculation);
      this.toggleIsochroneCalculationVisibility(calculation);
    },
    showHideNetworkData(calculation) {
      //Check if road netowrk is visible. Is so remove all features from map.
      const roadNetworkData = calculation.additionalData;
      for (let type in roadNetworkData) {
        // type can be 'Deafult' or 'Input'
        const state = roadNetworkData[type].state;
        const roadNetworkSource = this.isochroneRoadNetworkLayer.getSource();
        const features = roadNetworkData[type].features;
        if (state === true && calculation.isVisible === true) {
          features.forEach(feature => {
            if (roadNetworkSource.hasFeature(feature)) {
              roadNetworkSource.removeFeature(feature);
            }
          });
        } else if (state === true && calculation.isVisible === false) {
          features.forEach(feature => {
            roadNetworkSource.addFeature(feature);
          });
        }
      }
    },
    showHideIsochroneOverlayFeatures(calculation) {
      const id = calculation.id;
      const isVisible = !calculation.isVisible;
      this.isochroneOverlayLayer
        .getSource()
        .getFeatures()
        .forEach(feature => {
          if (feature.get("calculationNumber") === id) {
            feature.set("isVisible", isVisible);
          }
        });
    },
    showAdditionalLayerDialog(calculation) {
      this.additionalLayersDialogState = true;
      this.selectedCalculation = calculation;
    },
    getPaletteColor(calculation, mode) {
      const colorKey = `${mode}ColorPalette`;
      return Object.values(this.colors[calculation[colorKey]]).toString();
    },
    toggleColorPickerDialog(calculation, mode) {
      this.isochroneColorPickerState = true;
      this.activeCalculation = calculation;
      this.activeCalculationMode = mode;
    },
    // ------------CLEAR----------
    /**
     * Clears the map and ol interaction activity
     */
    clear() {
      if (this.mapClickListener) {
        unByKey(this.mapClickListener);
        this.mapClickListener = null;
      }
      this.stopHelpTooltip();
      this.map.getTarget().style.cursor = "";
      EventBus.$emit("ol-interaction-stoped", this.interactionType);
    }
  },
  watch: {
    routing() {
      this.speed = this.appConfig.routing[this.routing].speed;
    }
  },
  created() {
    // Set default routing
    const defaultRouting = this.appConfig.routing[0];
    this.routing = defaultRouting.type;
    this.speed = defaultRouting.speed;
  }
};
</script>
<style lang="css">
.result-icons {
  color: "#4A4A4A";
  cursor: pointer;
}
.result-icons:hover {
  color: #30c2ff;
}
.delete-icon:hover {
  color: #ff6060;
}
.isochrone-nr {
  position: absolute;
}
.v-data-table td,
.v-data-table th {
  padding: 0 5px;
}
.v-data-table th {
  font-size: 14px;
}
.v-data-table td {
  font-size: 13px;
}
.legend {
  height: 24px;
  border-radius: 7px;
}

.colorPalettePicker {
  height: 24px;
  border-radius: 7px;
  width: 50px;
  cursor: pointer;
}

.activeIcon {
  color: #30c2ff;
}
.v-input--selection-controls {
  margin-top: 0px;
  padding-top: 0px;
}

.subheader {
  height: 25px;
}

.v-chip--label {
  border-radius: 0px 8px 8px 0px !important;
}

.result-title {
  display: inline-block;
  width: 265px;

  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chip-label-custom {
  display: block;
  width: 66px;
  word-wrap: break-word;
  overflow-wrap: break-word;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
