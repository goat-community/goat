<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-subheader>
        <span class="title">{{ $t("appBar.edit.title") }}</span>
      </v-subheader>
      <v-card-text class="pr-16 pl-16 pt-0 pb-0">
        <v-divider></v-divider>

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
                    :color="activeColor.primary"
                    fab
                    dark
                    small
                    @click="showScenarioDialog = true"
                  >
                    <v-icon dark>add</v-icon>
                  </v-btn>
                </template>
                <span>Create new scenario</span></v-tooltip
              >
            </v-col>
            <v-col v-if="activeScenario" class="text-center">
              <v-tooltip top>
                <template v-slot:activator="{ on }">
                  <v-btn
                    v-on="on"
                    class="mt-1 ml-1"
                    :color="activeColor.primary"
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
                <span>Edit Scenario Name</span></v-tooltip
              >
            </v-col>
          </v-row>
        </div>
        <div v-if="Object.keys(scenarios).length === 0">
          <v-row align="center">
            <v-col class="text-center">
              <v-btn
                width="100%"
                class="text-xs-center white--text"
                dark
                :color="activeColor.primary"
                @click="showScenarioDialog = true"
              >
                <v-icon left dark>add</v-icon>
                Create Scenario
              </v-btn>
            </v-col></v-row
          >
        </div>

        <div v-if="Object.keys(scenarios).length > 0">
          <v-divider></v-divider>
          <v-subheader class="ml-0 pl-0 mb-0 pb-0">
            <v-icon style="color:#30c2ff;" small class="mr-2"
              >fas fa-layer-group</v-icon
            >
            <h3>Select Layer</h3>
          </v-subheader>
          <v-select
            class="mt-4"
            :items="editableLayers"
            v-model="selectedLayer"
            item-value="values_.name"
            return-object
            :loading="loadingLayerInfo"
            solo
            :label="$t('appBar.edit.selectLayer')"
          >
            <template slot="selection" slot-scope="{ item }">
              {{ translate("layerName", item.get("name")) }}
            </template>
            <template slot="item" slot-scope="{ item }">
              {{ translate("layerName", item.get("name")) }}
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
              selectedLayer.getVisible() === false &&
              selectedLayer.get('displayInLayerList') &&
              selectedLayer.get('name') === 'pois'
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
                  v-show="selectedLayer.get('canModifyGeom') !== false"
                  top
                >
                  <template v-slot:activator="{ on }">
                    <v-btn
                      v-show="selectedLayer.get('canModifyGeom') !== false"
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
                      v-show="selectedLayer.get('modifyAttributes') === true"
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
                      selectedLayer.get('editGeometry').includes(r)
                    )
                  "
                >
                  <template v-slot:activator="{ on }">
                    <v-btn
                      v-show="
                        !['Point', 'LineString'].some(r =>
                          selectedLayer.get('editGeometry').includes(r)
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
                          selectedLayer.get('editGeometry').includes(r)
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
                <v-tooltip v-if="selectedLayer.get('name') === 'buildings'" top>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      class="ml-0 mr-2 mt-2"
                      v-if="selectedLayer.get('name') === 'buildings'"
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
                      selectedLayer.get('editGeometry').includes(r)
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
                      selectedLayer.get('editGeometry').includes(r)
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

          <!-- ==== <SCENARIO MANAGE> ====-->
          <v-subheader
            class="clickable ml-0 pl-0"
            @click="dataManageElVisible = !dataManageElVisible"
          >
            <v-icon
              :style="dataManageElVisible === true ? { color: '#30c2ff' } : {}"
              small
              class="mr-2"
              >fas fa-database</v-icon
            >
            <h3>Scenario Import/Export</h3>
          </v-subheader>
          <div class="ml-2" v-if="dataManageElVisible">
            <v-flex
              v-if="layerConf[layerName.split(':')[1]]"
              xs12
              v-show="selectedLayer != null && dataManageElVisible === true"
              class="mt-1 pt-0 mb-0"
            >
              <v-file-input
                :rules="uploadRules"
                @change="readFile"
                @click:clear="clearFile"
                accept=".json,.geojson"
                clearable
                v-model="file"
                label="Import"
              ></v-file-input>

              <!-- LAYER FIELD INFO ALERT  -->
              <v-alert
                v-if="
                  fileInputFeaturesCache.length === 0 &&
                    fileInputValidationMessage === 'fileValidOrNoFile' &&
                    schema[layerName]
                "
                class="elevation-2"
                type="info"
                :color="activeColor.primary"
                border="left"
                colored-border
                dense
              >
                <span
                  >&#9679; {{ $t("appBar.edit.dataTypeInfo") }}:
                  <b>{{ selectedLayer.get("editDataType") }}</b>
                </span>
                <br />
                <span
                  >&#9679; {{ $t("appBar.edit.geometryTypeInfo") }}:
                  <b>{{ selectedLayer.get("editGeometry").toString() }}</b>
                </span>
                <br />
                <span
                  >&#9679; {{ $t("appBar.edit.referenceSystemInfo") }}
                  <b>EPSG:4326</b>
                </span>
                <br />
                <span v-html="getFields"> </span>
              </v-alert>

              <!-- FILE INPUT VALIDATION MESSAGE ALERTS -->
              <v-alert
                v-if="fileInputValidationMessage !== 'fileValidOrNoFile'"
                class="elevation-2"
                :type="fileInputValidationTypeEnum[fileInputValidationMessage]"
                dense
              >
                <span v-html="getValidationMessage"></span>
              </v-alert>

              <!-- FEATURES NOT YET UPLOADED ALERT -->
              <!-- <v-alert
                class="elevation-2"
                v-if="fileInputFeaturesCache.length > 0"
                dense
                type="info"
              >
                {{ $t("appBar.edit.featuresNotyetUploaded") }}
              </v-alert> -->
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  :disabled="scenarioDataTable.length === 0"
                  :loading="isExportScenarioBusy"
                  class="white--text"
                  :color="activeColor.primary"
                  @click="exportScenario"
                >
                  <v-icon left>fas fa-download</v-icon>Export
                </v-btn>
              </v-card-actions>
            </v-flex>
          </div>
          <v-divider></v-divider>

          <!-- ==== </SCENARIO MANAGE> ====-->

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
            <h3>Scenario Features</h3>
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
      </v-card-text>

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
            selectedLayer.get('name') === 'buildings' &&
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
            isDeleteAllBusy ||
              (isUploadBtnEnabled === false &&
                selectedLayer &&
                selectedLayer.get('name') === 'buildings' &&
                olEditCtrl.source.getFeatures().length > 0)
          "
          :color="activeColor.primary"
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
    <!-- Opening hours -->
    <opening-hours
      :color="activeColor.primary"
      :visible="showOpeningHours"
      @close="showOpeningHours = false"
    />
  </v-flex>
</template>

<script>
import { EventBus } from "../../../EventBus";
import { Mapable } from "../../../mixins/Mapable";
import { KeyShortcuts } from "../../../mixins/KeyShortcuts";
import { InteractionsToggle } from "../../../mixins/InteractionsToggle";
import { Isochrones } from "../../../mixins/Isochrones";
import { mapFields } from "vuex-map-fields";
import {
  getAllChildLayers,
  getPoisListValues,
  wfsTransactionParser,
  mapFeatureTypeProps,
  readTransactionResponse
} from "../../../utils/Layer";
import OlEditController from "../../../controllers/OlEditController";
import OlSelectController from "../../../controllers/OlSelectController";
import editLayerHelper from "../../../controllers/OlEditLayerHelper";

import OverlayPopup from "../../viewer/ol/controls/Overlay";
import ScenarioDialog from "../../core/ScenarioDialog";
import http from "axios";
import VJsonschemaForm from "../../other/dynamicForms/index";
import OpeningHours from "../../other/OpeningHours";

import { geojsonToFeature } from "../../../utils/MapUtils";
import { mapGetters, mapMutations } from "vuex";
import { debounce } from "../../../utils/Helpers";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import { featuresToGeojson } from "../../../utils/MapUtils";
import VectorSource from "ol/source/Vector";

import { saveAs } from "file-saver";

export default {
  components: {
    "overlay-popup": OverlayPopup,
    "opening-hours": OpeningHours,
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
    loadingLayerInfo: false,
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
      this.canCalculateScenario(this.options.calculationModes.active);
    },
    "options.calculationModes.active": function(value) {
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
      const editableLayers = getAllChildLayers(me.map).filter(layer =>
        layer.get("canEdit")
      );
      me.editableLayers = [...editableLayers];
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
     * Use scenario id to export files.
     */
    exportScenario() {
      this.isExportScenarioBusy = true;
      http
        .post(
          "/api/export_scenario",
          {
            scenario_id: this.activeScenario
          },
          {
            responseType: "blob"
          }
        )
        .then(response => {
          this.isExportScenarioBusy = false;
          if (response.data) {
            saveAs(
              response.data,
              `${this.scenarios[this.activeScenario].title}.zip`
            );
          }
        })
        .catch(error => {
          console.log(error);
          this.toggleSnackbar({
            type: "error", //success or error
            message: "cantExportScenario",
            state: true,
            timeout: 2500
          });
          this.isExportScenarioBusy = false;
        });
    },
    /**
     * Parse user input file and transform features if valid.
     */
    readFile(file) {
      if (file) {
        const reader = new FileReader();
        reader.readAsText(file);
        reader.onload = () => {
          //- Check for size and other validations
          const result = reader.result;
          //- Parse geojson data
          let features = geojsonToFeature(result, {
            dataProjection: "EPSG:4326",
            featureProjection: "EPSG:3857"
          });
          if (!features || features.length === 0) return;

          if (
            this.selectedLayer.get("name") === "buildings" &&
            features[0].getGeometry().getType() === "Point"
          ) {
            features.forEach(feature => {
              const point = feature.getGeometry().getCoordinates();
              // Check if there is a building under the uploaded features.
              const featuresAtCoord = this.olEditCtrl.source
                .getFeaturesAtCoordinate(point)
                .filter(f => f.get("layerName") === "buildings");
              if (featuresAtCoord[0]) {
                feature.set(
                  "building_gid",
                  featuresAtCoord[0].get("gid") ||
                    featuresAtCoord[0].get("id") ||
                    featuresAtCoord[0].getId()
                );
              }
            });
          }
          //- Check geometry type
          //- For buildings point geometry is allowed in order to upload building entrance layer

          let editGeometryTypes = this.selectedLayer.get("editGeometry");
          if (
            this.selectedLayer.get("name") === "buildings" &&
            features[0].getGeometry().getType() === "Point" // User is upload building entrance features..
          ) {
            editGeometryTypes = [...editGeometryTypes];
            editGeometryTypes.push("Point");
          }
          if (
            ![features[0].getGeometry().getType()].some(r =>
              editGeometryTypes.includes(r)
            )
          ) {
            //Geojson not valid
            this.fileInputValidationMessage = this.fileInputValidationMessageEnum.DIFFERENT_GEOMETRY_TYPE;
            return;
          }

          //- Check field names
          if (
            !this.selectedLayer.get("name") === "buildings" &&
            !features[0].getGeometry().getType() === "Point"
          ) {
            const props = features[0].getProperties();
            const propKeys = Object.keys(props);
            const intersected = propKeys.filter(
              value => !this.reqFields.includes(value)
            );
            if (
              propKeys.length !==
              intersected.length + this.reqFields.length
            ) {
              //Geojson not valid.
              this.fileInputValidationMessage = this.fileInputValidationMessageEnum.MISSING_FIELDS;
              const missing = this.reqFields.filter(
                value => !propKeys.includes(value)
              );
              if (missing.length > 0) {
                this.missingFieldsNames = missing.join(", ");
              }
              return;
            } else {
              this.fileInputValidationMessage = this.fileInputValidationMessageEnum.FILE_VALID_OR_NO_FILE;
            }
          }

          //5- Import scenario features
          this.importScenario(
            this.userId,
            this.activeScenario,
            this.selectedLayer.get("name") === "buildings" &&
              features[0].getGeometry().getType() === "Point"
              ? "buildings_entrances"
              : this.selectedLayer.get("name"),
            features
          );
        };
        reader.onerror = () => {
          console.log(reader.error);
        };
      }
    },
    /**
     * Clear event when X icon is clicked in the file input form.
     * Cache features will be removed from edit layer.
     */
    clearFile() {
      const editLayerSource = this.olEditCtrl.source;
      if (!editLayerSource) return;
      this.fileInputFeaturesCache = [];
      this.fileInputValidationMessage = this.fileInputValidationMessageEnum.FILE_VALID_OR_NO_FILE;
      this.file = null;
      this.missingFieldsNames = "";
    },
    /**
     * Upload user uploaded features to DB using a wfs-t
     */
    importScenario(user_id, scenario_id, layerName, features) {
      const payload = featuresToGeojson(features, "EPSG:3857", "EPSG:4326");
      http
        .post(
          "api/import_scenario",
          {
            user_id,
            scenario_id,
            layerName,
            payload: JSON.parse(payload)
          },
          {
            headers: { "Content-Type": "application/json" }
          }
        )
        .then(response => {
          console.log(response);
          if (response.data) {
            //Add features to the edit layer to let the user interact
            const features = geojsonToFeature(response.data, {
              dataProjection: "EPSG:4326",
              featureProjection: "EPSG:3857"
            });
            let areAllUploaded = 1;
            //- Transform features
            const visibleFeatures = [];

            //- Filter out building features that dont intersect.

            features.forEach(feature => {
              //- Fiilter out building features that dont intersect.
              if (
                this.selectedLayer.get("name") === "buildings" &&
                feature.getGeometry().getType() === "Point"
              ) {
                const point = feature.getGeometry().getCoordinates();
                // Check if there is a building under the uploaded features.
                const featuresAtCoord = this.olEditCtrl.source
                  .getFeaturesAtCoordinate(point)
                  .filter(f => f.get("layerName") === "buildings");
                if (featuresAtCoord[0]) {
                  feature.set(
                    "building_gid",
                    featuresAtCoord[0].get("gid") ||
                      featuresAtCoord[0].get("id") ||
                      featuresAtCoord[0].getId()
                  );
                }
              }

              if (layerName !== "pois") {
                feature.set("status", null);
              }
              feature.set("scenario_id", this.activeScenario);
              //Clone geometry and change name to 'geom' (should be the same as geoserver layer geometry name)
              feature.set("geom", feature.getGeometry().clone());
              feature.setGeometryName("geom");
              //Add an extra attribute to distinguish between local features from file upload and those that are laoded from the DB.
              // feature.set("user_uploaded", true);
              //Remove previously geometry object
              feature.unset("geometry");

              if (feature.get("upload_status") !== "successful") {
                areAllUploaded = 0;
              }

              if (feature.get("gid")) {
                feature.setId(feature.get("gid"));
              }

              // Manage delete features.
              if (
                !["deleted", "old_modified"].includes(
                  feature.get("edit_type")
                ) &&
                feature.get("upload_status") === "successful"
              ) {
                visibleFeatures.push(feature);
              }
              if (
                feature.get("edit_type") === "deleted" &&
                feature.get("upload_status") === "successful"
              ) {
                if (
                  layerName !== "buildings_entrances" &&
                  feature.get("edit_type") === "deleted"
                ) {
                  // Push to deleted
                  const fid =
                    feature.getProperties().original_id ||
                    feature.getProperties().id ||
                    feature.getProperties().gid;
                  if (fid) {
                    editLayerHelper.featuresIDsToDelete.push(fid.toString());
                  }
                  editLayerHelper.deletedFeatures.push(feature);
                }
                if (!feature.getProperties().hasOwnProperty("original_id")) {
                  feature.set("original_id", null);
                }
              }
            });

            if (areAllUploaded) {
              this.fileInputValidationMessage = this.fileInputValidationMessageEnum.ALL_FEATURES_UPLOADED;
            } else {
              this.fileInputValidationMessage = this.fileInputValidationMessageEnum.NOT_ALL_UPLOADED;
            }
            const tempSource = new VectorSource();
            tempSource.addFeatures(visibleFeatures);
            const featuresExtent = tempSource.getExtent();
            if (layerName === "buildings_entrances") {
              this.olEditCtrl.bldEntranceLayer
                .getSource()
                .addFeatures(visibleFeatures);
              this.olEditCtrl.bldEntranceLayer.getSource().changed();
              this.map.getView().fit(featuresExtent);
            } else {
              this.olEditCtrl.source.addFeatures(visibleFeatures);
              this.map.getView().fit(featuresExtent);
              this.fileInputFeaturesCache = [...visibleFeatures];
              this.olEditCtrl.source.changed();
            }
          } else {
            this.fileInputValidationMessage = this.fileInputValidationMessageEnum.ERROR_HAPPENED;
          }
          setTimeout(() => {
            this.fileInputValidationMessage = this.fileInputValidationMessageEnum.FILE_VALID_OR_NO_FILE;
          }, 3000);
        });
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
              ((candidate.get("gid") ||
                candidate.get("id") ||
                candidate.getId()) &&
                this.tempBldEntranceFeature &&
                this.tempBldEntranceFeature.get("building_gid") ===
                  candidate.get("gid")) ||
              this.tempBldEntranceFeature.get("building_gid") ===
                candidate.get("id") ||
              this.tempBldEntranceFeature.get("building_gid") ===
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
        !buildingFeatureAtCoord.getProperties().hasOwnProperty("original_id")
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

      let payload;
      let bldEntranceFeature;
      const formatGML = {
        featureNS: "cite",
        featureType: `population_modified`,
        srsName: "urn:x-ogc:def:crs:EPSG:4326"
      };
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
        payload = wfsTransactionParser(null, [clonedFeature], null, formatGML);
      } else {
        // Add new feature
        bldEntranceFeature = new Feature({
          geometry: new Point(bldEntranceCoordinate),
          building_gid:
            buildingFeatureAtCoord.get("gid") ||
            buildingFeatureAtCoord.get("id") ||
            buildingFeatureAtCoord.getId(),
          scenario_id: this.activeScenario
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

        payload = wfsTransactionParser([clonedFeature], null, null, formatGML);
      }
      const serializedPayload = new XMLSerializer().serializeToString(payload);
      http
        .post("geoserver/cite/wfs", serializedPayload, {
          headers: { "Content-Type": "text/xml" }
        })
        .then(response => {
          const result = readTransactionResponse(response.data);
          const FIDs = result.insertIds;
          if (FIDs != undefined && FIDs[0] != "none") {
            const id = parseInt(FIDs[0].split(".")[1]);
            bldEntranceFeature.setId(id);
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
      if (["pois"].includes(evt.feature.get("layerName"))) {
        evt.feature.set("status", 1);
      }

      if (
        this.selectedLayer.get("name") === "buildings" &&
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
      this.loadingLayerInfo = true;
      if (this.schema[this.layerName]) {
        this.loadingLayerInfo = false;
        this.updateReqFields(this.reqFields);
        return;
      }
      http
        .get(
          `geoserver/wfs?request=describeFeatureType&typename=${this.layerName}_modified&outputFormat=application/json`
        )
        .then(response => {
          const props = response.data.featureTypes[0].properties;
          const layerName = this.layerName.split(":")[1];
          const jsonSchema = mapFeatureTypeProps(
            props,
            layerName,
            this.layerConf[layerName]
          );
          this.schema[this.layerName] = jsonSchema;
          this.loadingLayerInfo = false;
          this.updateReqFields(this.reqFields);
          this.$forceUpdate();
        });
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
      if (newValue.get("name") === "buildings") {
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
      me.clearFile();
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
      const layerNames = [this.selectedLayer.get("name")];
      this.$refs.confirm
        .open(
          this.$t("appBar.edit.deleteAllTitle"),
          this.$t("appBar.edit.deleteAllMessage"),
          { color: this.activeColor.primary }
        )

        .then(confirm => {
          if (confirm) {
            //1- Call api to delete all features.
            const userId = this.userId;
            //1- Call api to delete all features.
            this.isDeleteAllBusy = true;
            http
              .post("api/deleteAllScenarioData", {
                user_id: userId,
                layer_names: layerNames,
                scenario_id: this.activeScenario
              })
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
            prop.hasOwnProperty("original_id") ||
            (prop.hasOwnProperty("deletedId") && prop.status !== 1)
          ) {
            //Assign layerName to feature property if doesn't exist
            if (!prop.layerName) {
              f.set("layerName", this.layerName.split(":")[1]);
            }
            const fid = f.getId();
            const layerName = f.get("layerName");
            const isDeleted = false;
            let status = prop.status ? "Uploaded" : "NotUploaded";
            const originalId = f.get("original_id");
            let type = "";
            if (
              prop.hasOwnProperty("original_id") &&
              f.get("original_id") === null
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
            f.set("layerName", this.layerName.split(":")[1]);
          }
          const layerName = f.get("layerName");
          const isDeleted = fid;
          let status = prop.status === 1 ? "Uploaded" : "NotUploaded";
          if (f.get("layerName") === "pois") {
            status = "Uploaded";
          }
          const type = "deleted";
          let source = "";
          if (
            prop.hasOwnProperty("original_id") &&
            f.get("original_id") === null
          ) {
            //Original deleted Features.
            source = "drawn";
          } else {
            //Drawn Delete Feature
            source = "original";
          }
          const originalId = f.get("original_id");

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
        if (f.get("layerName") && f.get("layerName") === "buildings") {
          // Check if there is a entrance point. If not disable upload
          const extent = f.getGeometry().getExtent();
          const entrancesInExtent = this.olEditCtrl.bldEntranceLayer
            .getSource()
            .getFeaturesInExtent(extent);
          let entrances = 0;
          entrancesInExtent.forEach(entrance => {
            const buildingId = f.get("gid") || f.get("id") || f.getId();
            if (entrance.get("building_gid") === buildingId) {
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
      return this.selectedLayer.getSource().getParams().LAYERS;
    },
    reqFields() {
      const layerSchema = this.schema[this.layerName];
      const layerFieldsKeys = Object.keys(layerSchema.properties);
      return layerFieldsKeys.filter(
        el =>
          !["original_id", "id", "gid", "scenario_id"].includes(el) &&
          layerSchema.required.includes(el)
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
    ...mapGetters("user", { userId: "userId" }),
    ...mapGetters("isochrones", { options: "options" }),
    ...mapGetters("app", {
      activeColor: "activeColor"
    }),
    ...mapGetters("map", {
      contextmenu: "contextmenu"
    }),
    ...mapFields("isochrones", {
      scenarioDataTable: "scenarioDataTable",
      scenarios: "scenarios",
      activeScenario: "activeScenario"
    }),
    ...mapFields("map", {
      selectedLayer: "selectedEditLayer"
    })
  },
  created() {
    this.layerConf = this.$appConfig.layerConf;
    //Edge Case (get all pois keys)
    if (
      this.layerConf.pois.listValues.amenity &&
      this.layerConf.pois.listValues.amenity.values === "*"
    ) {
      const poisListValues = getPoisListValues(
        this.$appConfig.componentData.pois.allPois
      );
      this.layerConf.pois.listValues.amenity.values = poisListValues;
    }
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
