<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-subheader class="mb-4">
        <span class="title">{{ $t("appBar.edit.title") }}</span>
      </v-subheader>
      <v-card-text class="pt-0 pb-0 px-0 mx-0">
        <v-divider></v-divider>
      </v-card-text>
      <v-card-text class="pa-2">
        <div v-if="scenarioList.length === 1 && scenarioList[0].id === null">
          <v-tooltip top>
            <template v-slot:activator="{ on }">
              <v-btn
                v-on="on"
                class="mt-n11 ml-2"
                :color="appColor.primary"
                @click="showScenarioDialog = true"
                fab
                dark
                small
              >
                <v-icon dark>add</v-icon>
              </v-btn>
            </template>
            <span>{{ $t("appBar.edit.createScenario") }}</span>
          </v-tooltip>
        </div>
      </v-card-text>

      <v-card class="px-16 mx-4 py-0 mb-2 fill-height" flat>
        <!-- CREATE SCENARIO  -->
        <div v-if="scenarioList.length > 1">
          <v-row class="mt-4" no-gutters no-wrap>
            <v-select
              v-model="activeScenario"
              :items="scenarioList"
              style="max-width: 260px;"
              item-text="scenario_name"
              item-value="id"
              label="Select scenario"
              solo
            >
              <template
                class="create-scenario-text"
                slot="selection"
                slot-scope="{ item }"
              >
                {{ item.scenario_name }}
              </template>
              <template
                class="create-scenario-text"
                slot="item"
                slot-scope="{ item }"
              >
                {{ item.scenario_name }}
              </template>
            </v-select>

            <div v-if="activeScenario">
              <v-speed-dial
                style="z-index:100;"
                v-model="scenarioSpeedDialFab"
                direction="bottom"
                class="ml-3 mt-2"
                transition="slide-y-reverse-transition"
              >
                <template v-slot:activator>
                  <v-btn
                    v-model="scenarioSpeedDialFab"
                    :color="scenarioSpeedDialFab ? 'error' : appColor.primary"
                    dark
                    small
                    fab
                  >
                    <v-icon v-if="scenarioSpeedDialFab">
                      close
                    </v-icon>
                    <v-icon v-else>
                      more_vert
                    </v-icon>
                  </v-btn>
                </template>
                <v-tooltip top>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      v-on="on"
                      :color="appColor.primary"
                      fab
                      dark
                      x-small
                      v-if="scenarios.length < currentUser.limit_scenarios"
                      @click="showScenarioDialog = true"
                    >
                      <v-icon dark>add</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.createScenario") }}</span>
                </v-tooltip>
                <v-tooltip v-show="activeScenario" top>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      v-show="activeScenario"
                      v-on="on"
                      :color="appColor.primary"
                      fab
                      dark
                      x-small
                      @click="
                        showScenarioDialog = true;
                        activeScenarioId = activeScenario;
                      "
                    >
                      <v-icon dark>edit</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.editScenarioName") }}</span>
                </v-tooltip>
                <v-tooltip v-show="activeScenario" top>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      v-show="activeScenario"
                      v-on="on"
                      color="error"
                      fab
                      dark
                      x-small
                      @click="deleteScenario"
                    >
                      <v-icon dark>delete</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.deleteScenario") }}</span>
                </v-tooltip>
              </v-speed-dial>
            </div>
            <div v-else>
              <v-tooltip top>
                <template v-slot:activator="{ on }">
                  <v-btn
                    v-on="on"
                    :color="appColor.primary"
                    class="ml-3 mt-2"
                    fab
                    :disabled="scenarios.length >= currentUser.limit_scenarios"
                    small
                    @click="showScenarioDialog = true"
                  >
                    <v-icon color="white">add</v-icon>
                  </v-btn>
                </template>
                <span>{{ $t("appBar.edit.createScenario") }}</span>
              </v-tooltip>
            </div>
          </v-row>
        </div>
        <v-alert
          v-if="scenarios.length >= currentUser.limit_scenarios"
          dense
          outlined
          type="error"
        >
          {{ $t("appBar.edit.scenarioLimitReached") }}
        </v-alert>
        <div v-if="scenarioList.length > 1 && activeScenario">
          <v-divider></v-divider>
          <v-subheader class="ml-0 pl-0 mb-0 pb-0">
            <v-icon :style="`color:${appColor.secondary};`" small class="mr-2"
              >fas fa-layer-group</v-icon
            >
            <h3>{{ $t("appBar.edit.selectLayer") }}</h3>
          </v-subheader>
          <v-select
            class="mt-4"
            :items="editableLayers"
            v-model="selectedLayer"
            item-value="name"
            return-object
            solo
            :label="$t('appBar.edit.layerToEdit')"
          >
            <template slot="selection" slot-scope="{ item }">
              {{ translate("layerName", item.name) }}
            </template>
            <template slot="item" slot-scope="{ item }">
              {{ translate("layerName", item.name) }}
            </template>
          </v-select>
        </div>

        <template v-if="selectedLayer && schema[layerName] && activeScenario">
          <v-divider></v-divider>
          <!-- ==== <EDIT> ====-->

          <v-subheader
            v-show="selectedLayer !== null && activeScenario"
            class="clickable ml-0 pl-0"
            @click="editElVisible = !editElVisible"
          >
            <v-icon
              :style="
                editElVisible === true ? { color: appColor.secondary } : {}
              "
              small
              class="mr-2"
              >fas fa-edit</v-icon
            >
            <h3>{{ $t("appBar.edit.editTools") }}</h3>
            <v-spacer></v-spacer>
            <v-icon v-html="editElVisible === true ? 'remove' : 'add'"></v-icon>
          </v-subheader>

          <div class="ml-2" v-if="editElVisible">
            <span
              v-show="selectedLayer != null && selectedLayer['name'] !== 'poi'"
              class="py-1 mb-0 mt-3 pl-0 ml-0"
            >
              <h4>{{ $t("appBar.edit.selectFeatures") }}</h4>
            </span>

            <v-flex
              xs12
              v-show="selectedLayer != null && selectFeaturesVisible"
              class="mt-1 pt-0 mb-4"
            >
              <v-btn-toggle
                v-show="selectedLayer['name'] != 'poi'"
                v-model="toggleSelection"
              >
                <v-tooltip top>
                  <template v-slot:activator="{ on }">
                    <v-btn v-on="on" text>
                      <v-icon>far fa-dot-circle</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.drawCircle") }}</span>
                </v-tooltip>
                <v-tooltip top>
                  <template v-slot:activator="{ on }">
                    <v-btn v-on="on" text v-show="false">
                      <v-icon>far fa-hand-pointer</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.selectOnMap") }}</span>
                </v-tooltip>
              </v-btn-toggle>
            </v-flex>

            <span v-show="selectedLayer != null" class="py-1 mb-0 pl-0 ml-0">
              <h4>{{ $t("appBar.edit.editTools") }}</h4>
            </span>

            <v-flex
              xs12
              v-show="selectEditVisible && selectedLayer != null"
              class="mt-1 pt-0 mb-3"
            >
              <v-btn-toggle v-model="toggleEdit">
                <v-tooltip top>
                  <template v-slot:activator="{ on }">
                    <v-btn :value="1" v-on="on" text>
                      <v-icon medium>add</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.drawFeatureTooltip") }}</span>
                </v-tooltip>

                <v-tooltip
                  v-show="selectedLayer['canModifyGeom'] !== false"
                  top
                >
                  <template v-slot:activator="{ on }">
                    <v-btn
                      v-show="selectedLayer['canModifyGeom'] !== false"
                      :value="2"
                      v-on="on"
                      text
                    >
                      <v-icon>far fa-edit</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.modifyFeatureTooltip") }}</span>
                </v-tooltip>

                <v-tooltip top>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      :value="3"
                      v-show="selectedLayer['modifyAttributes'] === true"
                      v-on="on"
                      text
                    >
                      <v-icon>far fa-list-alt</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.modifyAttributes") }}</span>
                </v-tooltip>

                <v-tooltip top>
                  <template v-slot:activator="{ on }">
                    <v-btn :value="4" v-on="on" text>
                      <v-icon>far fa-trash-alt</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.deleteFeature") }}</span>
                </v-tooltip>

                <v-tooltip
                  top
                  v-show="
                    !['Point'].some(r =>
                      selectedLayer['editGeometry'].includes(r)
                    )
                  "
                >
                  <template v-slot:activator="{ on }">
                    <v-btn
                      v-show="
                        !['Point', 'LineString'].some(r =>
                          selectedLayer['editGeometry'].includes(r)
                        )
                      "
                      :value="5"
                      v-on="on"
                      text
                    >
                      <v-icon>far fa-clone</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.moveFeature") }}</span>
                </v-tooltip>
                <v-tooltip top>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      :value="6"
                      v-show="
                        !['Point', 'LineString'].some(r =>
                          selectedLayer['editGeometry'].includes(r)
                        )
                      "
                      v-on="on"
                      text
                    >
                      <v-icon>far fa-object-group</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.drawPolygonHole") }}</span>
                </v-tooltip>
              </v-btn-toggle>
              <br />

              <v-btn-toggle v-model="toggleEdit">
                <v-tooltip v-if="selectedLayer['name'] === 'building'" top>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      class="ml-0 mr-2 mt-2"
                      v-if="selectedLayer['name'] === 'building'"
                      :value="7"
                      v-on="on"
                      text
                    >
                      <v-icon>far fa-building</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.addBldEntrance") }}</span>
                </v-tooltip>
              </v-btn-toggle>

              <v-btn-toggle v-model="toggleSnapGuide">
                <v-tooltip
                  top
                  v-if="
                    ['Polygon', 'MultiPolygon'].some(r =>
                      selectedLayer['editGeometry'].includes(r)
                    )
                  "
                >
                  <template v-slot:activator="{ on }">
                    <v-btn class="ml-0 mt-2" v-on="on" text>
                      <v-icon>fas fa-border-all</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.snapGuide") }}</span>
                </v-tooltip>
              </v-btn-toggle>

              <v-btn-toggle v-model="toggleFeatureLabels">
                <v-tooltip
                  top
                  v-if="
                    ['Polygon', 'MultiPolygon'].some(r =>
                      selectedLayer['editGeometry'].includes(r)
                    )
                  "
                >
                  <template v-slot:activator="{ on }">
                    <v-btn class="ml-2 mt-2" v-on="on" text>
                      <v-icon>fas fa-font</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ $t("appBar.edit.featureLabels") }}</span>
                </v-tooltip>
              </v-btn-toggle>
            </v-flex>
          </div>
          <v-divider></v-divider>
          <!-- ==== </EDIT> ==== -->
        </template>

        <template v-if="activeScenario && selectedLayer && schema[layerName]">
          <!-- ==== <DATA TABLE> ====-->
          <v-subheader
            class="clickable ml-0 pl-0"
            @click="dataTableElVisible = !dataTableElVisible"
          >
            <v-icon
              :style="
                dataTableElVisible === true ? { color: appColor.secondary } : {}
              "
              small
              class="mr-2"
              >far fa-list-alt</v-icon
            >
            <h3>{{ $t("appBar.edit.scenarioFeatures") }}</h3>
            <v-spacer></v-spacer>
            <v-icon
              v-html="dataTableElVisible === true ? 'remove' : 'add'"
            ></v-icon>
          </v-subheader>
          <div class="ml-2" v-if="dataTableElVisible">
            <v-expand-transition>
              <v-flex xs12 class="mt-1 pt-0 mb-0">
                <v-data-table
                  :headers="headers"
                  :loading="isTableLoading"
                  :items="scenarioDataTable"
                  :items-per-page="15"
                  class="elevation-0"
                >
                  <template v-slot:item.status="{ item }">
                    <v-chip
                      small
                      :color="
                        item.status === 'uploaded' ? appColor.primary : 'error'
                      "
                      dark
                      class="mx-0 px-1"
                      >{{ $t(`appBar.edit.status.${item.status}`) }}</v-chip
                    >
                  </template>
                  <template v-slot:item.type="{ item }">
                    <span>{{ $t(`appBar.edit.type.${item.type}`) }}</span>
                  </template>

                  <template v-slot:item.action="{ item }">
                    <!-- zoom to scenario feature -->
                    <v-tooltip top>
                      <template v-slot:activator="{ on }">
                        <v-icon
                          v-on="on"
                          :disabled="isUploadBusy"
                          class="scenario-icon"
                          @click="scenarioActionBtnHandler(item, 'zoom')"
                        >
                          zoom_out_map
                        </v-icon>
                      </template>
                      <span>{{ $t(`map.tooltips.zoomToFeature`) }}</span>
                    </v-tooltip>
                    <!-- delete scenario feature -->
                    <v-tooltip top>
                      <template v-slot:activator="{ on }">
                        <v-icon
                          v-show="isDeleteBtnVisible(item)"
                          class="scenario-icon-delete"
                          :disabled="isUploadBusy"
                          v-on="on"
                          @click="scenarioActionBtnHandler(item, 'delete')"
                        >
                          delete
                        </v-icon>
                      </template>
                      <span>{{ $t(`map.tooltips.deleteFeature`) }}</span>
                    </v-tooltip>
                    <v-tooltip top>
                      <template v-slot:activator="{ on }">
                        <v-icon
                          v-show="isRestoreBtnVisible(item)"
                          class="scenario-icon"
                          :disabled="isUploadBusy"
                          v-on="on"
                          @click="scenarioActionBtnHandler(item, 'restore')"
                        >
                          restore_from_trash
                        </v-icon>
                      </template>
                      <span>{{ $t(`map.tooltips.restoreFeature`) }}</span>
                    </v-tooltip>
                  </template>
                </v-data-table>
              </v-flex>
            </v-expand-transition>
          </div>
          <!-- ==== < /DATA TABLE> ====-->
        </template>
      </v-card>
      <!-- ----- -->
      <v-card-actions v-if="selectedLayer && schema[layerName]">
        <v-spacer></v-spacer>

        <v-hover v-slot="{ hover }">
          <v-btn
            v-show="selectedLayer"
            class="white--text"
            :color="hover ? 'error' : 'grey'"
            outlined
            :loading="isDeleteAllBusy"
            :disabled="scenarioDataTable.length === 0 || isUploadBusy"
            @click="deleteAll"
          >
            <v-icon left>delete</v-icon>{{ $t("appBar.edit.clearBtn") }}
          </v-btn>
        </v-hover>
      </v-card-actions>
    </v-card>

    <!-- Scenario dialog -->
    <scenario-dialog
      :visible="showScenarioDialog"
      :scenarioId="activeScenarioId"
      @close="
        showScenarioDialog = false;
        activeScenarioId = null;
      "
    ></scenario-dialog>
    <!-- Confirm Delete all  -->
    <confirm ref="confirm"></confirm>
    <!-- Popup overlay  -->
    <overlay-popup
      style="cursor: default;"
      :title="$t(`map.popup.${popup.title}`)"
      v-show="popup.isVisible"
      ref="popup"
    >
      <v-btn icon>
        <v-icon>close</v-icon>
      </v-btn>
      <template v-slot:close>
        <v-btn @click="closePopup()" icon>
          <v-icon>close</v-icon>
        </v-btn>
      </template>
      <template v-slot:body>
        <div v-if="popup.selectedInteraction === 'delete'">
          <b>{{ $t("appBar.edit.popup.deleteFeatureMsg") }}</b>
        </div>
        <div
          v-else-if="
            ['add', 'modifyAttributes'].includes(popup.selectedInteraction)
          "
        >
          <v-form ref="edit-form" v-model="formValid">
            <v-jsonschema-form
              style="width:260px;"
              v-if="schema[layerName] && popup && popup.isVisible"
              :schema="schema[layerName]"
              :model="dataObject"
              :key="jsonFormKey"
              :options="options"
            />
          </v-form>
        </div>
      </template>
      <template v-slot:actions>
        <template v-if="popup.selectedInteraction === 'delete'">
          <v-btn color="primary darken-1" @click="ok('delete')" text>{{
            $t("buttonLabels.yes")
          }}</v-btn>
          <v-btn color="grey" text @click="closePopup()">{{
            $t("buttonLabels.cancel")
          }}</v-btn>
        </template>
        <template
          v-else-if="
            ['add', 'modifyAttributes'].includes(popup.selectedInteraction)
          "
        >
          <v-btn
            color="primary darken-1"
            :disabled="formValid === false"
            @click="ok(popup.selectedInteraction)"
            text
            >{{ $t("buttonLabels.save") }}</v-btn
          >
          <v-btn color="grey" text @click="closePopup()">{{
            $t("buttonLabels.cancel")
          }}</v-btn>
        </template>
      </template>
    </overlay-popup>
  </v-flex>
