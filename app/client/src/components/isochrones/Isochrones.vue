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
            class="py-0 my-0 mb-2 justify-center"
          >
            <v-row no-gutters justify="center" align="center">
              <v-radio-group
                class="ml-2 mt-4 radio-group-height"
                v-model="type"
                :value="type"
                @change="stop"
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
            </v-row>
            <v-row no-gutters>
              <template v-if="type === 'single'">
                <v-col cols="12" justify="center" align="center" class="pr-2">
                  <template v-if="!isIsochroneBusy">
                    <span>
                      <v-tooltip top>
                        <template v-slot:activator="{ on }">
                          <v-btn
                            outlined
                            fab
                            v-on="on"
                            class="mr-2"
                            depressed
                            text
                            @click="registerMapClick('isochrone')"
                          >
                            <v-icon
                              :color="
                                mapClickListener ? appColor.secondary : 'grey'
                              "
                              >fas fa-map-marker-alt</v-icon
                            >
                          </v-btn>
                        </template>
                        <span>{{ $t("isochrones.single.startTooltip") }}</span>
                      </v-tooltip>
                    </span>
                    <br />
                    <span>Isochrone Single</span>
                  </template>
                  <span v-if="isIsochroneBusy">
                    <v-tooltip top>
                      <template v-slot:activator="{ on }">
                        <v-btn
                          fab
                          dark
                          v-on="on"
                          class="mb-4 elevation-0"
                          color="red"
                          @click="stopIsochroneCalculation"
                        >
                          <v-icon color="white">close</v-icon>
                        </v-btn>
                      </template>
                      <span>{{ $t("isochrones.stopIsochroneCalc") }}</span>
                    </v-tooltip>
                  </span>
                </v-col>
              </template>
              <template v-if="type === 'multiple'">
                <v-row no-gutters>
                  <v-col cols="6" justify="center" align="center" class="pl-10">
                    <span
                      v-if="!isIsochroneBusy || multiIsochroneMethod === 'draw'"
                    >
                      <v-tooltip top>
                        <template v-slot:activator="{ on }">
                          <v-btn
                            outlined
                            fab
                            v-on="on"
                            class="ml-2"
                            depressed
                            text
                            @click="activateMultiIsochrone('study_area')"
                          >
                            <v-icon
                              :color="
                                multiIsochroneMethod === 'study_area'
                                  ? appColor.secondary
                                  : 'grey'
                              "
                              >fa-solid fa-hand-pointer</v-icon
                            >
                          </v-btn>
                        </template>
                        <span>{{ $t("isochrones.multiple.studyArea") }}</span>
                      </v-tooltip>
                    </span>
                    <span
                      v-if="
                        isIsochroneBusy && multiIsochroneMethod === 'study_area'
                      "
                    >
                      <v-tooltip top>
                        <template v-slot:activator="{ on }">
                          <v-btn
                            fab
                            dark
                            v-on="on"
                            class="mb-4 elevation-0"
                            color="red"
                            @click="stopIsochroneCalculation"
                          >
                            <v-icon color="white">close</v-icon>
                          </v-btn>
                        </template>
                        <span>{{ $t("isochrones.stopIsochroneCalc") }}</span>
                      </v-tooltip>
                    </span>
                    <br />
                    <span>{{ $t("isochrones.multiple.studyArea") }}</span>
                  </v-col>
                  <v-col cols="6" justify="center" align="center" class="pr-10">
                    <span
                      v-if="
                        !isIsochroneBusy ||
                          multiIsochroneMethod === 'study_area'
                      "
                    >
                      <v-tooltip top>
                        <template v-slot:activator="{ on }">
                          <v-btn
                            outlined
                            fab
                            v-on="on"
                            class="ml-2 mr-4"
                            depressed
                            text
                            @click="activateMultiIsochrone('draw')"
                          >
                            <v-icon
                              :color="
                                multiIsochroneMethod === 'draw'
                                  ? appColor.secondary
                                  : 'grey'
                              "
                              >fa-solid fa-draw-polygon</v-icon
                            >
                          </v-btn>
                        </template>
                        <span>{{ $t("isochrones.multiple.drawPolygon") }}</span>
                      </v-tooltip>
                    </span>
                    <span
                      v-if="isIsochroneBusy && multiIsochroneMethod === 'draw'"
                    >
                      <v-tooltip top>
                        <template v-slot:activator="{ on }">
                          <v-btn
                            fab
                            dark
                            v-on="on"
                            class="mb-4 elevation-0"
                            color="red"
                            @click="stopIsochroneCalculation"
                          >
                            <v-icon color="white">close</v-icon>
                          </v-btn>
                        </template>
                        <span>{{ $t("isochrones.stopIsochroneCalc") }}</span>
                      </v-tooltip>
                    </span>
                    <br />
                    <span>{{ $t("isochrones.multiple.drawPolygon") }}</span>
                  </v-col>
                </v-row>
                <v-row no-gutters justify="center" class="mt-2" align="center">
                  <v-btn
                    small
                    class="white--text mr-2 mt-5 mb-2"
                    color="error"
                    outlined
                    @click="stop"
                  >
                    {{ $t("isochrones.multiple.clear") }}
                  </v-btn>
                  <v-btn
                    :disabled="
                      !multiIsochronePoiCount ||
                        multiIsochronePoiCount > maxAmenities ||
                        isMapBusy
                    "
                    small
                    class="white--text ml-2 mt-5 mb-2"
                    :color="appColor.primary"
                    @click="calculateMultiIsochrone"
                  >
                    {{ $t("isochrones.multiple.calculate") }}
                  </v-btn>
                </v-row>
              </template>
            </v-row>
            <v-progress-linear
              v-if="isIsochroneBusy"
              indeterminate
              height="1"
              class="mx-0 pb-0"
              :color="appColor.primary"
            ></v-progress-linear>
          </v-card-text>
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

            <v-hover v-slot="{ hover }">
              <v-btn
                small
                v-show="isResultsElVisible === true && calculations.length > 1"
                class="white--text mr-2"
                :color="hover ? 'error' : 'grey'"
                outlined
                @click.stop="deleteAll"
              >
                <v-icon left>delete</v-icon
                >{{ $t("isochrones.results.deleteAll") }}
              </v-btn>
            </v-hover>

            <v-icon
              v-html="isResultsElVisible === true ? 'remove' : 'add'"
            ></v-icon>
          </v-subheader>
          <v-layout>
            <v-flex xs12 class="mx-3" v-show="isResultsElVisible">
              <template v-for="calculation in calculations">
                <v-card
                  style="width: 330px;"
                  class="mb-3 "
                  :id="`result-${calculation.id}`"
                  :key="calculation.id"
                  :class="{
                    'elevation-5': isCalculationActive(calculation)
                  }"
                >
                  <v-card-title
                    style="background-color:#EEEEEE;"
                    class="pb-0 mt-0 pt-0 mb-0"
                  >
                    <v-layout row wrap class="py-1">
                      <v-layout align-start justify-start>
                        <v-card-text class="pa-0 ma-0 ml-2">
                          <v-icon small class="text-xs-center">{{
                            routingProfiles[calculation.routing_profile].icon
                          }}</v-icon>
                          <span class="ml-1 caption">
                            {{
                              $t(
                                `isochrones.options.${calculation.routing_profile}`
                              )
                            }}
                          </span>

                          <v-icon small class="text-xs-center mx-2"
                            >fas fa-tachometer-alt
                          </v-icon>
                          <span class="caption">{{ calculation.speed }}</span>
                          <span
                            class="pl-2 ml-2 text-xs-center"
                            style="border-left: 1px solid #424242;"
                            >{{
                              $te(
                                `isochrones.options.${calculation.calculationMode}`
                              )
                                ? $t(
                                    `isochrones.options.${calculation.calculationMode}`
                                  )
                                : calculation.calculationMode
                            }}</span
                          >
                        </v-card-text>
                      </v-layout>

                      <v-layout row>
                        <v-spacer></v-spacer>
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
                      <v-layout class="ml-0" row> </v-layout>
                    </v-card-text>
                  </v-card-title>
                  <v-subheader
                    justify-center
                    align-center
                    class="clickable subheader mt-1 pb-1"
                    @click="calculation.isExpanded = !calculation.isExpanded"
                  >
                    <span class="fa-stack fa-xs mr-1" style="color:#800000;">
                      <span
                        class="fa fa-solid fa-location-pin fa-stack-2x"
                      ></span>
                      <strong
                        style="font-size:12px;"
                        class="white--text fa-stack-1x mb-1"
                      >
                        {{ calculation.id }}
                      </strong>
                    </span>
                    <v-tooltip
                      :disabled="
                        calculation.position === 'multiIsochroneCalculation'
                      "
                      open-delay="600"
                      max-width="300"
                      top
                    >
                      <template v-slot:activator="{ on }">
                        <p class="result-title subtitle-2 mt-4" v-on="on">
                          {{
                            calculation.position === "multiIsochroneCalculation"
                              ? $t("isochrones.results.multiIsochroneHeader")
                              : calculation.position
                          }}
                        </p>
                      </template>
                      <span>{{ calculation.position }}</span></v-tooltip
                    >
                    <v-tooltip top>
                      <template v-slot:activator="{ on }">
                        <div
                          v-if="
                            calculation.calculationMode === 'scenario' ||
                              calculation.calculationMode === 'comparison'
                          "
                          v-on="on"
                          @click.stop="
                            toggleColorPickerDialog(calculation, 'scenario')
                          "
                          class="my-1 ml-1 mx-2 colorPalettePicker"
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
                          @click.stop="
                            toggleColorPickerDialog(calculation, 'default')
                          "
                          v-on="on"
                          class="my-1 mx-2 colorPalettePicker"
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
                    <v-icon
                      small
                      class="ml-2"
                      v-html="
                        calculation.isExpanded
                          ? 'fas fa-chevron-down'
                          : 'fas fa-chevron-up'
                      "
                    ></v-icon>
                  </v-subheader>
                  <v-divider
                    v-if="calculation.isExpanded"
                    style="border-width:revert;"
                  ></v-divider>

                  <v-card-text
                    class="pt-0 pb-0"
                    v-show="calculation.isExpanded"
                  >
                    <v-row justify-center align-center no-gutters>
                      <v-tooltip top>
                        <template v-slot:activator="{ on }">
                          <v-btn
                            :color="appColor.primary"
                            fab
                            dark
                            class="my-1 mt-3 elevation-1"
                            v-on="on"
                            x-small
                            @click="toggleDownloadDialog(calculation)"
                          >
                            <v-icon small>fa-solid fa-download</v-icon>
                          </v-btn>
                        </template>
                        <span>{{
                          $t("isochrones.results.downloadTooltip")
                        }}</span>
                      </v-tooltip>
                      <v-spacer></v-spacer>
                      <v-switch
                        class="mt-4 mr-3"
                        dense
                        :color="appColor.secondary"
                        hide-details
                      >
                        <template v-slot:label>
                          <span class="caption">{{
                            $t("isochrones.results.roadNetwork")
                          }}</span>
                        </template>
                      </v-switch>
                      <v-switch
                        class="mt-4"
                        :value="isCalculationActive(calculation)"
                        dense
                        :color="appColor.secondary"
                        hide-details
                        @change="toggleIsochroneWindow(calculation)"
                      >
                        <template v-slot:label>
                          <span class="caption">{{
                            $t("isochrones.results.dataTable")
                          }}</span>
                        </template>
                      </v-switch>
                    </v-row>

                    <v-data-table
                      dense
                      :headers="headers"
                      :items="calculation.data"
                      class="elevation-0 subtitle-1 pb-3"
                      hide-default-footer
                      hide-default-header
                      light
                    >
                      <template v-slot:header="{ props: { headers } }">
                        <thead>
                          <tr>
                            <th :key="h.value" v-for="h in headers">
                              <v-checkbox
                                v-if="h.value === 'visible'"
                                @change="showHideCalculation(calculation)"
                                :input-value="
                                  getToggleCalculationCheckboxState(calculation)
                                "
                                :indeterminate="
                                  getToggleCalculationCheckboxIndeterminateState(
                                    calculation
                                  )
                                "
                                :color="appColor.secondary"
                                hide-details
                                dense
                              >
                              </v-checkbox>
                              <span v-else>{{ h.text }}</span>
                            </th>
                          </tr>
                        </thead>
                      </template>
                      <template v-slot:item.visible="{ item }">
                        <v-checkbox
                          class="my-2"
                          dense
                          :input-value="item.isVisible"
                          :color="appColor.secondary"
                          hide-details
                          @change="toggleIsochroneVisibility(item, calculation)"
                        ></v-checkbox>
                      </template>
                      <template v-slot:items="props">
                        <td>{{ props.item.range }}</td>
                        <td>{{ props.item.area }}</td>
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
  isochroneOverlayStyle,
  studyAreaASelectStyle
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
  getPolygonArea,
  geometryToWKT
} from "../../utils/MapUtils";
import DrawInteraction from "ol/interaction/Draw";
import IsochroneUtils from "../../utils/IsochroneUtils";
import { getDistance } from "ol/sphere";
import { toLonLat } from "ol/proj";
import { transform } from "ol/proj.js";
import { unByKey } from "ol/Observable";
//Other
import { EventBus } from "../../EventBus";
import ApiService from "../../services/api.service";
import axios from "axios";

