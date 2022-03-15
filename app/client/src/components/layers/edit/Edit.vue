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
        <div v-if="Object.keys(scenarios).length === 0">
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
        <div v-if="Object.keys(scenarios).length > 0">
          <v-row class="mt-4" no-gutters>
            <v-col class="text-center" :cols="8">
              <v-select
                v-model="activeScenario"
                :items="scenarioArray"
                item-text="display"
                item-value="value"
                label="Select scenario"
                solo
              >
                <template
                  class="create-scenario-text"
                  slot="selection"
                  slot-scope="{ item }"
                >
                  {{ item.display }}
                </template>
                <template
                  class="create-scenario-text"
                  slot="item"
                  slot-scope="{ item }"
                >
                  {{ item.display }}
                </template>
              </v-select>
            </v-col>
            <v-col class="text-center ml-0 pl-0">
              <v-tooltip top>
                <template v-slot:activator="{ on }">
                  <v-btn
                    v-on="on"
                    class="mt-1 ml-2"
                    :color="appColor.primary"
                    fab
                    dark
                    small
                    @click="showScenarioDialog = true"
                  >
                    <v-icon dark>add</v-icon>
                  </v-btn>
                </template>
                <span>{{ $t("appBar.edit.createScenario") }}</span></v-tooltip
              >
            </v-col>
            <v-col v-if="activeScenario" class="text-center">
              <v-tooltip top>
                <template v-slot:activator="{ on }">
                  <v-btn
                    v-on="on"
                    class="mt-1 ml-1"
                    :color="appColor.primary"
                    fab
                    dark
                    small
                    @click="
                      showScenarioDialog = true;
                      activeScenarioId = activeScenario;
                    "
                  >
                    <v-icon dark>edit</v-icon>
                  </v-btn>
                </template>
                <span>{{ $t("appBar.edit.editScenarioName") }}</span></v-tooltip
              >
            </v-col>
          </v-row>
        </div>

        <div v-if="Object.keys(scenarios).length > 0">
          <v-divider></v-divider>
          <v-subheader class="ml-0 pl-0 mb-0 pb-0">
            <v-icon style="color:#30c2ff;" small class="mr-2"
              >fas fa-layer-group</v-icon
            >
            <h3>{{ $t("appBar.edit.selectLayer") }}</h3>
          </v-subheader>
          <v-select
            class="mt-4"
            :items="editableLayers"
            v-model="selectedLayer"
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

        <v-alert
          border="left"
          colored-border
          class="mb-2 mt-0 mx-0 elevation-2"
          icon="warning"
          color="warning"
          dense
          v-if="
            selectedLayer &&
              selectedLayer['displayInLayerList'] &&
              selectedLayer['name'] === 'poi'
          "
        >
          <span v-html="$t('appBar.edit.activateLayerToDrawScenario')"></span>
        </v-alert>
        <template v-if="selectedLayer && schema[layerName]">
          <v-divider></v-divider>
          <!-- ==== <EDIT> ====-->

          <v-subheader
            v-show="selectedLayer !== null"
            class="clickable ml-0 pl-0"
            @click="editElVisible = !editElVisible"
          >
            <v-icon
              :style="editElVisible === true ? { color: '#30c2ff' } : {}"
              small
              class="mr-2"
              >fas fa-edit</v-icon
            >
            <h3>{{ $t("appBar.edit.editTools") }}</h3>
          </v-subheader>
          <div class="ml-2" v-if="editElVisible">
            <span
              v-show="selectedLayer != null"
              class="py-1 mb-0 mt-3 pl-0 ml-0"
            >
              <h4>{{ $t("appBar.edit.selectFeatures") }}</h4>
            </span>

            <v-flex
              xs12
              v-show="selectedLayer != null && selectFeaturesVisible"
              class="mt-1 pt-0 mb-4"
            >
              <v-btn-toggle v-model="toggleSelection">
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

          <!-- ==== <DATA TABLE> ====-->
          <v-subheader
            v-show="selectedLayer !== null"
            class="clickable ml-0 pl-0"
            @click="dataTableElVisible = !dataTableElVisible"
          >
            <v-icon
              :style="dataTableElVisible === true ? { color: '#30c2ff' } : {}"
              small
              class="mr-2"
              >far fa-list-alt</v-icon
            >
            <h3>{{ $t("appBar.edit.scenarioFeatures") }}</h3>
          </v-subheader>
          <div class="ml-2" v-if="dataTableElVisible">
            <v-expand-transition>
              <v-flex
                v-if="dataTableElVisible && selectedLayer !== null"
                xs12
                class="mt-1 pt-0 mb-0"
              >
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
                      :color="item.status === 'Uploaded' ? 'success' : 'error'"
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

      <!-- ADD ENTRANCES FOR BUILDINGS ALERT -->
      <br />
      <v-alert
        border="left"
        colored-border
        class="mb-2 mt-0 mx-3 elevation-2"
        icon="info"
        color="warning"
        dense
        v-if="
          isUploadBtnEnabled === false &&
            selectedLayer &&
            selectedLayer['name'] === 'building' &&
            olEditCtrl.source.getFeatures().length > 0
        "
      >
        <span v-html="$t('appBar.edit.addEntrancesForBuildings')"></span>
      </v-alert>
      <!-- ----- -->
      <v-card-actions v-if="selectedLayer && schema[layerName]">
        <v-spacer></v-spacer>

        <v-btn
          v-show="selectedLayer != null"
          class="white--text"
          v-if="!isUploadBusy"
          :disabled="
            (this.busyLayers && this.busyLayers.length > 0) ||
              isDeleteAllBusy ||
              (isUploadBtnEnabled === false &&
                selectedLayer &&
                selectedLayer['name'] === 'building' &&
                olEditCtrl.source.getFeatures().length > 0)
          "
          :color="appColor.primary"
          @click="uploadFeatures"
        >
          <v-icon left>cloud_upload</v-icon>{{ $t("appBar.edit.uploadBtn") }}
        </v-btn>

        <v-btn
          v-else
          class="white--text"
          @click.stop="stopUpload"
          color="error"
        >
          <v-icon color="white">close</v-icon>Stop Upload
        </v-btn>

        <v-btn
          v-show="selectedLayer != null"
          class="white--text"
          color="error"
          :loading="isDeleteAllBusy"
          :disabled="scenarioDataTable.length === 0 || isUploadBusy"
          @click="deleteAll"
        >
          <v-icon left>delete</v-icon>{{ $t("appBar.edit.clearBtn") }}
        </v-btn>
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
      :title="popup.title"
      v-show="popup.isVisible"
      ref="popup"
    >
      <v-btn icon>
        <v-icon>close</v-icon>
      </v-btn>
      <template v-slot:close>
        <v-btn
          @click="
            popup.selectedInteraction === 'modifyAttributes'
              ? cancelAttributeEdit()
              : cancel()
          "
          icon
        >
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
              v-if="schema[layerName]"
              :schema="schema[layerName]"
              :model="dataObject"
              :options="options"
              @input="e => inputFn(e)"
            />
          </v-form>
        </div>
      </template>
      <template v-slot:actions>
        <template v-if="popup.selectedInteraction === 'delete'">
          <v-btn color="primary darken-1" @click="ok('delete')" text>{{
            $t("buttonLabels.yes")
          }}</v-btn>
          <v-btn color="grey" text @click="cancel()">{{
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
          <v-btn
            color="grey"
            text
            @click="
              popup.selectedInteraction === 'modifyAttributes'
                ? cancelAttributeEdit()
                : cancel()
            "
            >{{ $t("buttonLabels.cancel") }}</v-btn
          >
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
import OlEditController from "../../../controllers/OlEditController";
import OlSelectController from "../../../controllers/OlSelectController";
import editLayerHelper from "../../../controllers/OlEditLayerHelper";

import OverlayPopup from "../../viewer/ol/controls/Overlay";
import ScenarioDialog from "../../core/ScenarioDialog";
import ApiService from "../../../services/api.service";
import VJsonschemaForm from "../../other/dynamicForms/index";

import { geojsonToFeature, geometryToWKT } from "../../../utils/MapUtils";
import { mapGetters, mapMutations } from "vuex";
import { debounce } from "../../../utils/Helpers";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";

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
    isExportScenarioBusy: false,
    //Popup configuration
    popup: {
      title: "",
      isVisible: false,
      el: null,
      selectedInteraction: null
    },
    //Upload field.
    file: null,
    uploadRules: [
      value =>
        !value || value.size < 1000000 || "File size should be less than 1 MB!"
    ],
    fileInputFeaturesCache: [],
    fileInputValidationMessageEnum: {
      FILE_VALID_OR_NO_FILE: "fileValidOrNoFile",
      DIFFERENT_GEOMETRY_TYPE: "differentGeometryType",
      MISSING_FIELDS: "missingFields",
      FILE_CORRUPTED: "fileCorrupted",
      ALL_FEATURES_UPLOADED: "allFeaturesUploaded",
      NOT_ALL_UPLOADED: "notAllUploaded",
      ERROR_HAPPENED: "errorHappened"
    },
    fileInputValidationTypeEnum: {
      allFeaturesUploaded: "success",
      notAllUploaded: "warning",
      errorHappened: "error",
      differentGeometryType: "error",
      missingFields: "error",
      fileCorrupted: "error"
    },

    fileInputValidationMessage: "fileValidOrNoFile",
    missingFieldsNames: "",
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
    //Opening Hours
    showOpeningHours: false,
    isUploadBtnEnabled: true,
    //Scenario Dialog
    showScenarioDialog: false,
    activeScenarioId: null,

    editElVisible: true,
    dataManageElVisible: true,
    scenarioImpExpVisible: false,
    selectEditVisible: true,
    selectFeaturesVisible: true,
    dataTableElVisible: true,
    // Feature storage layers.
    editLayerStorageLayer: [],
    bldEntranceStorageLayer: []
  }),
  watch: {
    selectedLayer(newValue) {
      this.updateSelectedLayer(newValue);
    },
    activeScenario() {
      /** For edit layer */
      //1- Store the features in the storage layer. ()
      this.olEditCtrl.source.getFeatures().forEach(feature => {
        if (!this.olEditCtrl.storageLayer.getSource().hasFeature(feature)) {
          this.olEditCtrl.storageLayer.getSource().addFeature(feature);
        }
      });
      //2- Clear edit layer
      this.olEditCtrl.source.clear();
      //3- Copy the active scenario features in source;
      const editFeaturesInActiveScenario = this.olEditCtrl.storageLayer
        .getSource()
        .getFeatures()
        .filter(f => f.get("scenario_id") === this.activeScenario);
      this.olEditCtrl.source.addFeatures(editFeaturesInActiveScenario);

      /** For building entrance layer */
      //1- Store the features in the storage layer. ()
      this.olEditCtrl.bldEntranceLayer
        .getSource()
        .getFeatures()
        .forEach(feature => {
          if (
            !this.olEditCtrl.bldEntranceStorageLayer
              .getSource()
              .hasFeature(feature)
          ) {
            this.olEditCtrl.bldEntranceStorageLayer
              .getSource()
              .addFeature(feature);
          }
        });
      //2- Clear bld entrance layer
      this.olEditCtrl.bldEntranceLayer.getSource().clear();
      //3- Copy active scenario features in bld entrance layer;
      const bldEntranceFeaturesInActiveScenario = this.olEditCtrl.bldEntranceStorageLayer
        .getSource()
        .getFeatures()
        .filter(f => f.get("scenario_id") === this.activeScenario);
      this.olEditCtrl.bldEntranceLayer
        .getSource()
        .addFeatures(bldEntranceFeaturesInActiveScenario);

      //**//
      this.onEditSourceChange();
      this.olEditCtrl.source.changed();
      this.olEditCtrl.bldEntranceLayer.getSource().changed();
      if (editLayerHelper.selectedLayer) {
        this.updateSelectedLayer(editLayerHelper.selectedLayer);
      }
    },
    toggleSelection: {
      handler(state) {
        const me = this;
        me.toggleSelectInteraction(state);
      }
    },
    toggleEdit: {
      handler(state) {
        const me = this;
        me.toggleEditInteraction(state);
      }
    },
    toggleSnapGuide(value) {
      this.toggleSnapGuideInteraction(value);
    },
    toggleFeatureLabels(value) {
      this.toggleFeatureLabelsInteraction(value);
    },
    scenarioDataTable() {
      this.canCalculateScenario(this.calculationMode.active);
    },
    "calculationMode.active": function(value) {
      this.canCalculateScenario(value);
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
    }
  },
  mounted() {
    const me = this;
    me.popup.el = me.$refs.popup;
    me.olEditCtrl.referencePopupElement(me.popup);
  },
  methods: {
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      const me = this;
      //Initialize ol select controllers.
      me.olSelectCtrl = new OlSelectController(me.map);
      me.olSelectCtrl.createSelectionLayer();
      //Initialize ol edit controller
      me.olEditCtrl = new OlEditController(me.map);
      me.olEditCtrl.createEditLayer(
        this.onFeatureChange,
        this.onEditSourceChange
      );
      me.olEditCtrl.createBldEntranceLayer(
        this.onBldEntranceFeatureChange,
        this.onBldEntranceSourceChange
      );
      me.setBldEntranceLayer(me.olEditCtrl.bldEntranceLayer);
      me.setEditLayer(me.olEditCtrl.layer);
      this.setUpCtxMenu();
      this.toggleFeatureLabelsInteraction(this.toggleFeatureLabels);
    },

    /**
     * Toggle the select interaction
     */
    toggleSelectInteraction(state) {
      const me = this;
      //Close other interactions.
      if (state != undefined) {
        EventBus.$emit("ol-interaction-activated", me.interactionType);
        me.map.getTarget().style.cursor = this.mapCursorTypeEnum["select"];
      } else {
        EventBus.$emit("ol-interaction-stoped", me.interactionType);
        me.map.getTarget().style.cursor = "";
      }
      let selectionType;
      switch (state) {
        case 0:
          selectionType = "multiple";
          break;
        case 1:
          selectionType = "single";
          break;
        default:
          break;
      }
      if (selectionType !== undefined) {
        me.clearSelection();
        me.olSelectCtrl.addInteraction(
          selectionType,
          me.selectedLayer,
          me.onSelectionStart,
          me.onSelectionEnd
        );
        if (this.addKeyupListener) {
          this.addKeyupListener();
        }
      } else {
        me.olSelectCtrl.removeInteraction();
      }
    },
    /**
     * Toggle the edit interaction
     */
    toggleEditInteraction(state) {
      const me = this;
      //Remove select interaction
      me.olSelectCtrl.removeInteraction();
      me.toggleSelection = undefined;
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
        me.olEditCtrl.addInteraction(editType, startCb, endCb);
        EventBus.$emit("ol-interaction-activated", me.interactionType);
        setTimeout(() => {
          me.map.getTarget().style.cursor = this.mapCursorTypeEnum[editType];
        }, 50);
        if (this.addKeyupListener) {
          this.addKeyupListener();
        }
      } else {
        me.olEditCtrl.removeInteraction();
        EventBus.$emit("ol-interaction-stoped", me.interactionType);
        me.map.getTarget().style.cursor = "";
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
      this.olEditCtrl.layer.set("showLabels", state);
      this.olEditCtrl.layer.getSource().changed();
    },

    /**
     * Callback function executed when selection interaction starts.
     */
    onSelectionStart() {
      const me = this;
      me.olEditCtrl.clear();
    },
    /**
     * Callback function executed when selection interaction ends.
     *
     * @param  {ol/feature} features The features returned from selection interaction
     */
    onSelectionEnd(response) {
      const me = this;
      me.toggleSelection = undefined;
      if (response.second) {
        editLayerHelper.filterResults(
          response,
          me.olEditCtrl.getLayerSource(),
          me.olEditCtrl.bldEntranceLayer,
          me.olEditCtrl.storageLayer.getSource()
        );
      }
    },

    /**
     * Open modify attribute popup
     */
    openModifyAttributePopup(evt) {
      const feature = this.olEditCtrl.source.getClosestFeatureToCoordinate(
        evt.coordinate
      );
      this.olEditCtrl.featuresToCommit = [];
      this.olEditCtrl.highlightSource.clear();
      if (feature) {
        const props = feature.getProperties();
        for (const attr in this.dataObject) {
          this.dataObject[attr] = attr in props ? props[attr] : null;
        }
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
        this.olEditCtrl.featuresToCommit.push(feature);
        this.olEditCtrl.highlightSource.addFeature(feature.clone());
        this.olEditCtrl.popup.title = "modifyAttributes";
        this.olEditCtrl.popup.selectedInteraction = "modifyAttributes";
        this.olEditCtrl.popup.isVisible = true;
      }
    },

    /**
     * Modify interaction start event handler
     */
    onModifyStart() {
      this.olEditCtrl.featuresToCommit = [];
      this.olEditCtrl.isInteractionOnProgress = true;
    },
    /**
     * Modify interaction end event handler
     */
    onModifyEnd() {
      this.olEditCtrl.isInteractionOnProgress = false;
      let props = {};
      Object.keys(this.schema[this.layerName].properties).forEach(key => {
        props[key] = null;
      });
      this.olEditCtrl.transact(props);

      this.olEditCtrl.featuresToCommit.forEach(feature => {
        feature.set("status", null);
      });
      //update cache
      this.updateFileInputFeatureCache();
    },
    /**
     * Draw interaction start event handler
     */
    onDrawStart() {
      this.olEditCtrl.featuresToCommit = [];
    },
    /**
     * Draw interaction start event handler
     */
    onDrawEnd(evt) {
      const feature = evt.feature;
      this.olEditCtrl.closePopup();
      this.clearDataObject();
      //Disable interaction until user fills the attributes for the feature and closes the popup
      if (this.olEditCtrl.edit) {
        this.olEditCtrl.edit.setActive(false);
      }
      this.olEditCtrl.featuresToCommit.push(feature);
      this.olEditCtrl.highlightSource.addFeature(feature);
      let popupCoordinate = feature.getGeometry().getCoordinates();
      while (popupCoordinate && Array.isArray(popupCoordinate[0])) {
        popupCoordinate = popupCoordinate[0];
      }
      this.map.getView().animate({
        center: popupCoordinate,
        duration: 400
      });
      this.olEditCtrl.popupOverlay.setPosition(popupCoordinate);
      this.olEditCtrl.popup.title = "attributes";
      this.olEditCtrl.popup.selectedInteraction = "add";
      this.olEditCtrl.popup.isVisible = true;
      //update cache
      this.updateFileInputFeatureCache();
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

      // Update Building upload state
      if (buildingFeatureAtCoord) {
        buildingFeatureAtCoord.set("status", null);
      }

      let payload = {
        features: []
      };

      let mode = "";
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
        clonedFeature.getGeometry().transform("EPSG:3857", "EPSG:4326");
        clonedFeature.setId(bldEntranceFeature.getId());
        // Prepare payload for update
        const props = clonedFeature.getProperties();
        if (props.hasOwnProperty("geom")) {
          delete props.geom;
        }
        const wktGeom = geometryToWKT(clonedFeature.getGeometry());
        props.geom = wktGeom;
        props.id =
          clonedFeature.getId() ||
          clonedFeature.get("id") ||
          clonedFeature.get("id");
        payload.features = [props];
        mode = "update";
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
        clonedFeature.getGeometry().transform("EPSG:3857", "EPSG:4326");

        // Prepare payload for insert

        const props = clonedFeature.getProperties();
        if (props.hasOwnProperty("geom")) {
          delete props.geom;
        }
        if (props.hasOwnProperty("id")) {
          delete props.id;
        }
        const wktGeom = geometryToWKT(clonedFeature.getGeometry());
        props.geom = wktGeom;
        payload.features = [props];
        mode = "insert";
      }
      let promise = "";
      if (mode === "update") {
        promise = ApiService.put(
          `/scenarios/${this.activeScenario}/population_modified/features`,
          payload
        );
      } else {
        promise = ApiService.post(
          `/scenarios/${this.activeScenario}/population_modified/features`,
          payload
        );
      }
      promise.then(response => {
        if (response.data) {
          const feature = geojsonToFeature(response.data);
          if (feature[0] && feature[0].get("id")) {
            bldEntranceFeature.setId(feature[0].get("id"));
          }
        }
      });
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
     * Source change base event. Used to update upload button state
     * This event is called very often, so for performance improvement a
     * debounce method  is used on updateUploadBtnState
     */
    onBldEntranceSourceChange() {
      this.updateUploadBtnState();
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
              if (candidate.get("name") === "Building Entrance Edit Layer") {
                return true;
              }
              return false;
            }
          });
          if (features.length > 0) {
            this.contextmenu.extend([
              "-", // this is a separator
              {
                text: `<i class="fa fa-trash fa-1x" aria-hidden="true"></i>&nbsp;&nbsp${this.$t(
                  "map.contextMenu.deleteBldEntrancePoint"
                )}`,
                label: "deleteBldEntrancePoint",
                callback: () => {
                  this.olEditCtrl.deleteBldEntranceFeatures(features);
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
      const me = this;
      //Exclude features from file input as we add this feature later when user click upload button
      //  if (evt.feature.get("user_uploaded")) return;
      if (
        ["modify", "move", "modifyAttributes", "drawHole"].includes(
          me.olEditCtrl.currentInteraction
        )
      ) {
        const index = me.olEditCtrl.featuresToCommit.findIndex(
          i => i.ol_uid === evt.feature.ol_uid
        );
        if (index === -1) {
          me.olEditCtrl.featuresToCommit.push(evt.feature);
        } else {
          me.olEditCtrl.featuresToCommit[index] = evt.feature;
        }
      }

      /** For pois layer features are "uploaded" (inserted in db) automatically */
      if (["poi"].includes(evt.feature.get("layerName"))) {
        evt.feature.set("status", 1);
      }

      if (
        this.selectedLayer["name"] === "building" &&
        this.olEditCtrl.currentInteraction === "draw"
      ) {
        this.toggleEdit = 7;
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
      this.updateUploadBtnState();
    },
    /**
     * Clear data object that user has entered,
     * so the next time the popup is opened the form is clean.
     */
    clearDataObject() {
      if (this.dataObject) {
        for (const key of Object.keys(this.dataObject)) {
          this.dataObject[key] = null;
        }
      }
    },
    /**
     * Get Layer attribute fields
     */
    getlayerFeatureTypes() {
      const schemas = this.openapiConfig.components.schemas;
      const scenarioLayersConfig = [
        schemas.ScenarioPoisModifiedCreate,
        schemas.ScenarioWaysModifiedCreate,
        schemas.ScenarioBuildingsModifiedCreate
      ];
      const editableLayers = [];
      scenarioLayersConfig.forEach(config => {
        editableLayers.push(config.client_config);
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
          columnConfig.data_type = propertiesConfig[key].type;
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
          if (key === "amenity" && ["poi"].includes(layerName)) {
            layerConfig.listValues[key] = {
              values: Object.keys(this.poiIcons)
            };
          }
        });

        const jsonSchema = mapFeatureTypeProps(props, layerName, layerConfig);
        this.schema[layerName] = jsonSchema;
      });
      console.log(this.schema);

      this.editableLayers = editableLayers;
      this.updateReqFields(this.reqFields);
      this.$forceUpdate();
    },
    /**
     * Method used only on drawend or modifyend to update fileinput feature cache
     */
    updateFileInputFeatureCache() {
      //Update fileInputFeatureCache (we can't use a computed property since it will affect the performance)
      //Check if user has already inputed a file
      if (this.file) {
        const uploadedFeatures = this.olEditCtrl.source
          .getFeatures()
          .filter(feature => {
            return feature.get("user_uploaded");
          });
        this.fileInputFeaturesCache = uploadedFeatures;
      }
    },
    /**
     * Method called to update data when layer or scenario is changed.
     */
    updateSelectedLayer(newValue) {
      const me = this;
      //Read or Insert deleted features
      me.clear();
      editLayerHelper.selectedLayer = newValue;
      me.getlayerFeatureTypes();
      me.olEditCtrl.readOrInsertDeletedFeatures();
      me.olEditCtrl.dataObject = this.dataObject;
      if (newValue["name"] === "building") {
        this.isUploadBtnEnabled = false;
      } else {
        this.isUploadBtnEnabled = true;
      }
      this.updateUploadBtnState();
    },
    /**
     * Clears all the selection
     */
    clearSelection() {
      const me = this;
      me.olEditCtrl.clear();
      me.olSelectCtrl.clear();
    },
    /**
     * Upload drawn and modidified features for scenario calculations
     */
    uploadFeatures() {
      //If there are file input feature commit those in db as well.
      this.isUploadBusy = true;
      this.olEditCtrl.uploadFeatures(state => {
        if (state === "success") {
          EventBus.$emit("updateAllLayers");
        }
        this.isUploadBusy = false;
        this.toggleSnackbar({
          type: state, //success or error
          message:
            state === "success"
              ? "uploadScenarioSuccess"
              : "uploadScenarioError",
          state: true,
          timeout: 4000
        });
        this.olEditCtrl.source.changed();
      });
    },
    scenarioActionBtnHandler(item, type) {
      const fid = item.fid;
      if (!fid) return;
      let feature;

      if (item.type === "deleted") {
        feature = editLayerHelper.deletedFeatures.filter(
          f => f.getId() === fid
        );
        feature.length > 0 ? (feature = feature[0]) : null;
      } else {
        feature = this.olEditCtrl.source.getFeatureById(fid);
      }

      if (!feature) return;

      if (type === "zoom") {
        this.map.getView().fit(feature.getGeometry().getExtent(), {
          padding: [10, 10, 10, 10]
        });
        this.olEditCtrl.highlightSource.addFeature(feature);
        setTimeout(() => {
          this.olEditCtrl.highlightSource.removeFeature(feature);
        }, 300);
      } else if (type === "delete") {
        this.olEditCtrl.openDeletePopup(feature);
      } else if (type === "restore") {
        const clonedFeature = feature.clone();
        clonedFeature.setId(feature.getId());
        clonedFeature.set("deletedId", feature.getId());

        //If the deleted feature is not uploaded in the server consider it uploaded in client side
        if (item.status === "NotUploaded") {
          clonedFeature.set("status", 1);
        } else {
          clonedFeature.set("status", null);
        }

        this.map.getView().fit(feature.getGeometry().getExtent(), {
          padding: [10, 10, 10, 10]
        });
        editLayerHelper.deletedFeatures = editLayerHelper.deletedFeatures.filter(
          f => f.getId() !== fid
        );
        this.olEditCtrl.highlightSource.addFeature(feature);
        setTimeout(() => {
          this.olEditCtrl.highlightSource.removeFeature(feature);
        }, 300);
        editLayerHelper.featuresIDsToDelete = editLayerHelper.featuresIDsToDelete.filter(
          id => feature.getProperties().id.toString() !== id
        );
        this.olEditCtrl.source.addFeature(clonedFeature);
        //Commit restore changes. ("commitDelete" just updates array of deleted features ids in the database)
        editLayerHelper.commitDelete("update_deleted_features");
      }
    },
    /**
     * Stop Upload button
     */
    stopUpload() {
      if (editLayerHelper.cancelReq instanceof Function) {
        editLayerHelper.cancelReq("cancelled");
      }
    },
    /**
     * Clears  edit interaction
     */
    clearEdit() {
      const me = this;
      me.olEditCtrl.clear();
    },
    /**
     * Clears all the selection and edit interactions.
     */
    clear() {
      const me = this;
      me.clearSelection();
      me.clearEdit();
      me.toggleSelection = undefined;
      me.toggleEdit = undefined;
      EventBus.$emit("ol-interaction-stoped", me.interactionType);
    },
    /**
     * Delete all user scenario features in db.
     */
    deleteAll() {
      const layerName = [this.selectedLayer["name"]];
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
              `/scenarios/${this.activeScenario}/${layerName}_modified/features`
            )
              .then(response => {
                this.isDeleteAllBusy = false;
                this.isUploadBtnEnabled = true;
                if (response.data === "error") {
                  //Show error message can't delete
                  this.toggleSnackbar({
                    type: "error", //success or error
                    message: "cantDeleteAllScenarioFeatures",
                    state: true,
                    timeout: 4000
                  });
                } else {
                  //Show success message
                  this.toggleSnackbar({
                    type: "success", //success or error
                    message: "allScenarioFeaturesDelete",
                    state: true,
                    timeout: 4000
                  });
                  //2- Clear openlayers scenario features
                  this.clear();
                  // This also deletes user scenario features from the map
                  this.olEditCtrl.deleteAll();
                }
              })
              .catch(() => {
                this.isDeleteAllBusy = false;
              });
          }
        });
    },
    /**
     * Stop edit and select interactions (Doesn't deletes the features)
     */
    stop() {
      const me = this;
      me.olSelectCtrl.removeInteraction();
      me.olEditCtrl.removeInteraction();
      EventBus.$emit("ol-interaction-stoped", me.interactionType);
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
      if (["add", "modifyAttributes"].includes(type)) {
        if (type === "modifyAttributes") {
          var propKeys = Object.keys(this.dataObject);
          propKeys.forEach(key => {
            const propValue = this.dataObject[key];
            if (propValue) {
              this.olEditCtrl.featuresToCommit[0].set(key, propValue);
            }
            this.olEditCtrl.featuresToCommit[0].set("status", null);
          });
        }
        this.olEditCtrl.transact(this.dataObject);
        this.olEditCtrl.closePopup();
      } else {
        //Delete feature
        this.olEditCtrl.deleteFeature();
      }
    },
    /**
     * Methods used on popup cancel
     */
    cancel() {
      if (this.olEditCtrl.featuresToCommit.length > 0) {
        this.olEditCtrl.featuresToCommit.forEach(feature => {
          this.olEditCtrl.source.removeFeature(feature);
          if (this.olEditCtrl.storageLayer.getSource().hasFeature(feature)) {
            this.olEditCtrl.storageLayer.getSource().removeFeature(feature);
          }
        });
      }
      this.olEditCtrl.closePopup();
    },
    cancelAttributeEdit() {
      this.olEditCtrl.featuresToCommit = [];
      this.olEditCtrl.closePopup();
    },
    /**
     * Method called when edit layer source is changed.
     * A debounce is addes to improve performance
     * It updates the scenario data table.
     */
    updateDataTable: debounce(function() {
      const editLayerFeatures = this.olEditCtrl.source.getFeatures();
      const deletedFeatures = editLayerHelper.deletedFeatures;

      const scenarioDataTable = [];

      editLayerFeatures.forEach(f => {
        const prop = f.getProperties();
        if (this.activeScenario === f.get("scenario_id")) {
          if (
            prop.hasOwnProperty(this.original_id) ||
            (prop.hasOwnProperty("deletedId") && prop.status !== 1)
          ) {
            //Assign layerName to feature property if doesn't exist
            if (!prop.layerName) {
              f.set("layerName", this.layerName);
            }
            const fid = f.getId();
            const layerName = f.get("layerName");
            const isDeleted = false;
            let status = prop.status ? "Uploaded" : "NotUploaded";
            const originalId = f.get(this.original_id);
            let type = "";
            if (
              prop.hasOwnProperty(this.original_id) &&
              f.get(this.original_id) === null
            ) {
              type = "New";
            } else if (prop.hasOwnProperty("deletedId")) {
              type = "Restored"; //Not uploaded (if feature is uploaded it will not be visible in the list)
            } else {
              type = "Modified";
            }

            const obj = {
              fid,
              layerName,
              isDeleted,
              originalId,
              status,
              type
            };
            scenarioDataTable.push(obj);
          }
        }
      });

      deletedFeatures.forEach(f => {
        if (this.activeScenario === f.get("scenario_id")) {
          const prop = f.getProperties();
          const fid = f.getId() || prop.id;
          if (!f.getId()) {
            f.setId(prop.id);
          }
          if (!prop.layerName) {
            f.set("layerName", this.layerName);
          }
          const layerName = f.get("layerName");
          const isDeleted = fid;
          let status = prop.status === 1 ? "Uploaded" : "NotUploaded";
          if (f.get("layerName") === "poi") {
            status = "Uploaded";
          }
          const type = "deleted";
          let source = "";
          if (
            prop.hasOwnProperty(this.original_id) &&
            f.get(this.original_id) === null
          ) {
            //Original deleted Features.
            source = "drawn";
          } else {
            //Drawn Delete Feature
            source = "original";
          }
          const originalId = f.get(this.original_id);

          const obj = {
            fid,
            layerName,
            isDeleted,
            originalId,
            status,
            type,
            source
          };
          scenarioDataTable.push(obj);
        }
      });
      this.scenarioDataTable = scenarioDataTable;
      this.isTableLoading = false;
    }, 900),
    updateUploadBtnState: debounce(function() {
      const features = this.olEditCtrl.source.getFeatures();
      let featuresWithoutEntrances = 0;
      features.forEach(f => {
        if (f.get("layerName") && f.get("layerName") === "building") {
          // Check if there is a entrance point. If not disable upload
          const extent = f.getGeometry().getExtent();
          const entrancesInExtent = this.olEditCtrl.bldEntranceLayer
            .getSource()
            .getFeaturesInExtent(extent);
          let entrances = 0;
          entrancesInExtent.forEach(entrance => {
            const buildingId = f.get("id") || f.getId();
            if (entrance.get("building_modified_id") === buildingId) {
              entrances += 1;
            }
          });
          if (entrances === 0) {
            featuresWithoutEntrances += 1;
          }
        }
      });
      this.isUploadBtnEnabled = featuresWithoutEntrances === 0 ? true : false;
    }, 500),
    isRestoreBtnVisible(item) {
      if (item.source !== "original") {
        return false;
      }
      return item.isDeleted;
    },
    isDeleteBtnVisible(item) {
      if (!item.originalId && item.isDeleted) {
        return false;
      }
      return !item.isDeleted;
    },

    inputFn(e) {
      if (e === "open_dialog") {
        this.showOpeningHours = true;
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
    scenarioArray() {
      const scenarioArray = [];
      Object.keys(this.scenarios).forEach(key => {
        scenarioArray.push({
          display: this.scenarios[key].title,
          value: parseInt(key)
        });
      });
      return scenarioArray;
    },
    layerName() {
      const value = this.selectedLayer["name"];
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
    getValidationMessage() {
      let message = `<span>${this.$t(
        `appBar.edit.${this.fileInputValidationMessage}`
      )}</span>`;
      if (
        this.fileInputValidationMessage ===
        this.fileInputValidationMessageEnum.MISSING_FIELDS
      ) {
        message += `<span> : <b>${this.missingFieldsNames}</b></span>`;
      }
      return message;
    },
    getFields() {
      const layerName = this.schema[this.layerName];
      return layerName && this.reqFields.length > 0
        ? `&#9679; ${this.$t(
            "appBar.edit.requiredFields"
          )}: <span> <b>${this.reqFields.join(", ")}</b></span>`
        : `<span></span>`;
    },
    original_id() {
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
    ...mapGetters("auth", { currentUser: "currentUser" }),
    ...mapGetters("app", {
      appColor: "appColor",
      calculationMode: "calculationMode",
      openapiConfig: "openapiConfig",
      poiIcons: "poiIcons"
    }),
    ...mapGetters("map", {
      contextmenu: "contextmenu",
      layers: "layers"
    }),
    ...mapFields("scenarios", {
      scenarioDataTable: "scenarioDataTable",
      scenarios: "scenarios",
      activeScenario: "activeScenario"
    }),
    ...mapFields("map", {
      selectedLayer: "selectedEditLayer",
      busyLayers: "busyLayers"
    })
  },
  created() {
    this.getlayerFeatureTypes();
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