</template>

<script>
import { EventBus } from "../../../EventBus";
import { Mapable } from "../../../mixins/Mapable";
import { KeyShortcuts } from "../../../mixins/KeyShortcuts";
import { InteractionsToggle } from "../../../mixins/InteractionsToggle";
import { Isochrones } from "../../../mixins/Isochrones";
import { mapFields } from "vuex-map-fields";
import { mapFeatureTypeProps } from "../../../utils/Layer";
import OlSelectController from "../../../controllers/OlSelectController";
import OlEditController from "../../../controllers/OlEditController";
import {
  bldEntrancePointsStyle,
  getEditStyle,
  getFeatureHighlightStyle
} from "../../../style/OlStyleDefs";
import OverlayPopup from "../../viewer/ol/controls/Overlay";
import ScenarioDialog from "../../core/ScenarioDialog";
import ApiService from "../../../services/api.service";
import axios from "axios";
import VJsonschemaForm from "../../other/dynamicForms/index";

import { geojsonToFeature, geometryToWKT } from "../../../utils/MapUtils";
import { mapGetters, mapMutations } from "vuex";
import { debounce } from "../../../utils/Helpers";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";
import VectorImageLayer from "ol/layer/VectorImage";
import { GET_SCENARIOS } from "../../../store/actions.type";

