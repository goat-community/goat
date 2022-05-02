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
                  <v-col class="d-flex mt-2 pt-0" cols="12" sm="6">
                    <v-text-field
                      :label="$t(`isochrones.options.time`)"
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
                  <v-col class="d-flex mt-2 pt-0" cols="12" sm="6">
                    <v-text-field
                      :label="$t(`isochrones.options.nr`)"
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
                        v-if="
                          calculation.calculationMode !== 'comparison' &&
                            calculation.calculationType !== 'multiple'
                        "
                        class="mt-4 mr-3"
                        dense
                        :color="appColor.secondary"
                        hide-details
                        :disabled="isIsochroneBusy"
                        @change="
                          toggleRoadNetwork(
                            $event,
                            calculation,
                            calculation.calculationMode
                          )
                        "
                        :input-value="
                          calculation.additionalData[
                            calculation.calculationMode
                          ]
                            ? calculation.additionalData[
                                calculation.calculationMode
                              ].state
                            : false
                        "
                      >
                        <template v-slot:label>
                          <span class="caption">{{
                            $t("isochrones.results.roadNetwork")
                          }}</span>
                        </template>
                      </v-switch>
                      <v-switch
                        class="mt-4"
                        :input-value="isCalculationActive(calculation)"
                        dense
                        :color="appColor.secondary"
                        hide-details
                        @change="toggleIsochroneWindow($event, calculation)"
                      >
                        <template v-slot:label>
                          <span class="caption">{{
                            $t("isochrones.results.dataTable")
                          }}</span>
                        </template>
                      </v-switch>
                    </v-row>
                    <v-row
                      class="mb-2"
                      v-if="calculation.calculationType === 'multiple'"
                      justify-center
                      align-center
                      no-gutters
                    >
                      <v-switch
                        class="mt-2 ml-1"
                        dense
                        @change="toggleStudyArea($event, calculation)"
                        :color="appColor.secondary"
                        :input-value="
                          getStudyAreaToggleSwitchState(calculation)
                        "
                        hide-details
                      >
                        <template v-slot:label>
                          <span class="caption">{{
                            $t("isochrones.additionalLayers.studyArea")
                          }}</span>
                        </template>
                      </v-switch>
                      <!-- TODO: Isochrone starting points not yet available -->
                      <v-switch
                        :disabled="true"
                        class="mt-2 ml-3"
                        dense
                        :color="appColor.secondary"
                        hide-details
                      >
                        <template v-slot:label>
                          <span class="caption">{{
                            $t("isochrones.additionalLayers.startingPoints")
                          }}</span>
                        </template>
                      </v-switch>
                    </v-row>
                    <v-divider></v-divider>
                    <v-row
                      no-gutters
                      :key="index"
                      v-for="(data, key, index) in groupedCalculationData(
                        calculation.data
                      )"
                    >
                      <v-row
                        no-gutters
                        v-if="calculation.calculationMode === 'comparison'"
                        style="width:100%;background-color:#EEEEEE;border-radius:4px;"
                        class="mr-0 mt-1 pa-1"
                      >
                        <v-col cols="4" justify="start" align="start">
                          <v-row no-gutters justify="start" align="start">
                            <span class="result-title subtitle-2 pb-0 mb-0">
                              {{
                                data[0] && data[0].modus
                                  ? $te(`isochrones.mode.${data[0].modus}`)
                                    ? $t(`isochrones.mode.${data[0].modus}`)
                                    : data[0].modus
                                  : key
                              }}
                            </span>
                          </v-row>
                        </v-col>
                        <v-col cols="8" justify="end" align-end class="pr-1">
                          <v-row no-gutters justify="end" align="center">
                            <v-switch
                              v-if="calculation.calculationType !== 'multiple'"
                              class="ma-0 pa-0"
                              dense
                              :color="appColor.secondary"
                              hide-details
                              @change="
                                toggleRoadNetwork(
                                  $event,
                                  calculation,
                                  data[0].modus
                                )
                              "
                              :disabled="isIsochroneBusy"
                              :input-value="
                                data &&
                                data[0] &&
                                calculation.additionalData[data[0].modus]
                                  ? calculation.additionalData[data[0].modus]
                                      .state
                                  : false
                              "
                            >
                              <template v-slot:label>
                                <span class="caption">{{
                                  $t("isochrones.results.roadNetwork")
                                }}</span>
                              </template>
                            </v-switch>
                          </v-row>
                        </v-col>
                      </v-row>
                      <v-data-table
                        dense
                        style="width:100%"
                        :headers="
                          calculation.calculationType === 'single'
                            ? headersSingle
                            : headersMulti
                        "
                        :items="data"
                        class="elevation-0 subtitle-1 pb-2"
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
                                  @change="
                                    toggleCalculation(
                                      calculation,
                                      calculation.calculationMode ===
                                        'comparison'
                                        ? data[0].modus
                                        : null
                                    )
                                  "
                                  :input-value="
                                    getToggleCalculationCheckboxState(data)
                                  "
                                  :indeterminate="
                                    getToggleCalculationCheckboxIndeterminateState(
                                      data
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
                            @change="
                              toggleIsochroneVisibility(item, calculation, data)
                            "
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
                    </v-row>
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
//TODO: ADD STUDY AREA LAYER AND POIS FOR MULTIISOCHRONES
//TODO: FIX MULTIISOCHRONE DATA TABLE WINDOW
import { Mapable } from "../../mixins/Mapable";
import { Isochrones } from "../../mixins/Isochrones";
import { KeyShortcuts } from "../../mixins/KeyShortcuts";
//Child components
import Download from "./IsochronesDownload";
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
  geometryToWKT,
  geobufToFeatures
} from "../../utils/MapUtils";
import DrawInteraction from "ol/interaction/Draw";
import IsochroneUtils from "../../utils/IsochroneUtils";
import { groupBy } from "../../utils/Helpers";
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
    selectedCalculation: null,
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
    cancelRequestToken: null
  }),
  components: {
    download: Download,
    IsochroneColorPicker
  },
  computed: {
    ...mapGetters("isochrones", {
      calculations: "calculations"
    }),
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
      scenarioIsochroneColor: "scenarioIsochroneColor",
      selectedThematicData: "selectedThematicData"
    }),
    ...mapFields("map", {
      isMapBusy: "isMapBusy"
    }),
    headersSingle() {
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
    headersMulti() {
      return [
        {
          text: this.$t("isochrones.results.table.visible"),
          value: "visible",
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
      this.setUpCtxMenu();

      EventBus.$on("show-isochrone-window", this.showIsochroneWindow);
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
        isochroneMarkerFeature.set("showLabel", false);
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
     * @param  {ol/Feature} isochroneMarkerFeature The starting point for the isochrone calculation (Optional)
     */
    calculateIsochrone(params) {
      const type = this.type;
      const time = this.time;
      const speed = this.speed;
      const routing = this.routing;
      const steps = this.steps;
      const modus = this.calculationMode.active;
      const scenario_id = this.activeScenario ? this.activeScenario : 0;
      const baseParams = {
        minutes: time,
        speed,
        modus,
        n: steps,
        routing_profile: routing,
        scenario_id
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
                const isochroneCalculationUid =
                  feature.get("isochrone_calculation_id") || calculationNumber;
                feature.setId(
                  "isochrone_feature_" + isochroneCalculationUid + "_" + index
                );
                let color = "";
                let level = feature.get("step");
                let modus = feature.get("modus") || modus;
                if (modus === "default" || modus === "comparison") {
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
                  type: feature.get("modus")
                    ? this.$t(
                        `isochrones.mode.${feature.get("modus").toLowerCase()}`
                      )
                    : this.$t(`isochrones.mode.${modus.toLowerCase()}`),
                  isochrone_calculation_id: isochroneCalculationUid,
                  modus: modus,
                  range: Math.round(feature.get("step") / 60) + " min",
                  color: color,
                  area: getPolygonArea(feature.getGeometry()),
                  population:
                    feature.get("reached_opportunities").sum_pop ||
                    feature.get("reached_opportunities").reached_population,
                  isVisible: true
                };
                feature.set("isVisible", true);
                feature.set("calculationNumber", calculationNumber);
                feature.set("color", color);
                feature.set("calculationType", type);
                feature.set("hoverColor", "");
                feature.set("showLabel", false);
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
                const markerFeature = this.isochroneLayer
                  .getSource()
                  .getFeatureById("isochrone_marker_" + calculationNumber);
                markerFeature.set("speed", speed);
                markerFeature.set("routing", routing);
                const startPointCoord = markerFeature
                  .getGeometry()
                  .getCoordinates();
                const wgs84Coord = toLonLat(startPointCoord);
                //Geocode

                delete axiosInstance.defaults.headers.common["Authorization"];
                axiosInstance
                  .get(
                    `https://api.locationiq.com/v1/reverse.php?key=ca068d7840bca4&lat=${wgs84Coord[1]}&lon=${wgs84Coord[0]}&format=json`
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
                    this.isMapBusy = false;
                    this.isIsochroneBusy = false;
                    this.calculations.forEach(calculation => {
                      calculation.isExpanded = false;
                    });
                    this.calculations.unshift(transformedData);
                    this.isochroneLayer.getSource().addFeatures(olFeatures);

                    this.toggleIsochroneWindow(true, transformedData);
                    this.isOptionsElVisible = false;
                  });
              } else {
                transformedData.position = "Multi Isochrone Calculation";
                this.calculations.forEach(calculation => {
                  calculation.isExpanded = false;
                });
                transformedData.additionalData["features"] = [];
                this.multiIsochroneSelectionLayer
                  .getSource()
                  .getFeatures()
                  .forEach(feature => {
                    const clonedFeature = feature.clone();
                    transformedData.additionalData["features"].push(
                      clonedFeature
                    );
                  });
                this.isochroneOverlayLayer
                  .getSource()
                  .addFeatures(transformedData.additionalData["features"]);
                this.calculations.unshift(transformedData);
                this.isochroneLayer.getSource().addFeatures(olFeatures);
                this.toggleIsochroneWindow(true, transformedData);
                this.isOptionsElVisible = false;
                this.isMapBusy = false;
                this.isIsochroneBusy = false;
              }
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
      });
    },
    calculateMultiIsochrone() {
      const regionType = this.multiIsochroneMethod;
      const payload = {
        region_type: regionType
      };
      const features = this.multiIsochroneSelectionLayer
        .getSource()
        .getFeatures();
      if (regionType === "study_area") {
        // Get selected study areas ids
        const region = [];
        features.forEach(feature => {
          region.push(feature.get("id").toString());
        });
        payload.region = region;
      } else {
        // Get polygon geometry
        const feature = features[0];
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
    isCalculationActive(calculation) {
      if (!this.selectedThematicData) {
        return false;
      }
      if (calculation.id === this.selectedThematicData.calculationId) {
        return true;
      } else {
        return false;
      }
    },
    groupedCalculationData(data) {
      const groupedCalculations = groupBy(data, "type");
      return groupedCalculations;
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
    showIsochroneWindow(calculationId) {
      const calculation = this.calculations.filter(
        calculation => calculation.id === calculationId
      );
      if (calculation && calculation[0]) {
        this.toggleIsochroneWindow(true, calculation[0]);
      }
    },
    toggleIsochroneWindow(state, calculation) {
      if (state === false) {
        this.isochroneLayer
          .getSource()
          .getFeatures()
          .forEach(f => {
            f.set("highlightFeature", false);
          });
        this.selectedThematicData = null;
        return;
      }
      const features = IsochroneUtils.getCalculationFeatures(
        calculation,
        this.isochroneLayer
      );

      features.forEach(f => {
        f.set("highlightFeature", true);
      });
      const pois = IsochroneUtils.getCalculationPoisObject(features);
      const payload = {
        calculationId: calculation.id,
        calculationType: calculation.calculationType,
        pois: pois
      };
      if (calculation.calculationType === "multiple") {
        const multiIsochroneTableData = IsochroneUtils.getMultiIsochroneTableData(
          features
        );
        payload.multiIsochroneTableData = multiIsochroneTableData;
      }
      this.selectedThematicData = payload;
    },
    // eslint-disable-next-line no-unused-vars
    toggleIsochroneVisibility(feature, calculation, data) {
      this.toggleIsochroneFeatureVisibility(feature);
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
    toggleCalculation(calculation, modus = null) {
      let data = calculation.data;
      if (modus) {
        data = data.filter(calculation => calculation.modus === modus);
      }
      const isIndeterminateState = this.getToggleCalculationCheckboxIndeterminateState(
        data
      );
      data.forEach(isochrone => {
        let featureId = isochrone.id;
        let isochroneFeature = this.isochroneLayer
          .getSource()
          .getFeatureById(featureId);
        if (isochroneFeature) {
          // Edge case for comparision

          if (modus && isochroneFeature.get("modus") === modus) {
            if (isIndeterminateState) {
              isochrone.isVisible = false;
            } else {
              isochrone.isVisible = !isochrone.isVisible;
            }
            isochroneFeature.set("isVisible", isochrone.isVisible);
          }
          if (!modus) {
            if (isIndeterminateState) {
              isochrone.isVisible = false;
            } else {
              isochrone.isVisible = !isochrone.isVisible;
            }
            isochroneFeature.set("isVisible", isochrone.isVisible);
          }
        }
      });
      const visibleCount = data.filter(isochrone => isochrone.isVisible).length;
      if (visibleCount === 0) {
        calculation.isVisible = false;
      } else {
        calculation.isVisible = true;
      }
    },
    toggleRoadNetwork(state, calculation, type) {
      const roadNetworkSource = this.isochroneRoadNetworkLayer.getSource();
      if (calculation.additionalData[type]) {
        // Network is already fetched
        const features = calculation.additionalData[type].features;
        if (state === true) {
          features.forEach(feature => {
            roadNetworkSource.addFeature(feature);
          });
        } else {
          features.forEach(feature => {
            if (roadNetworkSource.hasFeature(feature)) {
              roadNetworkSource.removeFeature(feature);
            }
          });
        }
      } else {
        this.isMapBusy = true;
        this.isIsochroneBusy = true;
        // Network is not fetched yet
        ApiService.get_(
          `/isochrones/network/${calculation.data[0].isochrone_calculation_id}/${type}?return_type=geobuf`,
          {
            responseType: "arraybuffer",
            headers: {
              Accept: "application/pdf"
            }
          }
        )
          .then(response => {
            if (response.data) {
              const olFeatures = geobufToFeatures(response.data, {
                dataProjection: "EPSG:4326",
                featureProjection: "EPSG:3857"
              });
              calculation.additionalData[type] = {
                features: olFeatures,
                state: true
              };
              // Set isochrone calculation speed property for styling purpose
              const speed = parseFloat(calculation.speed.split(" ")[0]);
              const lowestCostValue = 0; // TODO: Find lowest and highest based on response data
              const highestCostValue = 1200;
              olFeatures.forEach(feature => {
                feature.set("speed", speed);
                const cost = feature.get("cost");
                const modus = feature.get("modus");
                let color;
                if (modus === "default") {
                  color = this.colors[calculation.defaultColorPalette];
                } else if (modus === "scenario") {
                  color = this.colors[calculation.scenarioColorPalette];
                }
                const interpolatedColor = IsochroneUtils.getInterpolatedColor(
                  lowestCostValue,
                  highestCostValue,
                  cost,
                  color
                );
                feature.set("color", interpolatedColor);
              });
              roadNetworkSource.addFeatures(olFeatures);
            }
          })
          .catch(error => {
            console.log(error);
          })
          .finally(() => {
            this.isMapBusy = false;
            this.isIsochroneBusy = false;
          });
      }
    },
    toggleStudyArea(state, calculation) {
      const features = calculation.additionalData["features"];
      features.forEach(feature => {
        const hasFeature = this.isochroneOverlayLayer
          .getSource()
          .hasFeature(feature);
        if (state === false && hasFeature) {
          this.isochroneOverlayLayer.getSource().removeFeature(feature);
        } else if (state === true && !hasFeature) {
          this.isochroneOverlayLayer.getSource().addFeature(feature);
        }
      });
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
    getToggleCalculationCheckboxState(calculationData) {
      const countVisibleFeatures = calculationData.filter(
        o => o.isVisible === true
      );
      if (countVisibleFeatures.length === 0) {
        return false;
      }
      return true;
    },
    getToggleCalculationCheckboxIndeterminateState(calculationData) {
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
    getStudyAreaToggleSwitchState(calculation) {
      const features = calculation.additionalData["features"];
      let hasFeature = false;
      features.forEach(feature => {
        if (this.isochroneOverlayLayer.getSource().hasFeature(feature)) {
          hasFeature = true;
        }
      });
      return hasFeature;
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
          if (isochroneFeature.getGeometry().getType() === "Point") {
            isochroneFeature.setId("isochrone_marker_" + updatedNr);
            isochroneFeature.set("calculationNumber", updatedNr);
          } else {
            isochroneFeature.set("calculationNumber", updatedNr);
          }
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
      // Remove isochrone overlay features
      if (Array.isArray(calculation.additionalData.features)) {
        calculation.additionalData.features.forEach(feature => {
          if (this.isochroneOverlayLayer.getSource().hasFeature(feature)) {
            this.isochroneOverlayLayer.getSource().removeFeature(feature);
          }
        });
      }

      this.isochroneOverlayLayer.changed();
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
