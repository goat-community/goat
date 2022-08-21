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
            <v-icon
              small
              :style="
                isOptionsElVisible === true ? { color: appColor.secondary } : {}
              "
              class="mr-2"
              >fas fa-sliders-h</v-icon
            >
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
                      hide-details
                      v-model="routing"
                      :items="appConfig.routing"
                    >
                      <template slot="selection" slot-scope="{ item }">
                        <v-row>
                          <v-col cols="3" class="py-0"
                            ><v-icon dense>{{ item.icon }}</v-icon></v-col
                          >
                          <v-col cols="9" class="py-0"
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
                  <template v-if="!['transit', 'car'].includes(routing)">
                    <v-col class="d-flex mb-0 pb-2" cols="12" sm="6">
                      <v-text-field
                        :label="$t(`isochrones.options.speed`)"
                        type="number"
                        step="any"
                        min="1"
                        max="25"
                        ref="input"
                        :rules="[speedRule]"
                        v-model="speed"
                        suffix="km/h"
                        hide-details
                        class="mb-1"
                      ></v-text-field>
                    </v-col>
                  </template>
                  <template v-if="['transit', 'car'].includes(routing)">
                    <!-- DATE -->
                    <v-col class="d-flex mb-0 pb-0" cols="12" sm="6">
                      <v-menu
                        ref="pt_date"
                        v-model="dateMenu"
                        :close-on-content-click="false"
                        :nudge-right="40"
                        transition="scale-transition"
                        offset-y
                        min-width="auto"
                      >
                        <template v-slot:activator="{ on, attrs }">
                          <v-text-field
                            v-model="publicTransport.date"
                            label="Date"
                            class="mb-0 pb-0"
                            prepend-inner-icon="fas fa-calendar"
                            readonly
                            v-bind="attrs"
                            v-on="on"
                          ></v-text-field>
                        </template>
                        <v-date-picker
                          v-if="dateMenu"
                          :color="appColor.primary"
                          v-model="publicTransport.date"
                          @input="dateMenu = false"
                        ></v-date-picker>
                      </v-menu>
                    </v-col>
                    <!-- FROM TIME -->
                    <v-col class="d-flex mt-2 pt-0" cols="12" sm="6">
                      <v-menu
                        ref="pt_from_time"
                        v-model="fromTimeMenu"
                        :close-on-content-click="false"
                        :nudge-right="40"
                        transition="scale-transition"
                        offset-y
                        max-width="290px"
                        min-width="290px"
                      >
                        <template v-slot:activator="{ on, attrs }">
                          <v-text-field
                            v-model="publicTransport.fromTime"
                            label="From Time"
                            class="mb-0 pb-0"
                            prepend-inner-icon="fas fa-clock"
                            readonly
                            v-bind="attrs"
                            v-on="on"
                          ></v-text-field>
                        </template>
                        <v-time-picker
                          format="24hr"
                          v-if="fromTimeMenu"
                          full-width
                          :color="appColor.primary"
                          v-model="publicTransport.fromTime"
                          @click:minute="
                            $refs.pt_from_time.save(publicTransport.fromTime)
                          "
                        ></v-time-picker>
                      </v-menu>
                    </v-col>
                    <!-- TO TIME -->
                    <v-col class="d-flex mt-2 pt-0" cols="12" sm="6">
                      <v-menu
                        ref="pt_to_time"
                        v-model="toTimeMenu"
                        :close-on-content-click="false"
                        :nudge-right="40"
                        transition="scale-transition"
                        offset-y
                        max-width="290px"
                        min-width="290px"
                      >
                        <template v-slot:activator="{ on, attrs }">
                          <v-text-field
                            v-model="publicTransport.toTime"
                            label="To Time"
                            class="mb-0 pb-0"
                            prepend-inner-icon="fas fa-clock"
                            readonly
                            v-bind="attrs"
                            v-on="on"
                          ></v-text-field>
                        </template>
                        <v-time-picker
                          v-if="toTimeMenu"
                          format="24hr"
                          full-width
                          :color="appColor.primary"
                          v-model="publicTransport.toTime"
                          @click:minute="
                            $refs.pt_from_time.save(publicTransport.toTime)
                          "
                        ></v-time-picker>
                      </v-menu>
                    </v-col>
                    <template v-if="routing === 'transit'">
                      <!-- ACCESS MODE -->
                      <v-col class="d-flex mb-0 pb-0" cols="12" sm="6">
                        <v-select
                          label="Access Mode"
                          v-model="publicTransport.accessMode"
                          class="mb-2 mt-0"
                          item-value="type"
                          hide-details
                          :items="appConfig.routing[3].access_modes"
                        >
                          <template slot="selection" slot-scope="{ item }">
                            <v-row>
                              <v-col cols="3" class="py-0"
                                ><v-icon dense>{{ item.icon }}</v-icon></v-col
                              >
                              <v-col cols="9" class="py-0"
                                ><span class="cb-item">{{
                                  $t(
                                    `isochrones.options.${item.type.toLowerCase()}`
                                  )
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
                                  $t(
                                    `isochrones.options.${item.type.toLowerCase()}`
                                  )
                                }}</span></v-col
                              >
                            </v-row>
                          </template>
                        </v-select>
                      </v-col>
                      <!-- EGRESS MODE -->
                      <v-col class="d-flex mb-0 pb-0" cols="12" sm="6">
                        <v-select
                          label="Egress Mode"
                          class="mb-2 mt-0"
                          v-model="publicTransport.egressMode"
                          item-value="type"
                          hide-details
                          :items="appConfig.routing[3].egress_modes"
                        >
                          <template slot="selection" slot-scope="{ item }">
                            <v-row>
                              <v-col cols="3" class="py-0"
                                ><v-icon dense>{{ item.icon }}</v-icon></v-col
                              >
                              <v-col cols="9" class="py-0"
                                ><span class="cb-item">{{
                                  $t(
                                    `isochrones.options.${item.type.toLowerCase()}`
                                  )
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
                                  $t(
                                    `isochrones.options.${item.type.toLowerCase()}`
                                  )
                                }}</span></v-col
                              >
                            </v-row>
                          </template>
                        </v-select>
                      </v-col>
                      <!-- TRANSIT  -->
                      <v-col
                        class="d-flex mb-0 mt-2 pb-0 justify-center align-center"
                        cols="12"
                        sm="12"
                      >
                        <span
                          class="text-center mb-0"
                          color="rgba(0, 0, 0, 0.6)"
                        >
                          Transit Modes
                        </span>
                      </v-col>
                      <v-col
                        class="d-flex mb-5 pb-0 justify-center align-center"
                        cols="12"
                        sm="12"
                      >
                        <v-btn-toggle
                          v-model="publicTransport.transitModes"
                          multiple
                        >
                          <template
                            v-for="(transitMode, index) in routingProfiles
                              .transit.transit_modes"
                          >
                            <v-btn :key="index">
                              <i
                                :class="`${transitMode.icon} fa-2x`"
                                aria-hidden="true"
                                :style="
                                  `width: 40px;color:${
                                    transitMode.color ? transitMode.color : ''
                                  };`
                                "
                              ></i>
                            </v-btn>
                          </template>
                        </v-btn-toggle>
                      </v-col>
                    </template>
                  </template>
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
            <v-icon
              class="mr-2"
              :style="
                isIsochroneCalculationTypeElVisible === true
                  ? { color: appColor.secondary }
                  : {}
              "
              small
              >fas fa-bullseye</v-icon
            >
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
            <v-row
              no-gutters
              justify="center"
              align="center"
              v-if="!['transit', 'car'].includes(routing)"
            >
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
                    @click="calculateIsochrone"
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
                            routingProfiles[calculation.routing].icon
                          }}</v-icon>
                          <span class="ml-1 caption">
                            {{
                              $t(`isochrones.options.${calculation.routing}`)
                            }}
                          </span>

                          <template
                            v-if="
                              !['transit', 'car'].includes(calculation.routing)
                            "
                          >
                            <v-icon small class="text-xs-center mx-2"
                              >fas fa-tachometer-alt
                            </v-icon>
                            <span class="caption">{{
                              calculation.config.settings.speed
                            }}</span>
                          </template>
                          <template
                            v-if="
                              ['transit', 'car'].includes(calculation.routing)
                            "
                          >
                            <v-icon small class="text-xs-center mx-2"
                              >fas fa-clock
                            </v-icon>
                            <span class="caption">{{
                              calculation.config.settings.departure_date
                            }}</span>
                          </template>

                          <span
                            class="pl-2 ml-2 text-xs-center"
                            style="border-left: 1px solid #424242;"
                            >{{
                              $te(
                                `isochrones.options.${calculation.config.scenario.modus}`
                              )
                                ? $t(
                                    `isochrones.options.${calculation.config.scenario.modus}`
                                  )
                                : calculation.config.scenario.modus
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
                  >
                    <v-simple-checkbox
                      :ripple="false"
                      @input="toggleCalculation(calculation)"
                      :value="isCalculationActive(calculation)"
                      :color="appColor.secondary"
                    ></v-simple-checkbox>
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
                  </v-subheader>
                </v-card>
              </template>
            </v-flex>
            <confirm ref="confirm"></confirm>
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
import { toPixel } from "../../utils/MapUtils";
import { Isochrones } from "../../mixins/Isochrones";
import { KeyShortcuts } from "../../mixins/KeyShortcuts";

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
import Overlay from "ol/Overlay";

import {
  geojsonToFeature,
  geometryToWKT,
  computeSingleValuedSurface,
  fromPixel
} from "../../utils/MapUtils";
import DrawInteraction from "ol/interaction/Draw";
import { transform } from "ol/proj.js";
import { unByKey } from "ol/Observable";
//Other
import { EventBus } from "../../EventBus";
import ApiService from "../../services/api.service";
import axios from "axios";
import { parseTimesData } from "../../utils/ParseTimeData";
import { jsolines } from "../../utils/Jsolines";
import { toLonLat } from "ol/proj";
// import { isochroneHeatmap } from "../../utils/IsochroneHeatmap";

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
    isochroneColorPickerState: false,
    activeCalculation: null, // for color palette selection
    activeCalculationMode: null, // for color palette selection,
    //Single Isochrone
    mapClickListener: null,
    // Multiisochrone
    multiIsochronePoiCount: null,
    drawPolygon: null,
    mapPointerMoveKey: null,
    maxAmenities: 150, //TODO: make this a configurable setting
    // Cancel Request Token
    cancelRequestToken: null,
    // ----PT---
    fromTimeMenu: false,
    toTimeMenu: false,
    dateMenu: false,
    //Hover Overlya
    isochroneHoverOverlay: null,
    isochroneHoverOverlayEl: null
  }),
  computed: {
    ...mapGetters("scenarios", {
      activeScenario: "activeScenario"
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
      routing: "routing",
      calculations: "calculations",
      isochroneLayer: "isochroneLayer",
      isochroneOverlayLayer: "isochroneOverlayLayer",
      isochroneRoadNetworkLayer: "isochroneRoadNetworkLayer",
      multiIsochroneSelectionLayer: "multiIsochroneSelectionLayer",
      multiIsochroneMethod: "multiIsochroneMethod",
      colors: "colors",
      defaultIsochroneColor: "defaultIsochroneColor",
      scenarioIsochroneColor: "scenarioIsochroneColor",
      selectedCalculations: "selectedCalculations",
      publicTransport: "publicTransport",
      isochroneRange: "isochroneRange"
    }),
    ...mapFields("map", {
      isMapBusy: "isMapBusy"
    }),
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
        } (${this.$t("isochrones.multiple.limit")}: ${this.maxAmenities})`;
      }
      return text;
    },
    isMultiIsochroneCalculationDisabled() {
      if (
        this.multiIsochronePoiCount > 0 &&
        this.multiIsochronePoiCount < this.maxAmenities
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
      this.createMultiIsochroneSelectionLayer();
      this.setupMapPointerMove();
      this.createIsochroneHoverOverlay();
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
    createIsochroneHoverOverlay() {
      this.isochroneHoverOverlayEl = document.createElement("div");
      this.isochroneHoverOverlayEl.className = "tooltip tooltip-measure";
      this.isochroneHoverOverlay = new Overlay({
        element: this.isochroneHoverOverlayEl,
        autoPan: false,
        autoPanMargin: 40,
        offset: [0, -10],
        positioning: "bottom-center",
        autoPanAnimation: {
          duration: 250
        }
      });
      this.map.addOverlay(this.isochroneHoverOverlay);
    },

    /**
     * Create multi isochrone selection layer
     */
    createMultiIsochroneSelectionLayer() {
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
      if (this.type === "single") {
        this.mapClickListener = this.map.once("singleclick", this.onMapClick);
        this.startHelpTooltip(
          this.$t("map.tooltips.clickForIsochroneCalculation")
        );
      } else {
        this.mapClickListener = this.map.on("singleclick", this.onMapClick);
      }

      if (this.map.getTarget().style) {
        this.map.getTarget().style.cursor = "pointer";
      }
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
      if (this.map.getTarget().style) {
        this.map.getTarget().style.cursor = "pointer";
      }
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
          type: "Polygon"
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
      if (evt.feature) {
        this.multiIsochroneSelectionLayer.getSource().addFeature(evt.feature);
      } else {
        return;
      }
      if (this.selectedPois.length === 0) {
        this.toggleSnackbar({
          type: "error",
          message: this.$t("map.snackbarMessages.selectAmenities"),
          state: true,
          timeout: 10000
        });
        return;
      }
      this.countPois();
      this.toggleSnackbar({
        type:
          this.multiIsochronePoiCount > this.maxAmenities
            ? "error"
            : this.appColor.primary,
        message:
          this.$t("isochrones.multiple.amenityCount") +
          ` ${this.multiIsochronePoiCount} / ${this.maxAmenities}`,
        state: true,
        timeout: 0
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
    countPois() {
      this.multiIsochronePoiCount = 0;
      const region = [];
      const multiIsochroneSelectionLayerFeatures = this.multiIsochroneSelectionLayer
        .getSource()
        .getFeatures();
      if (multiIsochroneSelectionLayerFeatures.length === 0) {
        this.toggleSnackbar({
          type:
            this.multiIsochronePoiCount > this.maxAmenities ||
            this.multiIsochronePoiCount === 0
              ? "error"
              : this.appColor.primary,
          message:
            this.$t("isochrones.multiple.amenityCount") +
            ` ${this.multiIsochronePoiCount} (Limit: ${this.maxAmenities})`,
          state: true,
          timeout: 100000
        });
        return;
      }
      multiIsochroneSelectionLayerFeatures.forEach(feature => {
        if (this.multiIsochroneMethod === "study_area") {
          region.push(feature.get("id"));
        } else {
          const geometry = feature
            .getGeometry()
            .clone()
            .transform("EPSG:3857", "EPSG:4326");
          region.push(geometryToWKT(geometry));
        }
      });
      ApiService.post(`/isochrones/multi/count-pois`, {
        region_type: this.multiIsochroneMethod,
        region,
        scenario_id: 0, //TODO: Get scenario id
        modus: this.calculationMode.active,
        routing_profile: this.routing,
        minutes: this.time,
        speed: this.speed,
        amenities: this.selectedPoisOnlyKeys
      })
        .then(response => {
          if (response.data) {
            const poisNumber = response.data;
            this.multiIsochronePoiCount = poisNumber;
            this.toggleSnackbar({
              type:
                this.multiIsochronePoiCount > this.maxAmenities ||
                this.multiIsochronePoiCount === 0
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
          this.countPois();
          return;
        }
        const subStudyAreaAtCoord = this.subStudyAreaLayer
          .getSource()
          .getFeaturesAtCoordinate(evt.coordinate);
        if (subStudyAreaAtCoord.length > 0) {
          const feature = subStudyAreaAtCoord[0].clone();
          this.multiIsochroneSelectionLayer.getSource().addFeature(feature);
        }
        this.countPois();
      } else {
        const startPoint = {
          x: coordinateWgs84[0],
          y: coordinateWgs84[1]
        };
        const calculationNumber = this.calculations.length + 1;
        const isochroneMarkerFeature = new Feature({
          geometry: new Point(evt.coordinate),
          calculationNumber: calculationNumber
        });
        isochroneMarkerFeature.setId("isochrone_marker_" + calculationNumber);
        isochroneMarkerFeature.set("showLabel", false);
        this.isochroneLayer.getSource().addFeature(isochroneMarkerFeature);
        const promiseArray = this.calculateIsochrone(startPoint);
        axios
          .all(promiseArray)
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
     * @param  {startPoint} startPoint The start point of the isochrone. Only used for single isochrone.
     */
    calculateIsochrone(startPoint) {
      let routing = this.routing;
      let _routing = this.routing; //store selected routing for later use
      let mode = routing;
      //-- SETTINGS --//
      let settings = {
        travel_time: 20, //TODO: Make this configurable
        speed: this.speed
      };
      if (routing.includes("walking") || routing.includes("cycling")) {
        routing = routing.split("_");
        if (routing[0] === "walking") {
          settings["walking_profile"] = routing[1];
          mode = "walking";
        } else {
          settings["cycling_profile"] = routing[1];
          mode = "cycling";
        }
      }
      if (["car", "transit"].includes(routing)) {
        const transitModes = [];
        this.publicTransport.transitModes.forEach(index => {
          transitModes.push(
            this.routingProfiles.transit.transit_modes[index].type
          );
        });
        const fromTimeArr = this.publicTransport.fromTime.split(":");
        const toTimeArr = this.publicTransport.toTime.split(":");
        settings = {
          ...settings,
          travel_time: 60,
          transit_modes: routing === ["car"] ? "" : transitModes,
          departure_date: this.publicTransport.date,
          access_mode:
            routing === "car" ? "car" : this.publicTransport.accessMode,
          egress_mode: this.publicTransport.egressMode,
          bike_traffic_stress: 4,
          from_time: fromTimeArr[0] * 3600 + fromTimeArr[1] * 60,
          to_time: toTimeArr[0] * 3600 + toTimeArr[1] * 60,
          // Advanced settings (TODO: UI for these)
          max_rides: 4,
          max_bike_time: 20,
          max_walk_time: 20,
          percentiles: [5, 25, 50, 75, 95],
          monte_carlo_draws: 200
        };
      }

      //-- STARTING_POINT --//
      let starting_point = {
        input: []
      };
      if (this.type === "single") {
        // single
        starting_point.input.push({
          lat: startPoint.y,
          lon: startPoint.x
        });
      } else {
        //multiple
        const regionType = this.multiIsochroneMethod;
        starting_point.input = this.selectedPoisOnlyKeys;
        starting_point["region_type"] = regionType;
        const features = this.multiIsochroneSelectionLayer
          .getSource()
          .getFeatures();
        if (regionType === "study_area") {
          // Get selected study areas ids
          const region = [];
          features.forEach(feature => {
            region.push(feature.get("id").toString());
          });
          starting_point["region"] = region;
        } else {
          // Get polygon geometry
          const feature = features[0];
          if (!feature) return;
          const geometry = feature
            .getGeometry()
            .clone()
            .transform("EPSG:3857", "EPSG:4326");
          const region = geometryToWKT(geometry);
          starting_point["region"] = [region];
        }
      }
      //-- SCENARIO --// (** CONSIDERED ONLY FOR WALKING AND CYCLING **)
      let scenario = {
        id: this.activeScenario ? this.activeScenario : 0,
        modus: this.calculationMode.active
      };

      //-- OUTPUT --//
      let output = {
        type: "grid",
        resolution: ["car", "transit"].includes(routing) ? 9 : 12
      };
      const payloads = [];

      // If modus is "comparision" do two requests one for default and one for scenario
      if (
        this.calculationMode.active === "comparision" &&
        (routing.includes("walking") || routing.includes("cycling"))
      ) {
        const defaultPayload = {
          mode,
          starting_point: starting_point,
          settings: settings,
          scenario: {
            id: 0,
            modus: "default"
          },
          output: output
        };
        const scenarioPayload = {
          mode,
          starting_point: starting_point,
          settings: settings,
          scenario: {
            id: this.activeScenario,
            modus: "scenario"
          },
          output: output
        };
        payloads.push(defaultPayload, scenarioPayload);
      } else {
        payloads.push({
          mode,
          settings,
          starting_point,
          scenario,
          output
        });
      }
      this.isMapBusy = true;
      this.isIsochroneBusy = true;
      const promiseArray = [];
      payloads.forEach(payload => {
        const axiosInstance = axios.create();
        promiseArray.push(
          new Promise((resolve, reject) => {
            axiosInstance
              .post(`./isochrones`, payload, {
                responseType: "arraybuffer"
              })
              .then(response => {
                resolve(response);
                if (response.data) {
                  const isochroneSurface = parseTimesData(response.data);
                  let singleValuedSurface = {};
                  if (isochroneSurface.depth === 1) {
                    singleValuedSurface = isochroneSurface;
                    singleValuedSurface["surface"] = isochroneSurface.data;
                  } else {
                    singleValuedSurface = computeSingleValuedSurface(
                      isochroneSurface,
                      50
                    );
                  }
                  const {
                    surface,
                    width,
                    height,
                    west,
                    north,
                    zoom
                    // eslint-disable-next-line no-undef
                  } = singleValuedSurface;
                  const isochronePolygon = jsolines({
                    surface,
                    width,
                    height,
                    cutoff: this.isochroneRange,
                    project: ([x, y]) => {
                      const ll = fromPixel({ x: x + west, y: y + north }, zoom);
                      return [ll.lon, ll.lat];
                    }
                  });
                  let olFeatures = geojsonToFeature(isochronePolygon, {
                    dataProjection: "EPSG:4326",
                    featureProjection: "EPSG:3857"
                  });

                  const calculationNumber = this.calculations.length + 1;
                  const isochroneCalculationUid =
                    olFeatures[0].get("isochrone_calculation_id") ||
                    calculationNumber;
                  olFeatures[0].setId(
                    "isochrone_feature_" + isochroneCalculationUid
                  );
                  olFeatures[0].set("calculationNumber", calculationNumber);
                  let calculation = {
                    id: calculationNumber,
                    routing: _routing,
                    config: payload,
                    rawData: isochroneSurface,
                    surfaceData: singleValuedSurface,
                    feature: olFeatures[0]
                  };
                  //Geocode
                  delete axiosInstance.defaults.headers.common["Authorization"];
                  axiosInstance
                    .get(
                      `https://api.locationiq.com/v1/reverse.php?key=ca068d7840bca4&lat=${startPoint.y}&lon=${startPoint.x}&format=json`
                    )
                    .then(response => {
                      if (
                        response.status === 200 &&
                        response.data.display_name
                      ) {
                        const address = response.data.display_name;
                        calculation.position = address;
                      }
                    })
                    .catch(() => {
                      calculation.position = "Unknown";
                    })
                    .finally(() => {
                      this.isMapBusy = false;
                      this.isIsochroneBusy = false;
                      if (this.selectedCalculations.length === 2) {
                        // Remove first calculation if length is already 2
                        this.selectedCalculations.shift();
                      }
                      this.calculations.unshift(calculation);
                      this.selectedCalculations.push(calculation);
                      this.isOptionsElVisible = false;
                    });
                }
              })
              .catch(error => {
                reject(error);
              })
              .finally(() => {
                this.multiIsochroneSelectionLayer.getSource().clear();
                this.isMapBusy = false;
                this.isIsochroneBusy = false;
                this.clear();
              });
          })
        );
      });
      return promiseArray;
    },
    /**
     * Map pointer move event .
     */
    setupMapPointerMove() {
      this.mapPointerMoveListenerKey = this.map.on("pointermove", evt => {
        this.isochroneHoverOverlay.setPosition(undefined);
        if (
          evt.dragging ||
          !this.isochroneLayer ||
          this.selectedCalculations.length === 0
        ) {
          return;
        }
        const features = this.isochroneLayer
          .getSource()
          .getFeaturesAtCoordinate(evt.coordinate)
          .filter(
            f =>
              f.get("calculationNumber") &&
              f.getGeometry().getType() !== "Point"
          );
        let overlayerInnerHtml = ``;
        if (features.length > 0) {
          features.forEach((feature, index) => {
            const calculationId = feature.get("calculationNumber");
            const calculation = this.selectedCalculations.find(
              c => c.id === calculationId
            );
            const lonLat = toLonLat(evt.coordinate);
            const pixel = toPixel(lonLat, calculation.surfaceData.zoom);
            const x = Math.floor(pixel.x - calculation.surfaceData.west);
            const y = Math.floor(pixel.y - calculation.surfaceData.north);
            const depthIndex = calculation.rawData.depth === 1 ? 0 : 2;
            let time = null;
            if (calculation.rawData.contains(x, y, depthIndex)) {
              time = [calculation.rawData.get(x, y, depthIndex)];
            }
            if (time) {
              overlayerInnerHtml += `<div>${calculationId}- Time: ${time} min</div>`;
            }
            if (features.length === 2 && index == 0) {
              overlayerInnerHtml += `<br>`;
            }
            this.isochroneHoverOverlayEl.innerHTML = overlayerInnerHtml;
          });
          this.isochroneHoverOverlay.setPosition(evt.coordinate);
        }
      });
    },
    isCalculationActive(calculation) {
      let isActive = false;
      this.selectedCalculations.forEach(selectedCalculation => {
        if (selectedCalculation.id === calculation.id) {
          isActive = true;
        }
      });
      return isActive;
    },
    toggleCalculation(calculation) {
      const isActive = this.isCalculationActive(calculation);
      if (isActive) {
        // Remove
        this.selectedCalculations = this.selectedCalculations.filter(
          selectedCalculation => {
            return selectedCalculation.id !== calculation.id;
          }
        );
      } else {
        if (this.selectedCalculations.length === 2) {
          // Remove first calculation if length is already 2
          this.selectedCalculations.shift();
        }
        this.selectedCalculations.push(calculation);
      }
    },
    // ------------CLEAR----------
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
      this.calculations = this.calculations.filter(
        calculation => calculation.id !== id
      );
      this.selectedCalculations = this.selectedCalculations.filter(
        selectedCalculation => selectedCalculation.id !== id
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
          if (isochroneFeature.getGeometry().getType() === "Point") {
            isochroneFeature.setId("isochrone_marker_" + updatedNr);
            isochroneFeature.set("calculationNumber", updatedNr);
          } else {
            isochroneFeature.set("calculationNumber", updatedNr);
          }
        }
      });
    },
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
      if (this.map.getTarget().style) {
        this.map.getTarget().style.cursor = "";
      }
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
      this.appConfig.routing.forEach(routing => {
        if (routing.type === this.routing) {
          this.speed = routing.speed;
        }
      });
      if (this.routing === "transit") {
        this.type = "single";
      }
    },
    selectedPois() {
      if (this.multiIsochroneMethod) {
        this.countPois();
      }
    },
    type(value) {
      if (value === "single" && this.subStudyAreaLayer.getVisible()) {
        this.subStudyAreaLayer.setVisible(false);
      }
    },
    selectedCalculations() {
      this.isochroneLayer
        .getSource()
        .getFeatures()
        .forEach(feature => {
          console.log(feature.getGeometry().getType());
          if (feature.getGeometry().getType() !== "Point") {
            this.isochroneLayer.getSource().removeFeature(feature);
          }
        });
      this.selectedCalculations.forEach(calculation => {
        this.isochroneLayer.getSource().addFeatures([calculation.feature]);
      });
      if (this.selectedCalculations.length === 0) {
        this.isochroneRange = 15;
        // Reset features to 15 minutes.
        this.calculations.forEach(calculation => {
          const {
            surface,
            width,
            height,
            west,
            north,
            zoom
            // eslint-disable-next-line no-undef
          } = calculation.surfaceData;
          const isochronePolygon = jsolines({
            surface,
            width,
            height,
            cutoff: this.isochroneRange,
            project: ([x, y]) => {
              const ll = fromPixel({ x: x + west, y: y + north }, zoom);
              return [ll.lon, ll.lat];
            }
          });
          let olFeatures = geojsonToFeature(isochronePolygon, {
            dataProjection: "EPSG:4326",
            featureProjection: "EPSG:3857"
          });
          calculation.feature.setGeometry(olFeatures[0].getGeometry());
        });
      }
    }
  },
  created() {
    // Set default routing
    const defaultRouting = this.appConfig.routing[0];
    this.routing = defaultRouting.type;
    if (defaultRouting.speed) {
      this.speed = defaultRouting.speed;
    }

    // Set default values for public transport routing
    if (this.routingProfiles.transit) {
      this.publicTransport.accessMode = this.routingProfiles.transit.access_modes[0].type;
      this.publicTransport.egressMode = this.routingProfiles.transit.egress_modes[0].type;
      const fromTimeDate = new Date(0);
      fromTimeDate.setSeconds(this.routingProfiles.transit.from_time);
      this.publicTransport.fromTime = fromTimeDate
        .toISOString()
        .substring(11, 16);

      const toTimeDate = new Date(0);
      toTimeDate.setSeconds(this.routingProfiles.transit.to_time);
      this.publicTransport.toTime = toTimeDate.toISOString().substring(11, 16);
      this.publicTransport.transitModes = [
        ...this.routingProfiles.transit.transit_modes.keys()
      ];
    }
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

.hover-info {
  position: absolute;
  height: 1px;
  width: 1px;
  z-index: 100;
}
.hover-tooltip.in {
  opacity: 1;
}
.hover-tooltip-top .tooltip-arrow {
  border-top-color: white;
}
.tooltip-inner {
  border: 2px solid white;
}
</style>