export default {
  components: {
    "overlay-popup": OverlayPopup,
    "scenario-dialog": ScenarioDialog,
    VJsonschemaForm
  },
  mixins: [InteractionsToggle, Mapable, KeyShortcuts, Isochrones],
  data: () => ({
    interactionType: "edit-interaction",
    selectedFeatures: [],
    editableLayers: [],
    toggleSelection: undefined,
    toggleEdit: undefined,
    toggleSnapGuide: 0, // Used for snap and other functionalities (Active by default).
    toggleFeatureLabels: 0,
    isUploadBusy: false,
    isDeleteAllBusy: false,
    //Popup configuration
    popup: {
      title: "",
      isVisible: false,
      el: null,
      selectedInteraction: null
    },
    //Edit form
    layerConf: {},
    schema: {},
    dataObject: {},
    formValid: false,
    //Others
    mapCursorTypeEnum: {
      add: "crosshair",
      modify: "pointer",
      delete: "pointer",
      select: "pointer",
      move: "auto",
      modifyAttributes: "pointer",
      addBldEntrance: "pointer",
      drawHole: "crosshair"
    },
    //Data table
    isTableLoading: false,
    //Scenario Dialog
    showScenarioDialog: false,
    activeScenarioId: null,

    editElVisible: true,
    dataManageElVisible: true,
    selectEditVisible: true,
    selectFeaturesVisible: true,
    dataTableElVisible: true,
    scenarioSpeedDialFab: false,
    // -------------------------
    // ------------------------
    olEditCtrl: null,
    olSelectCtrl: null,
    highlightLayer: null,
    tempBldEntranceFeature: null,
    featuresToCommit: [],
    // Cache for poi modified feature
    poiModifiedFeatures: [],
    jsonFormKey: 0
  }),
  watch: {
    activeScenario() {
      // Fetch all features from the scenario
      if (this.selectedLayer) {
        this.fetchScenarioLayerFeatures(this.selectedLayer["name"]);
      }

      if (!this.activeScenario) {
        this.clearAll();
        this.cleanPoiTreeNode();
        this.poisAoisLayer.setVisible(true);
        this.selectedLayer = null;
        this.calculationMode.active = "default";
      }
      if (this.activeScenario) {
        this.calculationMode.active = "scenario";
      }
      this.fetchScenarioLayerSchemas();
    },
    selectedLayer(value, oldValue) {
      if (this.olEditCtrl && value) {
        this.appConfig.app_ui.base_color.primary = this.scenarioLayerEditModeColor;
        this.olEditCtrl.selectedLayer = value;
        this.originIdName = this.original_id;
        this.stop();
        this.clearAll();
        if (value && value.name === "poi") {
          this.poisAoisLayer.setVisible(false);
        } else {
          this.cleanPoiTreeNode();
          this.poisAoisLayer.setVisible(true);
        }
        // Fetch features for the selected layer
        this.fetchScenarioLayerFeatures(this.selectedLayer["name"]);
      }

      if (!value && this.primaryColorBackup) {
        if (oldValue.name === "poi") {
          this.cleanPoiTreeNode();
          this.poisAoisLayer.setVisible(true);
          this.clearAll();
        }
        // Revert color theme
        this.appConfig.app_ui.base_color.primary = this.primaryColorBackup;
      }
    },
    toggleSelection: {
      handler(state, oldState) {
        if (state !== undefined) {
          this.olEditCtrl.removeInteraction();
          this.toggleEdit = undefined;
          if (oldState !== undefined) {
            this.olSelectCtrl.removeInteraction();
            EventBus.$emit("ol-interaction-stoped", this.interactionType);
            if (this.map.getTarget().style) {
              this.map.getTarget().style.cursor = "";
            }
          }
          this.toggleSelectInteraction(state);
        }
      }
    },
    toggleEdit: {
      handler(state, oldState) {
        this.olSelectCtrl.removeInteraction();
        this.toggleSelection = undefined;
        if (oldState !== undefined) {
          this.olEditCtrl.removeInteraction();
          EventBus.$emit("ol-interaction-stoped", this.interactionType);
          if (this.map.getTarget().style) {
            this.map.getTarget().style.cursor = "";
          }
        }
        if (state !== undefined) {
          this.toggleEditInteraction(state);
        }
      }
    },
    toggleSnapGuide(value) {
      this.toggleSnapGuideInteraction(value);
    },
    toggleFeatureLabels(value) {
      this.toggleFeatureLabelsInteraction(value);
    },
    dataObject: {
      immediate: true,
      async handler() {
        await this.$nextTick();
        if (this.$refs["edit-form"]) {
          this.$refs["edit-form"].validate();
        }
      },
      deep: true
    },
    selectedPoisOnlyKeys() {
      this.editLayer.getSource().changed();
    },
    "calculationMode.active": function() {
      this.editLayer.getSource().changed();
    },
    poisAois() {
      // Add remove features.
      if (this.selectedLayer && this.selectedLayer["name"] === "poi") {
        this.syncPoiFeatures();
      }
    }
  },
  mounted() {
    this.popup.el = this.$refs.popup;
  },
  methods: {
    syncPoiFeatures() {
      this.poisAoisLayer
        .getSource()
        .getFeatures()
        .forEach(feature => {
          if (
            !["MultiPolygon", "Polygon"].includes(
              feature.getGeometry().getType()
            )
          ) {
            const category = feature.get("category");
            const featureInEdit = this.editLayer
              .getSource()
              .getFeatureById(feature.get("id"));
            const isFeatureActive = this.poisAois[category];
            if (featureInEdit && !isFeatureActive) {
              this.editLayer.getSource().removeFeature(featureInEdit);
            } else if (!featureInEdit && isFeatureActive) {
              let isFeatureModified = false;
              this.poiModifiedFeatures.forEach(modifiedFeature => {
                if (modifiedFeature.get("uid") === feature.get("uid")) {
                  isFeatureModified = true;
                }
              });
              if (!isFeatureModified) {
                const clonedFeature = feature.clone();
                clonedFeature.setId(feature.get("id"));
                clonedFeature.set("layerName", "poi");
                this.editLayer.getSource().addFeature(clonedFeature);
              }
            }
          }
        });
    },
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      this.olSelectCtrl = new OlSelectController(this.map);
      this.olSelectCtrl.createSelectionLayer();
      // Initialize ol edit controller.
      this.olEditCtrl = new OlEditController(this.map);
      //Initialize ol select controller.
      this.createLayers();
      this.olEditCtrl.highlightSource = this.highlightLayer.getSource();
      this.olEditCtrl.popup = this.popup;
      //Initialize component layers
      this.setUpCtxMenu();
      this.toggleFeatureLabelsInteraction(this.toggleFeatureLabels);
    },

    /**
     * Creates layers
     */
    createLayers() {
      // Edit layer
      const editLayer = new VectorImageLayer({
        name: "Edit Layer",
        displayInLayerList: false,
        source: new VectorSource({ wrapX: false }),
        zIndex: 10,
        style: getEditStyle(),
        queryable: true
      });
      editLayer.getSource().on("changefeature", this.onFeatureChange);
      editLayer.getSource().on("change", this.onEditSourceChange);
      this.map.addLayer(editLayer);
      this.editLayer = editLayer;
      this.olEditCtrl.layer = editLayer;
      this.olEditCtrl.source = editLayer.getSource();
      // Highlight Layer
      const highlightLayer = new VectorLayer({
        displayInLayerList: false,
        source: new VectorSource({ wrapX: false }),
        zIndex: 10,
        style: getFeatureHighlightStyle()
      });
      this.map.addLayer(highlightLayer);
      this.highlightLayer = highlightLayer;
      // Building entrance layer
      const bldEntranceLayer = new VectorLayer({
        name: "bld_entrance_layer",
        displayInLayerList: false,
        source: new VectorSource({ wrapX: false }),
        zIndex: 100,
        queryable: false,
        style: bldEntrancePointsStyle()
      });
      this.olEditCtrl.bldEntranceLayer = bldEntranceLayer;
      this.bldEntranceLayer = bldEntranceLayer;
      bldEntranceLayer
        .getSource()
        .on("changefeature", this.onBldEntranceFeatureChange);
      this.map.addLayer(bldEntranceLayer);
    },
    /**
     * Get Layer attribute fields
     */
    fetchScenarioLayerSchemas() {
      this.scenarioLayersConfig.forEach(config => {
        const layerName = config.client_config.name;
        const propertiesConfig = config.properties;
        const props = [];
        const layerConfig = {
          listValues: {},
          hiddenProps: [
            "id",
            "way_id",
            "building_id",
            "uid",
            "building_modified_id",
            "geom",
            "class_id"
          ],
          enableFileUpload: config.client_config.enableFileUpload || false
        };

        Object.keys(propertiesConfig).forEach(key => {
          const columnConfig = {};
          columnConfig.column_name = key;
          if (key === "geom") {
            columnConfig.data_type = "USER-DEFINED";
          } else {
            columnConfig.data_type = propertiesConfig[key].type;
          }
          if (config.required && config.required.includes(key)) {
            columnConfig.is_nullable = "NO";
          } else {
            columnConfig.is_nullable = "YES";
          }
          props.push(columnConfig);
          // Check if it has enum values
          if (propertiesConfig[key].enum) {
            layerConfig.listValues[key] = {
              values: propertiesConfig[key].enum
            };
          }
          // For pois add all list from poiIcon
          if (key === "category" && ["poi"].includes(layerName)) {
            layerConfig.listValues[key] = {
              values: this.poiList
            };
          }
        });

        const jsonSchema = mapFeatureTypeProps(props, layerName, layerConfig);
        this.schema[layerName] = jsonSchema;
      });
      if (this.layerName) {
        this.updateReqFields(this.reqFields);
        this.$forceUpdate();
      }
    },
    /**
     * Fetch scenario features for a layer
     */
    fetchScenarioLayerFeatures(layer) {
      const requests = [];
      this.clearAll();
      if (!this.activeScenario) return;

      const modifiedFeaturesPromise = ApiService.get_(
        `/scenarios/${this.activeScenario}/${layer}_modified/features?return_type=geojson`
      );
      requests.push(modifiedFeaturesPromise);
      if (layer === "building") {
        const populationModifiedFeaturePromise = ApiService.get_(
          `/scenarios/${this.activeScenario}/population_modified/features?return_type=geojson`
        );
        requests.push(populationModifiedFeaturePromise);
      }
      this.isMapBusy = true;

      axios
        .all(requests)
        .then(
          axios.spread((modifiedLayer, population) => {
            [modifiedLayer, population].forEach((layerData, index) => {
              if (layerData) {
                const features = geojsonToFeature(layerData.data, {
                  dataProjection: "EPSG:4326",
                  featureProjection: "EPSG:3857"
                });

                if (index === 1 && layer === "building") {
                  layer = "population";
                  this.bldEntranceLayer.getSource().clear();
                  this.bldEntranceLayer.getSource().addFeatures(features);
                  return;
                }
                features.forEach(feature => {
                  feature.setId(`${layer}_${feature.getId()}`);
                  feature.set("layerName", layer);
                });
                this.editLayer.getSource().addFeatures(features);
                if (layer === "poi") {
                  this.poiModifiedFeatures = features;
                  this.turnOnAndLockPoiTreeNode(features, "add");
                }
              }
            });
            if (layer === "poi") {
              this.syncPoiFeatures();
            }
            this.onEditSourceChange();
          })
        )
        .catch(error => {
          throw new Error(error);
        })
        .finally(() => {
          this.isMapBusy = false;
        });
    },
    /**
     * When poi layer is selected check if category is already selected from user and lock it, if not select it first.
     */
    turnOnAndLockPoiTreeNode(features, type) {
      const uniqueCategories = [
        ...new Set(features.map(f => f.get("category")))
      ];
      uniqueCategories.forEach(category => {
        if (type == "add") {
          if (!this.selectedPoisOnlyKeys.includes(category)) {
            const poiNodeObj = this.poisTreeOnlyChildren[category];
            if (poiNodeObj) {
              poiNodeObj.isLocked = true;
              this.selectedPoisAois.push(this.poisTreeOnlyChildren[category]);
            }
          } else {
            this.selectedPoisAois.forEach(selectedPoi => {
              if (selectedPoi.value === category) {
                selectedPoi.isLocked = true;
              }
            });
          }
        }
        if (type === "unlock") {
          this.selectedPoisAois.forEach(selectedPoi => {
            if (selectedPoi.values === category) {
              selectedPoi.isLocked = false;
            }
          });
        }
      });
    },
    cleanPoiTreeNode() {
      this.selectedPoisAois.forEach(selectedPoi => {
        if (selectedPoi.isLocked) {
          selectedPoi.isLocked = false;
        }
      });
    },
    /**
     * Toggle the select interaction
     */
    toggleSelectInteraction(state) {
      if (state != undefined) {
        EventBus.$emit("ol-interaction-activated", this.interactionType);
        if (this.map.getTarget().style) {
          this.map.getTarget().style.cursor = this.mapCursorTypeEnum["select"];
        }
      } else {
        EventBus.$emit("ol-interaction-stoped", this.interactionType);
        if (this.map.getTarget().style) {
          this.map.getTarget().style.cursor = "";
        }
      }
      let selectionType;
      switch (state) {
        case 0:
          selectionType = "multiple";
          break;
        default:
          break;
      }
      if (selectionType !== undefined) {
        this.olSelectCtrl.addInteraction(
          selectionType,
          this.selectedLayer,
          this.onSelectionStart,
          this.onSelectionEnd
        );
        if (this.addKeyupListener) {
          this.addKeyupListener();
        }
      } else {
        this.olSelectCtrl.removeInteraction();
      }
    },
    /**
     * Callback function executed when selection interaction starts.
     */
    onSelectionStart() {
      this.clear();
    },
    /**
     * Callback function executed when selection interaction ends.
     *
     * @param  {ol/feature} features The features returned from selection interaction
     */
    onSelectionEnd(response) {
      this.toggleSelection = undefined;
      this.olSelectCtrl.removeInteraction();
      if (response) {
        const features = geojsonToFeature(response.data, {
          dataProjection: "EPSG:4326",
          featureProjection: "EPSG:3857"
        });
        features.forEach(feature => {
          feature.set("layerName", this.selectedLayer["name"]);
        });
        this.editLayer.getSource().addFeatures(features);
      }
    },

    /**
     * Toggle the edit interaction
     */
    toggleEditInteraction(state) {
      let editType, startCb, endCb;
      switch (state) {
        case 1:
          editType = "add";
          startCb = this.onDrawStart;
          endCb = this.onDrawEnd;
          break;
        case 2:
          editType = "modify";
          startCb = this.onModifyStart;
          endCb = this.onModifyEnd;
          break;
        case 3:
          editType = "modifyAttributes";
          startCb = this.openModifyAttributePopup;
          break;
        case 4:
          editType = "delete";
          endCb = this.openDeletePopup;
          break;
        case 5:
          editType = "move";
          startCb = this.onModifyStart;
          endCb = this.onModifyEnd;
          break;
        case 6:
          editType = "drawHole";
          startCb = this.onModifyStart;
          endCb = this.onModifyEnd;
          break;
        case 7:
          editType = "addBldEntrance";
          endCb = this.onBldEntranceInteractionEnd;
          break;
        default:
          break;
      }
      if (editType !== undefined) {
        this.olEditCtrl.addInteraction(editType, startCb, endCb);
        EventBus.$emit("ol-interaction-activated", this.interactionType);
        this.$nextTick(() => {
          if (this.map.getTarget().style) {
            this.map.getTarget().style.cursor = this.mapCursorTypeEnum[
              editType
            ];
          }
        });
        if (this.addKeyupListener) {
          this.addKeyupListener();
        }
        this.olEditCtrl.editType = editType;
      } else {
        this.olEditCtrl.editType = undefined;
        this.olEditCtrl.removeInteraction();
        EventBus.$emit("ol-interaction-stoped", this.interactionType);
        if (this.map.getTarget().style) {
          this.map.getTarget().style.cursor = "";
        }
      }
    },

    /**
     * Adds or remove snap interaction
     */
    toggleSnapGuideInteraction(state) {
      if (state === 0) {
        this.olEditCtrl.addSnapGuideInteraction();
        this.olEditCtrl.isSnapGuideActive = 1;
      } else {
        this.olEditCtrl.removeSnapGuideInteraction();
        this.olEditCtrl.isSnapGuideActive = 0;
      }
    },

    /**
     * Toggle Feature labels
     */

    toggleFeatureLabelsInteraction(state) {
      this.editLayer.set("showLabels", state);
      this.editLayer.getSource().changed();
    },

    /**
     * Open modify attribute popup
     */
    openModifyAttributePopup(evt) {
      const feature = this.editLayer
        .getSource()
        .getClosestFeatureToCoordinate(evt.coordinate);
      this.featuresToCommit = [];
      this.highlightLayer.getSource().clear();
      if (feature) {
        const props = feature.getProperties();
        this.$nextTick(() => {
          for (const attr in this.dataObject) {
            this.dataObject[attr] = attr in props ? props[attr] : null;
          }
          this.jsonFormKey += 1;
        });
        const geometry = feature.getGeometry();
        let popupCoordinate = geometry.getCoordinates();
        while (popupCoordinate && Array.isArray(popupCoordinate[0])) {
          popupCoordinate = popupCoordinate[0];
        }
        this.map.getView().animate({
          center: popupCoordinate,
          duration: 400
        });
        this.olEditCtrl.popupOverlay.setPosition(popupCoordinate);
        this.featuresToCommit.push(feature);
        this.highlightLayer.getSource().addFeature(feature.clone());
        this.popup.title = "modifyAttributes";
        this.popup.selectedInteraction = "modifyAttributes";
        this.popup.isVisible = true;
      }
    },
    /**
     * Opens a popup for the delete confirmation
     */
    openDeletePopup(evt) {
      let feature;
      if (evt.coordinate) {
        const coordinate = evt.coordinate;
        feature = this.editLayer
          .getSource()
          .getClosestFeatureToCoordinate(coordinate);
      } else {
        //Triggered when user click scenario data table
        //Create overlayer
        this.olEditCtrl.createPopupOverlay();
        feature = evt;
      }

      this.highlightLayer.getSource().addFeature(feature.clone());
      this.featuresToCommit.push(feature);
      if (feature) {
        const geometry = feature.getGeometry();
        let popupCoordinate = geometry.getCoordinates();
        while (popupCoordinate && Array.isArray(popupCoordinate[0])) {
          popupCoordinate = popupCoordinate[0];
        }
        this.map.getView().animate({
          center: popupCoordinate,
          duration: 400
        });
        this.olEditCtrl.popupOverlay.setPosition(popupCoordinate);
        this.popup.title = "confirm";
        this.popup.selectedInteraction = "delete";
        this.popup.isVisible = true;
      }
    },

    /**
     * Modify interaction start event handler
     */
    onModifyStart() {
      this.featuresToCommit = [];
      this.olEditCtrl.isInteractionOnProgress = true;
    },
    /**
     * Modify interaction end event handler
     */
    onModifyEnd() {
      this.olEditCtrl.isInteractionOnProgress = false;
      this.clearDataObject();
      const featuresToAdd = [];
      const featuresToUpdate = [];
      this.featuresToCommit.forEach(feature => {
        const featureOut = this.setFeatureFields(feature);
        const props = feature.getProperties();
        if (props.editType !== "d") {
          if (props.hasOwnProperty("edit_type")) {
            featureOut.setId(feature.getId());
            featuresToUpdate.push(featureOut);
          } else {
            Object.keys(featureOut.getProperties()).forEach(prop => {
              if (!["edit_type", this.original_id, "geometry"].includes(prop)) {
                featureOut.set(prop, feature.get(prop));
              }
            });
            featureOut.set("edit_type", "m");
            featureOut.set(
              this.original_id,
              feature.get("uid") || feature.get("id")
            );
            featuresToAdd.push(featureOut);
          }
        }
      });
      this.createScenarioFeatures(featuresToAdd);
      this.updateScenarioFeatures(featuresToUpdate);
    },
    /**
     * Draw interaction start event handler
     */
    onDrawStart() {
      this.featuresToCommit = [];
    },
    /**
     * Draw interaction start event handler
     */
    onDrawEnd(evt) {
      const feature = evt.feature;
      this.editLayer.getSource().addFeature(feature);
      this.clearDataObject();
      //Disable interaction until user fills the attributes for the feature and closes the popup
      if (this.olEditCtrl.edit) {
        this.olEditCtrl.edit.setActive(false);
      }
      this.featuresToCommit.push(feature);
      this.highlightLayer.getSource().addFeature(feature.clone());
      let popupCoordinate = feature.getGeometry().getCoordinates();
      while (popupCoordinate && Array.isArray(popupCoordinate[0])) {
        popupCoordinate = popupCoordinate[0];
      }
      this.map.getView().animate({
        center: popupCoordinate,
        duration: 400
      });
      this.olEditCtrl.popupOverlay.setPosition(popupCoordinate);
      this.popup.title = "attributes";
      this.popup.selectedInteraction = "add";
      this.popup.isVisible = true;
    },
    setFeatureFields(feature) {
      const props = feature.getProperties();
      const featureOut = feature.clone();
      const mandatoryProps = [
        ...Object.keys(this.dataObject),
        "edit_type",
        this.original_id,
        "geometry",
        "geom"
      ];
      Object.keys(props).forEach(prop => {
        if (!mandatoryProps.includes(prop)) featureOut.unset(prop);
      });
      return featureOut;
    },

    /**
     * Building Entrance interaction end.
     */
    onBldEntranceInteractionEnd(evt) {
      let coordinate;
      if (evt.type === "modifyend") {
        if (!this.tempBldEntranceFeature) return;
        coordinate = this.tempBldEntranceFeature.getGeometry().getCoordinates();
      } else {
        coordinate = evt.feature.getGeometry().getCoordinates();
      }

      let buildingFeatureAtCoord;
      if (evt.type === "modifyend") {
        buildingFeatureAtCoord = this.olEditCtrl.source.getClosestFeatureToCoordinate(
          coordinate,
          candidate => {
            if (
              ((candidate.get("id") || candidate.getId()) &&
                this.tempBldEntranceFeature &&
                this.tempBldEntranceFeature.get("building_modified_id") ===
                  candidate.get("id")) ||
              this.tempBldEntranceFeature.get("building_modified_id") ===
                candidate.get("id") ||
              this.tempBldEntranceFeature.get("building_modified_id") ===
                candidate.getId()
            ) {
              return true;
            } else {
              return false;
            }
          }
        );
      } else {
        buildingFeatureAtCoord = this.olEditCtrl.source.getClosestFeatureToCoordinate(
          coordinate
        );
      }

      if (!buildingFeatureAtCoord && !buildingFeatureAtCoord.getId()) return;

      // This line restricts drawing entrance feature only in new drawn buildings (original_id is used as an identifier)
      if (
        !buildingFeatureAtCoord.getProperties().hasOwnProperty(this.original_id)
      ) {
        return;
      }

      let bldEntranceCoordinate;
      if (
        buildingFeatureAtCoord.getGeometry().intersectsCoordinate(coordinate)
      ) {
        bldEntranceCoordinate = coordinate;
      } else {
        const closestPoint = buildingFeatureAtCoord
          .getGeometry()
          .getClosestPoint(coordinate);
        bldEntranceCoordinate = closestPoint;
        if (this.tempBldEntranceFeature && evt.type === "modifyend") {
          this.tempBldEntranceFeature.setGeometry(
            new Point(bldEntranceCoordinate)
          );
        }
      }
      let bldEntranceFeature;
      if (evt.type === "modifyend") {
        // Update the existing building entrance feature
        bldEntranceFeature = this.tempBldEntranceFeature;

        // Can't update the feature if id isn't available
        if (!bldEntranceFeature.getId()) return;

        // Clone feature and transform for transaction.
        const {
          // eslint-disable-next-line no-unused-vars
          geometry,
          // eslint-disable-next-line no-unused-vars
          geom,
          ...propsWithNoGeometry
        } = bldEntranceFeature.getProperties();
        const clonedFeature = new Feature({
          geom: bldEntranceFeature.getGeometry().clone(),
          ...propsWithNoGeometry
        });
        clonedFeature.setGeometryName("geom");
        ApiService.put(
          `/scenarios/${this.activeScenario}/population_modified/features`,
          {
            features: [
              {
                id: bldEntranceFeature.getId(),
                geom: geometryToWKT(
                  clonedFeature
                    .getGeometry()
                    .clone()
                    .transform("EPSG:3857", "EPSG:4326")
                )
              }
            ]
          }
        ).then(response => {
          if (response.data) {
            const feature = geojsonToFeature(response.data);
            if (feature[0] && feature[0].get("id")) {
              bldEntranceFeature.setId(feature[0].get("id"));
            }
          }
        });
      } else {
        // Add new feature
        bldEntranceFeature = new Feature({
          geometry: new Point(bldEntranceCoordinate),
          building_modified_id:
            buildingFeatureAtCoord.get("id") ||
            buildingFeatureAtCoord.get("id") ||
            buildingFeatureAtCoord.getId()
        });
        this.olEditCtrl.bldEntranceLayer
          .getSource()
          .addFeature(bldEntranceFeature);

        // Clone feature and transform for transaction.
        const {
          // eslint-disable-next-line no-unused-vars
          geometry,
          // eslint-disable-next-line no-unused-vars
          geom,
          ...propsWithNoGeometry
        } = bldEntranceFeature.getProperties();
        const clonedFeature = new Feature({
          geom: new Point(bldEntranceCoordinate),
          ...propsWithNoGeometry
        });
        clonedFeature.setGeometryName("geom");
        ApiService.post(
          `/scenarios/${this.activeScenario}/population_modified/features`,
          {
            features: [
              {
                ...clonedFeature.getProperties(),
                geom: geometryToWKT(
                  clonedFeature
                    .getGeometry()
                    .clone()
                    .transform("EPSG:3857", "EPSG:4326")
                )
              }
            ]
          }
        ).then(response => {
          if (response.data) {
            const feature = geojsonToFeature(response.data);
            this.editLayer.getSource().changed();
            if (feature[0] && feature[0].get("id")) {
              bldEntranceFeature.setId(feature[0].get("id"));
            }
          }
        });
      }

      setTimeout(() => {
        this.tempBldEntranceFeature = null;
      }, 100);
    },
    /**
     * Feature change event handler for building entrance edit layer
     */
    onBldEntranceFeatureChange(evt) {
      if (evt.feature) {
        // Used on modifyEnd event.
        this.tempBldEntranceFeature = evt.feature;
      }
    },
    /**
     * Configure right-click for Edit.
     */
    setUpCtxMenu() {
      if (this.contextmenu) {
        this.olEditCtrl.contextmenu = this.contextmenu;
        this.contextmenu.on("beforeopen", evt => {
          // Close helptoltip
          if (this.olEditCtrl.helpTooltip) {
            this.olEditCtrl.helpTooltip.setPosition(undefined);
          }
          const features = this.map.getFeaturesAtPixel(evt.pixel, {
            layerFilter: candidate => {
              if (candidate.get("name") === "bld_entrance_layer") {
                return true;
              }
              return false;
            }
          });
          if (
            features.length > 0 &&
            this.selectedLayer["name"] === "building"
          ) {
            this.contextmenu.extend([
              "-", // this is a separator
              {
                text: `<i class="fa fa-trash fa-1x" aria-hidden="true"></i>&nbsp;&nbsp${this.$t(
                  "map.contextMenu.deleteBldEntrancePoint"
                )}`,
                label: "deleteBldEntrancePoint",
                callback: () => {
                  ApiService.delete(
                    `/scenarios/${
                      this.activeScenario
                    }/population_modified/features?id=${features[0].getId()}`
                  ).then(response => {
                    if (response.data) {
                      this.olEditCtrl.bldEntranceLayer
                        .getSource()
                        .removeFeature(features[0]);
                      this.editLayer.getSource().changed();
                    }
                  });
                }
              }
            ]);
          }
        });
      }
    },
    /**
     * Feature change event handler for edit layer
     */
    onFeatureChange(evt) {
      if (
        ["modify", "move", "modifyAttributes", "drawHole"].includes(
          this.olEditCtrl.editType
        )
      ) {
        const index = this.featuresToCommit.findIndex(
          i => i.ol_uid === evt.feature.ol_uid
        );
        if (index === -1) {
          this.featuresToCommit.push(evt.feature);
        } else {
          this.featuresToCommit[index] = evt.feature;
        }
      }
    },
    /**
     * Source change base event. Used to update scenario data table
     * This event is called very often, so for performance improvement a
     * debounce method  is used in updateDatatable
     */
    onEditSourceChange() {
      this.isTableLoading = true;
      this.updateDataTable();
    },

    /**
     * Method called when edit layer source is changed.
     * A debounce is addes to improve performance
     * It updates the scenario data table.
     */
    updateDataTable: debounce(function() {
      if (!this.activeScenario) return;
      const editLayerFeatures = this.editLayer.getSource().getFeatures();
      const scenarioDataTable = [];
      editLayerFeatures.forEach(f => {
        const fid = f.getId();
        const layerName = f.get("layerName");
        let isDeleted = false;
        let status = "uploaded";
        let type = "";
        let originId;
        if (f.get("edit_type")) {
          const editType = f.get("edit_type");
          if (editType === "n") {
            type = "new";
          } else if (editType === "d") {
            type = "deleted";
            isDeleted = true;
            originId = f.get(this.original_id);
          } else if (editType === "m") {
            type = "modified";
            originId = f.get(this.original_id);
          }
          const obj = {
            fid,
            layerName,
            isDeleted,
            originId,
            status,
            type
          };
          scenarioDataTable.push(obj);
        }
      });
      this.scenarioDataTable = scenarioDataTable;
      this.isTableLoading = false;
    }, 900),

    scenarioActionBtnHandler(item, type) {
      const fid = item.fid;
      if (!fid) return;
      let feature;
      feature = this.editLayer.getSource().getFeatureById(fid);
      if (!feature) return;
      if (type === "zoom") {
        this.map.getView().fit(feature.getGeometry().getExtent(), {
          padding: [10, 10, 10, 10]
        });
        this.highlightLayer.getSource().addFeature(feature);
        setTimeout(() => {
          this.highlightLayer.getSource().removeFeature(feature);
        }, 300);
      } else if (type === "delete") {
        this.openDeletePopup(feature);
      } else if (type === "restore") {
        this.map.getView().fit(feature.getGeometry().getExtent(), {
          padding: [10, 10, 10, 10]
        });
        this.deleteScenarioFeatures([feature]);
      }
    },
    isRestoreBtnVisible(item) {
      if (item.type !== "deleted" || !this.selectedLayer) {
        return false;
      }
      return item.isDeleted;
    },
    isDeleteBtnVisible(item) {
      if ((!item.originalId && item.isDeleted) || !this.selectedLayer) {
        return false;
      }
      return !item.isDeleted;
    },

    /**
     * Clear data object that user has entered,
     * so the next time the popup is opened the form is clean.
     */
    clearDataObject() {
      if (!this.layerName) return;
      const properties = this.schema[this.layerName].properties;
      const dataObject = {};
      Object.keys(properties).forEach(key => {
        if (properties[key] && properties[key]["x-display"] !== "hidden") {
          dataObject[key] = null;
          this.dataObject = dataObject;
        }
      });
    },

    /**
     * Closes the popup if user choose cancel.
     */
    closePopup() {
      if (this.olEditCtrl.popupOverlay) {
        this.olEditCtrl.popupOverlay.setPosition(undefined);
        this.popup.isVisible = false;
      }
      if (this.olEditCtrl.edit) {
        this.olEditCtrl.edit.setActive(true);
      }
      this.highlightLayer.getSource().clear();
      if (this.interactionType === "draw") {
        this.featuresToCommit.forEach(feature => {
          if (this.editLayer.getSource().hasFeature(feature)) {
            this.editLayer.getSource().removeFeature(feature);
          }
        });
      }
      // Removes features that are not modified

      this.editLayer
        .getSource()
        .getFeatures()
        .forEach(feature => {
          if (
            !feature.get("edit_type") &&
            feature.get("layerName") !== "poi" &&
            !feature.get("building_modified_id") // building_modified_id is edge case to not clean population_modified features as they don't have an edit_type property
          ) {
            this.editLayer.getSource().removeFeature(feature);
          }
        });

      this.featuresToCommit = [];
    },
    /**
     * Clears all the selection and edit interactions.
     */
    clear() {
      // Removes features that are not modified
      this.editLayer
        .getSource()
        .getFeatures()
        .forEach(feature => {
          if (
            !feature.get("edit_type") &&
            feature.get("layerName") !== "poi" &&
            !feature.get("building_modified_id") // building_modified_id is edge case to not clean population_modified features as they don't have an edit_type property
          ) {
            this.editLayer.getSource().removeFeature(feature);
          }
        });
      EventBus.$emit("ol-interaction-stoped", this.interactionType);
      this.clearDataObject();
      if (this.contextmenu) {
        this.contextmenu.close();
      }
      this.featuresToCommit = [];
    },

    /**
     * Clears all the features from edit layer (triggered when user changes scenario)
     */
    clearAll() {
      this.olEditCtrl.clear();
      this.olSelectCtrl.clear();
      this.editLayer.getSource().clear();
      this.highlightLayer.getSource().clear();
      this.bldEntranceLayer.getSource().clear();
      if (this.contextmenu) {
        this.contextmenu.close();
      }
      this.clearDataObject();
      this.scenarioDataTable = [];
      this.isInteractionOnProgress = false;
      this.isTableLoading = false;
      this.featuresToCommit = [];
      EventBus.$emit("ol-interaction-stoped", this.interactionType);
    },
    /**
     * Delete all user scenario features in db.
     */
    deleteAll() {
      this.$refs.confirm
        .open(
          this.$t("appBar.edit.deleteAllTitle"),
          this.$t("appBar.edit.deleteAllMessage"),
          { color: this.appColor.primary }
        )

        .then(confirm => {
          if (confirm) {
            //1- Call api to delete all features.
            this.isDeleteAllBusy = true;
            ApiService.delete(
              `/scenarios/${this.activeScenario}/${this.selectedLayer["name"]}_modified/features-all`
            )
              .then(response => {
                this.isDeleteAllBusy = false;
                this.isUploadBtnEnabled = true;
                if (response.data === "error") {
                  //Show error message can't delete
                  this.toggleSnackbar({
                    type: "error", //success or error
                    message: this.$t(
                      `map.snackbarMessages.cantDeleteAllScenarioFeatures`
                    ),
                    state: true,
                    timeout: 4000
                  });
                } else {
                  //Show success message
                  this.toggleSnackbar({
                    type: this.appColor.primary, //success or error
                    message: this.$t(
                      `map.snackbarMessages.allScenarioFeaturesDelete`
                    ),
                    state: true,
                    timeout: 4000
                  });
                  // Clear openlayers scenario features
                  this.stop();
                  if (this.selectedLayer["name"] === "poi") {
                    this.fetchScenarioLayerFeatures("poi");
                  } else {
                    this.clearAll();
                  }
                }
              })
              .catch(() => {
                this.isDeleteAllBusy = false;
              });
          }
        });
    },
    /**
     * Delete scenario
     */
    deleteScenario() {
      this.$refs.confirm
        .open(
          this.$t("appBar.edit.deleteAllTitle"),
          this.$t("appBar.edit.confirmDeleteScenario"),
          { color: this.appColor.primary }
        )

        .then(confirm => {
          if (confirm) {
            ApiService.delete(`/scenarios/${this.activeScenario}`).then(
              response => {
                if (response.data === "error") {
                  //Show error message can't delete
                  this.toggleSnackbar({
                    type: "error", //success or error
                    message: this.$t("map.snackbarMessages.cantDeleteScenario"),
                    state: true,
                    timeout: 3000
                  });
                } else {
                  //Show success message
                  this.toggleSnackbar({
                    type: this.appColor.primary, //success or error
                    message: this.$t("map.snackbarMessages.scenarioDeleted"),
                    state: true,
                    timeout: 3000
                  });

                  //- Refetch Scenario
                  this.$store.dispatch(`scenarios/${GET_SCENARIOS}`);
                  //- Clear openlayers scenario features
                  this.clearAll();
                  this.selectedLayer = null;
                  this.activeScenario = null;
                }
              }
            );
          }
        })
        .catch(() => {
          this.toggleSnackbar({
            type: "error", //success or error
            message: this.$t("map.snackbarMessages.cantDeleteScenario"),
            state: true,
            timeout: 3000
          });
        });
    },
    /**
     * Stop edit and select interactions (Doesn't deletes the features)
     */
    stop() {
      this.closePopup();
      this.olSelectCtrl.removeInteraction();
      this.olEditCtrl.removeInteraction();
      EventBus.$emit("ol-interaction-stoped", this.interactionType);
      this.toggleSelection = undefined;
      this.toggleEdit = undefined;
      if (this.map.getTarget().style) {
        this.map.getTarget().style.cursor = "";
      }
      this.clear();
    },
    /**
     * Translate method to avoid inline html logic
     */
    translate(type, key) {
      //type = {layerGroup || layerName}
      //Checks if key exists and translates it othewise return the input value
      const canTranslate = this.$te(`map.${type}.${key}`);
      if (canTranslate) {
        return this.$t(`map.${type}.${key}`);
      } else {
        return key;
      }
    },
    /**
     * Method used on popup save (draw)/ok(delete) depending on interaction type
     */
    ok(type) {
      const featureOut = this.featuresToCommit[0].clone();
      // Reset id of the original feature
      featureOut.setId(this.featuresToCommit[0].getId());
      const properties = this.featuresToCommit[0].getProperties();
      if (type === "add") {
        // New feature
        featureOut.setProperties(this.dataObject);
        featureOut.set("edit_type", "n");
        this.createScenarioFeatures([featureOut]);
      }
      if (type === "modifyAttributes") {
        // Modified existing feature
        const featureOut = this.setFeatureFields(this.featuresToCommit[0]);
        featureOut.setProperties(this.dataObject);
        const props = this.featuresToCommit[0].getProperties();
        if (props.editType !== "d") {
          if (props.hasOwnProperty("edit_type")) {
            featureOut.setId(this.featuresToCommit[0].getId());
            this.updateScenarioFeatures([featureOut]);
          } else {
            featureOut.set("edit_type", "m");
            featureOut.set(
              this.original_id,
              this.featuresToCommit[0].get("uid") ||
                this.featuresToCommit[0].get("id")
            );
            this.createScenarioFeatures([featureOut]);
            this.editLayer.getSource().removeFeature(this.featuresToCommit[0]);
          }
        }
      } else if (type === "delete" && !properties.hasOwnProperty("edit_type")) {
        // Deleted an origin feature (has to be created as deleted feature)
        const allowedKeys = Object.keys(this.dataObject);
        Object.keys(this.featuresToCommit[0].getProperties()).forEach(prop => {
          if (!allowedKeys.includes(prop) && prop !== "geometry") {
            featureOut.unset(prop);
          }
        });
        if (this.featuresToCommit[0].get("id")) {
          const original_id_ =
            this.featuresToCommit[0].get("uid") ||
            this.featuresToCommit[0].get("id");
          featureOut.set(this.original_id, original_id_);
        }
        featureOut.set("edit_type", "d");
        this.createScenarioFeatures([featureOut]);
        this.editLayer.getSource().removeFeature(this.featuresToCommit[0]);
      } else if (type === "delete") {
        // Deleted a feature which is already modified. Delete from "_modified" layer
        this.deleteScenarioFeatures([featureOut]);
      }
      if (this.olEditCtrl.popupOverlay) {
        this.olEditCtrl.popupOverlay.setPosition(undefined);
        this.popup.isVisible = false;
      }
      if (this.olEditCtrl.edit) {
        this.olEditCtrl.edit.setActive(true);
      }
      this.highlightLayer.getSource().clear();
    },

    /**
     * ====API CALLS====
     */
    /**
     * Create scenario features
     */
    createScenarioFeatures(features) {
      if (features.length === 0) return;
      let payload = features.map(feature => {
        const transformed = {
          ...feature.getProperties(),
          geom: geometryToWKT(
            feature
              .getGeometry()
              .clone()
              .transform("EPSG:3857", "EPSG:4326")
          )
        };
        delete transformed.geometry;
        return transformed;
      });
      this.isMapBusy = true;
      ApiService.post(this.scenarioApiBaseUrl, {
        features: payload
      })
        .then(response => {
          // TODO: Don't remove features from featuresToCommit (Too late here. We should get the features from cloned features)
          this.featuresToCommit.forEach(feature => {
            if (this.editLayer.getSource().hasFeature(feature)) {
              this.editLayer.getSource().removeFeature(feature);
            }
          });
          const featuresWithId = geojsonToFeature(response.data, {
            dataProjection: "EPSG:4326",
            featureProjection: "EPSG:3857"
          });
          featuresWithId.forEach(feature => {
            feature.setId(`${this.selectedLayer["name"]}_${feature.getId()}`);
            feature.set("layerName", this.selectedLayer["name"]);
          });
          if (this.selectedLayer["name"] === "poi") {
            this.turnOnAndLockPoiTreeNode(featuresWithId, "add");
            this.poiModifiedFeatures.push(...featuresWithId);
          }
          this.editLayer.getSource().addFeatures(featuresWithId);
          this.refreshHeatmap();
          // Activate building entrance interaction if selected layer is building
          if (
            this.selectedLayer["name"] === "building" &&
            this.olEditCtrl.editType === "add"
          ) {
            this.toggleEdit = 7;
          }
        })
        .catch(error => {
          console.log(error);
          this.toggleSnackbar({
            type: "error", //success or error
            message: this.$t(`appBar.edit.cantCreateScenarioFeature`),
            state: true,
            timeout: 3000
          });
          this.featuresToCommit.forEach(feature => {
            if (this.editLayer.getSource().hasFeature(feature)) {
              this.editLayer.getSource().removeFeature(feature);
            }
          });
        })
        .finally(() => {
          this.isMapBusy = false;
          this.featuresToCommit = [];
        });
    },
    /**
     * Update scenario features
     */
    updateScenarioFeatures(features) {
      if (features.length === 0) return;
      let payload = features.map(feature => {
        const transformed = {
          id: parseInt(feature.getId().split("_")[1]),
          ...feature.getProperties(),
          geom: geometryToWKT(
            feature
              .getGeometry()
              .clone()
              .transform("EPSG:3857", "EPSG:4326")
          )
        };
        delete transformed.edit_type;
        delete transformed.geometry;
        delete transformed[this.original_id];
        return transformed;
      });
      this.isMapBusy = true;
      ApiService.put(this.scenarioApiBaseUrl, {
        features: payload
      })
        .then(response => {
          features.forEach(feature => {
            const featureIn = this.editLayer
              .getSource()
              .getFeatureById(feature.getId());
            if (featureIn) {
              this.editLayer.getSource().removeFeature(featureIn);
            }
          });
          const featuresWithId = geojsonToFeature(response.data, {
            dataProjection: "EPSG:4326",
            featureProjection: "EPSG:3857"
          });
          featuresWithId.forEach(feature => {
            feature.setId(`${this.selectedLayer["name"]}_${feature.getId()}`);
            feature.set("layerName", this.selectedLayer["name"]);
          });
          this.editLayer.getSource().addFeatures(featuresWithId);
          this.refreshHeatmap();
        })
        .catch(() => {
          this.toggleSnackbar({
            type: "error", //success or error
            message: this.$t(`appBar.edit.canNotUpdateScenarioFeature`),
            state: true,
            timeout: 3000
          });
          features.forEach(feature => {
            if (this.editLayer.getSource().hasFeature(feature)) {
              this.editLayer.getSource().removeFeature(feature);
            }
          });
        })
        .finally(() => {
          this.isMapBusy = false;
          this.featuresToCommit = [];
        });
    },
    /**
     * Delete scenario features
     */
    deleteScenarioFeatures(features) {
      let queryParam = "";
      if (features.length === 1) {
        queryParam += `id=${parseInt(features[0].getId().split("_")[1])}`;
      } else {
        features.forEach((feature, index) => {
          const id = parseInt(feature.getId().split("_")[1]);
          if (id && index !== features - 1) {
            queryParam += `id=${id}&`;
          } else if (id) {
            queryParam += `id=${id}`;
          }
        });
      }
      this.isMapBusy = true;
      ApiService.delete(`${this.scenarioApiBaseUrl}?${queryParam}`)
        .then(() => {
          // For pois if there is no modified features, we need to unlock the tree node.
          features.forEach(feature => {
            if (feature.getId()) {
              const featureIn = this.editLayer
                .getSource()
                .getFeatureById(feature.getId());
              if (featureIn) {
                const props = featureIn.getProperties();
                if (["m", "d"].includes(props.edit_type)) {
                  featureIn.unset("edit_type");
                  if (this.selectedLayer["name"] === "poi") {
                    // Find origin feature and add it here
                    const originFeature = this.poisAoisLayer
                      .getSource()
                      .getFeatures()
                      .filter(f => f.get("uid") === featureIn.get("uid"));
                    if (
                      Array.isArray(originFeature) &&
                      originFeature.length > 0
                    ) {
                      const clonedFeature = originFeature[0].clone();
                      clonedFeature.setId(originFeature[0].get("id"));
                      clonedFeature.set("layerName", "poi");
                      this.editLayer.getSource().addFeature(clonedFeature);
                    }
                    // Delete feature from pois modified features array
                    this.poiModifiedFeatures.forEach(f => {
                      if (f.get("uid") === featureIn.get("uid")) {
                        this.poiModifiedFeatures.splice(
                          this.poiModifiedFeatures.indexOf(f),
                          1
                        );
                      }
                    });
                  }
                }
                if (
                  this.selectedLayer["name"] === "building" &&
                  featureIn.get("id")
                ) {
                  // Delete all bldEntrance features on the same building
                  const bldEntranceFeatures = this.bldEntranceLayer
                    .getSource()
                    .getFeatures()
                    .filter(
                      f => f.get("building_modified_id") === featureIn.get("id")
                    );
                  bldEntranceFeatures.forEach(f => {
                    this.bldEntranceLayer.getSource().removeFeature(f);
                  });
                }

                this.editLayer.getSource().removeFeature(featureIn);
              }
            }
          });
          this.refreshHeatmap();
        })
        .catch(() => {
          this.toggleSnackbar({
            type: "error", //success or error
            message: this.$t(`appBar.edit.canNotDeleteScenarioFeature`),
            state: true,
            timeout: 3000
          });
        })
        .finally(() => {
          this.isMapBusy = false;
          this.featuresToCommit = [];
        });
    },
    refreshHeatmap() {
      if (this.selectedLayer["name"]) {
        EventBus.$emit("update-heatmap", "poi");
      }
      if (this.selectedLayer["building"]) {
        // TODO: Update only when building population is added
        EventBus.$emit("update-heatmap", "population");
      }
    },
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR",
      updateReqFields: "UPDATE_REQ_FIELDS",
      setBldEntranceLayer: "SET_BLD_ENTRANCE_LAYER",
      setEditLayer: "SET_EDIT_LAYER"
    })
  },
  computed: {
    headers() {
      return [
        {
          text: this.$t("appBar.edit.table.layer"),
          value: "layerName",
          sortable: false,
          align: "center",
          width: "20%"
        },
        {
          text: this.$t("appBar.edit.table.status"),
          value: "status",
          sortable: false,
          align: "center",
          width: "25%"
        },
        {
          text: this.$t("appBar.edit.table.type"),
          value: "type",
          sortable: false,
          align: "center",
          width: "25%"
        },
        {
          text: this.$t("appBar.edit.table.actions"),
          value: "action",
          sortable: false,
          align: "center",
          width: "25%"
        }
      ];
    },
    scenarioLayersConfig() {
      const schemas = this.openapiConfig.components.schemas;
      const scenarioLayersConfig = [
        schemas.ScenarioPoisModifiedCreate,
        schemas.ScenarioWaysModifiedCreate,
        schemas.ScenarioBuildingsModifiedCreate
      ];
      return scenarioLayersConfig;
    },
    layerName() {
      let value;
      if (this.selectedLayer) {
        value = this.selectedLayer["name"];
      } else {
        value = "";
      }
      return value;
    },
    reqFields() {
      const layerSchema = this.schema[this.layerName];
      const layerFieldsKeys = Object.keys(layerSchema.properties);
      return layerFieldsKeys.filter(
        el =>
          ![
            "way_id",
            "uid",
            "building_modified_id",
            "building_id",
            "id",
            "scenario_id"
          ].includes(el) && layerSchema.required.includes(el)
      );
    },
    options() {
      return {
        debug: false,
        disableAll: false,
        autoFoldObjects: true
      };
    },
    original_id() {
      if (!this.selectedLayer) return "";
      if (this.selectedLayer["name"] === "poi") {
        return "uid";
      } else if (this.selectedLayer["name"] === "building") {
        return "building_id";
      } else if (this.selectedLayer["name"] === "way") {
        return "way_id";
      } else {
        return "";
      }
    },
    poiList() {
      return Object.keys(this.poiIcons).filter(
        poiName => !!this.poisConfig[poiName]
      );
    },
    scenarioApiBaseUrl() {
      return `/scenarios/${this.activeScenario}/${this.selectedLayer["name"]}_modified/features`;
    },
    ...mapGetters("auth", { currentUser: "currentUser" }),
    ...mapGetters("app", {
      appColor: "appColor",
      calculationMode: "calculationMode",
      openapiConfig: "openapiConfig",
      poiIcons: "poiIcons",
      poisConfig: "poisConfig",
      poisTreeOnlyChildren: "poisTreeOnlyChildren",
      scenarioLayerEditModeColor: "scenarioLayerEditModeColor"
    }),
    ...mapGetters("map", {
      contextmenu: "contextmenu",
      layers: "layers"
    }),
    ...mapGetters("poisaois", {
      poisAoisLayer: "poisAoisLayer",
      poisAois: "poisAois",
      selectedPoisOnlyKeys: "selectedPoisOnlyKeys"
    }),
    ...mapFields("poisaois", {
      selectedPoisAois: "selectedPoisAois"
    }),
    ...mapFields("scenarios", {
      scenarioDataTable: "scenarioDataTable",
      scenarios: "scenarios",
      activeScenario: "activeScenario"
    }),
    scenarioList() {
      return [
        { id: null, scenario_name: this.$t("appBar.edit.noSelection") },
        ...this.scenarios
      ];
    },
    ...mapGetters("scenarios", {
      activeScenarioObj: "activeScenarioObj"
    }),
    ...mapFields("map", {
      selectedLayer: "selectedEditLayer",
      isMapBusy: "isMapBusy",
      editLayer: "editLayer",
      bldEntranceLayer: "bldEntranceLayer"
    }),
    ...mapFields("app", {
      appConfig: "appConfig",
      calculationMode: "calculationMode"
    })
  },
  created() {
    const editableLayers = [];
    this.scenarioLayersConfig.forEach(config => {
      editableLayers.push(config.client_config);
    });
    this.editableLayers = editableLayers;
    this.fetchScenarioLayerSchemas();
    this.primaryColorBackup = this.appConfig.app_ui.base_color.primary;
  }
};
</script>
<style scoped>
.scenario-icon:hover {
  cursor: pointer;
  color: #30c2ff;
}
.scenario-icon-delete:hover {
  cursor: pointer;
  color: red;
}

.create-scenario-text {
  display: block;
  width: 150px;
  word-wrap: break-word;
  overflow-wrap: break-word;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