export default {
  mixins: [Mapable, Isochrones, KeyShortcuts],
  data: () => ({
    interactionType: "isochrone-interaction",
    isOptionsElVisible: true,
    isIsochroneOptionsVisible: true,
    speedRule: val => {
      if (val < 1) return "Please enter a number greater than 0";
      if (val > 40) return "Please enter a number no greater than 40";
      return true;
    },
    timeRule: val => {
      if (val < 1) return "Please enter a number greater than 0";
      if (val > 20) return "Please enter a number not greater than 20";
      return true;
    },
    isIsochroneBusy: false,
    isIsochroneCalculationTypeElVisible: true,
    isIsochroneStartElVisible: true,
    isResultsElVisible: true,
    downloadDialogState: false,
    additionalLayersDialogState: false,
    selectedCalculation: null,
    isochroneColorPickerState: false,
    activeCalculation: null, // for color palette selection
    activeCalculationMode: null, // for color palette selection,
    isThematicDataVisible: false,
    //Single Isochrone
    mapClickListener: null,
    // Multiisochrone
    multiIsochronePoiCount: null,
    drawPolygon: null,
    mapPointerMoveKey: null,
    maxAmenities: 150, //TODO: make this a configurable setting
    // Cancel Request Token
    cancelRequestToken: null
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
      contextmenu: "contextmenu",
      subStudyAreaLayer: "subStudyAreaLayer"
    }),
    ...mapGetters("app", {
      appColor: "appColor",
      appConfig: "appConfig",
      poisConfig: "poisConfig",
      routingProfiles: "routingProfiles",
      calculationMode: "calculationMode"
    }),
    ...mapGetters("poisaois", {
      poisAoisLayer: "poisAoisLayer",
      poisAois: "poisAois",
      selectedPois: "selectedPois",
      selectedPoisOnlyKeys: "selectedPoisOnlyKeys"
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
      multiIsochroneSelectionLayer: "multiIsochroneSelectionLayer",
      multiIsochroneMethod: "multiIsochroneMethod",
      colors: "colors",
      defaultIsochroneColor: "defaultIsochroneColor",
      scenarioIsochroneColor: "scenarioIsochroneColor"
    }),
    ...mapFields("map", {
      isMapBusy: "isMapBusy"
    }),
    headers() {
      return [
        {
          text: this.$t("isochrones.results.table.visible"),
          value: "visible",
          sortable: false
        },
        {
          text: this.$t("isochrones.results.table.range"),
          align: "center",
          value: "range",
          sortable: false
        },
        {
          text: this.$t("isochrones.results.table.area"),
          align: "center",
          value: "area",
          sortable: false
        },
        {
          text: this.$t("isochrones.results.table.population"),
          align: "center",
          value: "population",
          sortable: false
        },
        {
          text: this.$t("isochrones.results.table.legend"),
          value: "legend",
          sortable: false
        }
      ];
    },
    getMultiIsochroneInfoLabelText() {
      let text = "";
      if (
        this.multiIsochronePoiCount === 0 &&
        this.multiIsochroneMethod === "study_area"
      ) {
        text = this.$t("isochrones.multiple.studyAreaInfoLabel");
      } else if (
        this.multiIsochronePoiCount === 0 &&
        this.multiIsochroneMethod === "draw"
      ) {
        text = this.$t("isochrones.multiple.drawPolygonInfoLabel");
      } else {
        text = `${this.$t("isochrones.multiple.amenityCount")}: ${
          this.multiIsochronePoiCount
        } (${this.$t("isochrones.multiple.limit")}: 150)`;
      }
      return text;
    },
    isMultiIsochroneCalculationDisabled() {
      if (
        this.multiIsochronePoiCount > 0 &&
        this.multiIsochronePoiCount < 150
      ) {
        return false;
      } else {
        return true;
      }
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
      this.createIsochroneSelectionLayer();
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
     * Create multi isochrone selection layer
     */
    createIsochroneSelectionLayer() {
      const selectionSource = new VectorSource({
        wrapX: false
      });
      const selectionLayer = new VectorLayer({
        displayInLayerList: false,
        zIndex: 5,
        source: selectionSource,
        style: studyAreaASelectStyle()
      });
      this.map.addLayer(selectionLayer);
      this.multiIsochroneSelectionLayer = selectionLayer;
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
     * Activate multi isochrone method.
     */
    activateMultiIsochrone(type) {
      this.clear();
      this.multiIsochroneMethod = type;
      EventBus.$emit("ol-interaction-activated", this.interactionType);
      this.removeMultiIsochroneInteraction();
      this.map.getTarget().style.cursor = "pointer";
      if (this.addKeyupListener) {
        this.addKeyupListener();
      }

      if (this.multiIsochroneMethod === "study_area") {
        this.toggleSnackbar({
          type: this.appColor.primary,
          message: this.$t("isochrones.multiple.studyAreaInfoLabel"),
          state: true,
          timeout: 5000
        });
        //Study are method
        this.pointerMoveKey = this.map.on(
          "pointermove",
          this.onMultiIsochronePointerMove
        );
        if (!this.subStudyAreaLayer) {
          this.toggleSnackbar({
            type: "error",
            message: "Study area layer not available",
            state: true,
            timeout: 10000
          });
          this.stop();
          return;
        }

        this.subStudyAreaLayer.setVisible(true);
        this.registerMapClick();
        this.startHelpTooltip(this.$t("map.tooltips.clickToSelectStudyArea"));
      } else if (this.multiIsochroneMethod === "draw") {
        const drawPolygon = new DrawInteraction({
          type: "Polygon",
          source: this.multiIsochroneSelectionLayer.getSource()
        });
        drawPolygon.on("drawstart", this.onMultiIsochroneDrawStart);
        drawPolygon.on("drawend", this.onMultiIsochroneDrawEnd);
        this.map.addInteraction(drawPolygon);
        this.drawPolygon = drawPolygon;
        this.startHelpTooltip(
          this.$t("map.tooltips.clickToStartDrawingPolygon")
        );
        this.toggleSnackbar({
          type: this.appColor.primary,
          message: this.$t("isochrones.multiple.drawPolygonInfoLabel"),
          state: true,
          timeout: 10000
        });
      }
    },
    /**
     * Draw interaction start event handler
     */
    onMultiIsochroneDrawStart() {
      this.toggleSnackbar({ state: false });
      this.multiIsochronePoiCount = 0;
      this.multiIsochroneSelectionLayer.getSource().clear();
      this.startHelpTooltip(this.$t("map.tooltips.clickToContinueDrawing"));
    },

    /**
     * Draw interaction end event handler
     */
    onMultiIsochroneDrawEnd(evt) {
      const feature = evt.feature;
      let region = null;
      const geometry = feature
        .getGeometry()
        .clone()
        .transform("EPSG:3857", "EPSG:4326");
      region = geometryToWKT(geometry);
      if (this.selectedPois.length === 0) {
        this.toggleSnackbar({
          type: "error",
          message: this.$t("map.snackbarMessages.selectAmenities"),
          state: true,
          timeout: 10000
        });
        return;
      }
      this.countPois(region);
      this.toggleSnackbar({
        type:
          this.multiIsochronePoiCount > this.maxAmenities
            ? "error"
            : this.appColor.primary,
        message:
          this.$t("isochrones.multiple.amenityCount") +
          ` ${this.multiIsochronePoiCount} / ${this.maxAmenities}`,
        state: true,
        timeout: 100000
      });
      this.startHelpTooltip(this.$t("map.tooltips.clickToStartDrawing"));
    },
    /**
     * Event for updating the edit help tooltip
     */
    onMultiIsochronePointerMove(evt) {
      const coordinate = evt.coordinate;
      if (
        this.multiIsochroneMethod === "study_area" &&
        this.multiIsochroneSelectionLayer
          .getSource()
          .getFeaturesAtCoordinate(coordinate).length > 0
      ) {
        this.startHelpTooltip(this.$t("map.tooltips.clickToRemove"));
      } else if (
        this.multiIsochroneMethod === "study_area" &&
        this.multiIsochroneSelectionLayer
          .getSource()
          .getFeaturesAtCoordinate(coordinate).length == 0
      ) {
        this.startHelpTooltip(this.$t("map.tooltips.clickToSelectStudyArea"));
      }
    },
    removeMultiIsochroneInteraction() {
      // cleanup possible old select interaction
      if (this.drawPolygon) {
        this.map.removeInteraction(this.drawPolygon);
      }
      if (this.mapClickListenerKey) {
        unByKey(this.mapClickListenerKey);
      }
      if (this.pointerMoveKey) {
        unByKey(this.pointerMoveKey);
      }
      this.multiIsochronePoiCount = 0;
    },
    /**
     * Count pois that intersect with study area or polygon
     */
    countPois(region) {
      ApiService.post(`/isochrones/multi/count-pois`, {
        region_type: this.multiIsochroneMethod,
        region,
        scenario_id: 0, //TODO: Get scenario id
        modus: this.calculationMode.active,
        routing_profilie: this.routing,
        minutes: this.time,
        speed: this.speed,
        amenities: this.selectedPoisOnlyKeys
      })
        .then(response => {
          if (response.data && Array.isArray(response.data.features)) {
            const feature = response.data.features[0];
            const countPois = feature.properties.count_pois;
            this.multiIsochronePoiCount += countPois;
            this.toggleSnackbar({
              type:
                this.multiIsochronePoiCount > this.maxAmenities
                  ? "error"
                  : this.appColor.primary,
              message:
                this.$t("isochrones.multiple.amenityCount") +
                ` ${this.multiIsochronePoiCount} (Limit: ${this.maxAmenities})`,
              state: true,
              timeout: 100000
            });
          }
        })
        .catch(error => {
          console.log(error);
        });
    },

    //=============================================================
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
      if (
        this.multiIsochroneMethod === "study_area" &&
        this.type === "multiple"
      ) {
        console.log("select study area");
        //Check if there is a feature already selected at clicked coordinate,
        //and if so, delete it and return.
        const featureAtCoord = this.multiIsochroneSelectionLayer
          .getSource()
          .getFeaturesAtCoordinate(evt.coordinate);
        if (featureAtCoord.length > 0) {
          this.multiIsochroneSelectionLayer
            .getSource()
            .removeFeature(featureAtCoord[0]);
          this.startHelpTooltip(this.$t("map.tooltips.clickToSelectStudyArea"));
          return;
        }
        const region = geometryToWKT(new Point(coordinateWgs84));
        console.log(region);
      } else {
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
            if (error && error.message === "cancelled") {
              return;
            }
            this.toggleSnackbar({
              type: "error", //success or error
              message: this.$t("map.snackbarMessages.calculateIsochroneError"),
              state: true,
              timeout: 2500
            });
          });
        this.clear();
      }
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
      this.isIsochroneBusy = true;
      const axiosInstance = axios.create();
      const CancelToken = axios.CancelToken;
      return new Promise((resolve, reject) => {
        let endpoint = "";
        if (type === "single") {
          endpoint = "single";
        } else if (type === "multiple") {
          endpoint = "multi/pois";
        }
        axiosInstance
          .post(`/isochrones/${endpoint}`, payload, {
            cancelToken: new CancelToken(c => {
              // An executor function receives a cancel function as a parameter
              this.cancelRequestToken = c;
            })
          })
          .then(response => {
            this.isMapBusy = false;
            this.isIsochroneBusy = false;
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
              olFeatures.forEach((feature, index) => {
                feature.setId(
                  "isochrone_feature_" + calculationNumber + "_" + index
                );
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
                  range: feature.get("step") / 60 + " min",
                  color: color,
                  area: getPolygonArea(feature.getGeometry()),
                  population: feature.get("reached_opportunities").sum_pop,
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

                delete axiosInstance.defaults.headers.common["Authorization"];
                axiosInstance
                  .get(
                    `${process.env.VUE_APP_SEARCH_URL}/reverse.php?key=${process.env.VUE_APP_SEARCH_KEY}&lat=${wgs84Coord[1]}&lon=${wgs84Coord[0]}&format=json`
                  )
                  .then(response => {
                    if (response.status === 200 && response.data.display_name) {
                      const address = response.data.display_name;
                      transformedData.position = address;
                    }
                  })
                  .catch(() => {
                    transformedData.position = "Unknown";
                  })
                  .finally(() => {
                    this.calculations.forEach(calculation => {
                      calculation.isExpanded = false;
                    });
                    this.calculations.unshift(transformedData);
                    this.isochroneLayer.getSource().addFeatures(olFeatures);
                    this.isOptionsElVisible = false;
                  });
              } else {
                transformedData.position = "Multi Isochrone Calculation";
                this.calculations.forEach(calculation => {
                  calculation.isExpanded = false;
                });
                this.calculations.unshift(transformedData);
                this.isochroneLayer.getSource().addFeatures(olFeatures);
                this.isOptionsElVisible = false;
              }
            }
          })
          .catch(error => {
            this.isMapBusy = false;
            this.isIsochroneBusy = false;
            reject(error);
          })
          .finally(() => {
            this.isMapBusy = false;
            this.isIsochroneBusy = false;
          });
      });
    },
    calculateMultiIsochrone() {
      const regionType = this.multiIsochroneMethod;
      const payload = {
        region_type: regionType
      };
      if (regionType === "study_area") {
        // Get selected study areas ids
      } else {
        // Get polygon geometry
        const feature = this.multiIsochroneSelectionLayer
          .getSource()
          .getFeatures()[0];
        if (!feature) return;
        const geometry = feature
          .getGeometry()
          .clone()
          .transform("EPSG:3857", "EPSG:4326");
        const region = geometryToWKT(geometry);
        payload.region = [region];
      }
      payload.amenities = this.selectedPoisOnlyKeys;
      this.calculateIsochrone(payload);
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
    toggleIsochroneCalculationVisibility(calculation) {
      calculation.isVisible = !calculation.isVisible;

      calculation.data.forEach(isochrone => {
        let featureId = isochrone.id;
        isochrone.isVisible = calculation.isVisible;
        let isochroneFeature = this.isochroneLayer
          .getSource()
          .getFeatureById(featureId);
        if (isochroneFeature) {
          isochroneFeature.set("isVisible", calculation.isVisible);
        }
      });
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
    getToggleCalculationCheckboxState(calculation) {
      const calculationData = calculation.data;
      const countVisibleFeatures = calculationData.filter(
        o => o.isVisible === true
      );
      if (countVisibleFeatures.length === 0) {
        return false;
      }
      return true;
    },
    getToggleCalculationCheckboxIndeterminateState(calculation) {
      const calculationData = calculation.data;
      const countVisibleFeatures = calculationData.filter(
        o => o.isVisible === true
      );
      if (countVisibleFeatures.length === 0) {
        return false;
      }
      if (countVisibleFeatures.length === calculationData.length) {
        return false;
      }
      return true;
    },
    // ------------CLEAR----------
    /**
     * Clears the map and ol interaction activity
     */
    stopIsochroneCalculation() {
      this.clear();
      if (this.cancelRequestToken instanceof Function) {
        this.cancelRequestToken("cancelled");
      }
      this.toggleSnackbar({
        type: "error",
        message: this.$t("map.snackbarMessages.calculationCancelled"),
        state: true,
        timeout: 4000
      });
    },
    clear() {
      if (this.mapClickListener) {
        unByKey(this.mapClickListener);
        this.mapClickListener = null;
      }
      this.toggleSnackbar({ state: false });
      this.removeMultiIsochroneInteraction();
      this.multiIsochroneMethod = null;
      this.multiIsochronePoiCount = 0;
      this.stopHelpTooltip();
      this.map.getTarget().style.cursor = "";
      EventBus.$emit("ol-interaction-stoped", this.interactionType);
      this.multiIsochroneSelectionLayer.getSource().clear();
    },
    stop() {
      if (this.cancelRequestToken instanceof Function) {
        this.cancelRequestToken("cancelled");
      }
      this.clear();
    }
  },
  watch: {
    routing() {
      this.speed = this.appConfig.routing[this.routing].speed;
    },
    selectedPois() {
      if (this.multiIsochroneMethod) {
        this.multiIsochronePoiCount = 0;
        console.log("selectedPois", this.selectedPois);
        this.multiIsochroneSelectionLayer
          .getSource()
          .getFeatures()
          .forEach(feature => {
            const geometry = feature
              .getGeometry()
              .clone()
              .transform("EPSG:3857", "EPSG:4326");
            const region = geometryToWKT(geometry);
            this.countPois(region);
          });
      }
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
  height: 20px;
  border-radius: 4px;
  width: 40px;
}

.colorPalettePicker {
  height: 20px;
  border-radius: 4px;
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
