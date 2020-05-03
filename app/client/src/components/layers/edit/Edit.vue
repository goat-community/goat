<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-subheader>
        <span class="title">{{ $t("appBar.edit.title") }}</span>
      </v-subheader>
      <v-card-text class="pr-16 pl-16 pt-0 pb-0">
        <v-divider></v-divider>

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

        <v-alert
          border="left"
          colored-border
          class="mb-2 mt-0 mx-0 elevation-2"
          icon="info"
          color="green"
          dense
          v-if="
            selectedLayer &&
              selectedLayer.getVisible() === false &&
              selectedLayer.get('displayInLayerList')
          "
        >
          <span v-html="$t('appBar.edit.activateLayerToDrawScenario')"></span>
        </v-alert>
        <template v-if="selectedLayer && schema[layerName]">
          <v-divider></v-divider>
          <v-flex xs12 v-show="selectedLayer != null" class="mt-1 pt-0 mb-4">
            <p class="mb-1">{{ $t("appBar.edit.selectFeatures") }}</p>
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
          <v-flex xs12 v-show="selectedLayer != null" class="mt-1 pt-0 mb-4">
            <v-divider class="mb-1"></v-divider>
            <p class="mb-1">{{ $t("appBar.edit.editTools") }}</p>
            <v-btn-toggle v-model="toggleEdit">
              <v-tooltip top>
                <template v-slot:activator="{ on }">
                  <v-btn :value="1" v-on="on" text>
                    <v-icon medium>add</v-icon>
                  </v-btn>
                </template>
                <span>{{ $t("appBar.edit.drawFeatureTooltip") }}</span>
              </v-tooltip>

              <v-tooltip top>
                <template v-slot:activator="{ on }">
                  <v-btn :value="2" v-on="on" text>
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
                v-show="selectedLayer.get('editGeometry') !== 'Point'"
              >
                <template v-slot:activator="{ on }">
                  <v-btn
                    v-show="
                      !['Point', 'LineString'].includes(
                        selectedLayer.get('editGeometry')
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
            </v-btn-toggle>

            <v-btn-toggle v-model="toggleEdit">
              <v-tooltip top>
                <template v-slot:activator="{ on }">
                  <v-btn
                    :value="6"
                    class="ml-0 mr-2 mt-2"
                    v-show="
                      !['Point', 'LineString'].includes(
                        selectedLayer.get('editGeometry')
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
            <v-btn-toggle v-model="toggleSnapGuide">
              <v-tooltip
                top
                v-if="
                  ['Polygon', 'MultiPolygon'].includes(
                    selectedLayer.get('editGeometry')
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
          </v-flex>
          <v-flex
            v-if="
              layerConf.layerName &&
                layerConf[layerName.split(':')[1]].enableFileUpload === true
            "
            xs12
            v-show="selectedLayer != null"
            class="mt-1 pt-0 mb-0"
          >
            <v-divider class="mb-1"></v-divider>
            <p class="mb-1">{{ $t("appBar.edit.uploadYourData") }}</p>
            <v-file-input
              :rules="uploadRules"
              @change="readFile"
              @click:clear="clearFile"
              accept=".json,.geojson"
              clearable
              v-model="file"
              label="File input"
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
              color="green"
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
                <b>{{ selectedLayer.get("editGeometry") }}</b>
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
            <v-alert
              class="elevation-2"
              v-if="fileInputFeaturesCache.length > 0"
              dense
              type="info"
            >
              {{ $t("appBar.edit.featuresNotyetUploaded") }}
            </v-alert>
          </v-flex>

          <!-- DATA TABLE FOR DRAWN/MODIFIED/DELETED FEATURES OF THE USER  -->

          <v-flex v-if="selectedLayer !== null" xs12 class="mt-1 pt-0 mb-0">
            <v-divider class="mb-1"></v-divider>
            <p class="mb-1">{{ $t("appBar.edit.scenarioFeatures") }}</p>
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
        </template>
      </v-card-text>

      <!-- ----- -->
      <v-card-actions v-if="selectedLayer && schema[layerName]">
        <v-spacer></v-spacer>

        <v-btn
          v-show="selectedLayer != null"
          class="white--text"
          :loading="isUploadBusy"
          :disabled="isDeleteAllBusy"
          color="green"
          @click="uploadFeatures"
        >
          <v-icon left>cloud_upload</v-icon>{{ $t("appBar.edit.uploadBtn") }}
        </v-btn>
        <v-btn
          v-show="selectedLayer != null"
          class="white--text"
          color="error"
          :loading="isDeleteAllBusy"
          :disabled="scenarioDataTable.length === 0"
          @click="deleteAll"
        >
          <v-icon left>delete</v-icon>{{ $t("appBar.edit.clearBtn") }}
        </v-btn>
      </v-card-actions>
    </v-card>

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
          <v-form v-model="formValid">
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
  wfsTransactionParser
} from "../../../utils/Layer";
import OlEditController from "../../../controllers/OlEditController";
import OlSelectController from "../../../controllers/OlSelectController";
import editLayerHelper from "../../../controllers/OlEditLayerHelper";
import {
  mapFeatureTypeProps,
  readTransactionResponse
} from "../../../utils/Layer";
import OverlayPopup from "../../viewer/ol/controls/Overlay";
import http from "axios";
import VJsonschemaForm from "../../other/dynamicForms/index";
import OpeningHours from "../../other/OpeningHours";

import { geojsonToFeature } from "../../../utils/MapUtils";
import { mapGetters, mapMutations } from "vuex";
import { debounce } from "../../../utils/Helpers";

export default {
  components: {
    "overlay-popup": OverlayPopup,
    "opening-hours": OpeningHours,
    VJsonschemaForm
  },
  mixins: [InteractionsToggle, Mapable, KeyShortcuts, Isochrones],
  data: () => ({
    interactionType: "edit-interaction",
    selectedLayer: null,
    selectedFeatures: [],
    editableLayers: [],
    toggleSelection: undefined,
    toggleEdit: undefined,
    toggleSnapGuide: 0, // Used for snap and other functionalities (Active by default).
    loadingLayerInfo: false,
    isUploadBusy: false,
    isDeleteAllBusy: false,
    //Popup configuration
    popup: {
      title: "",
      isVisible: false,
      el: null,
      selectedInteraction: null
    },
    //Upload field.
    isFileUploadEnabled: false,
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
      drawHole: "crosshair"
    },
    //Data table
    isTableLoading: false,
    //Opening Hours
    showOpeningHours: false
  }),
  watch: {
    selectedLayer(newValue) {
      const me = this;
      //Read or Insert deleted features
      me.clear();
      editLayerHelper.selectedLayer = newValue;
      me.getlayerFeatureTypes();
      me.olEditCtrl.readOrInsertDeletedFeatures();
      me.olEditCtrl.dataObject = this.dataObject;
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
    scenarioDataTable() {
      this.canCalculateScenario(this.options.calculationModes.active);
    },
    "options.calculationModes.active": function(value) {
      this.canCalculateScenario(value);
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
    },
    /**
     * Parse user input file and transform features if valid.
     */
    readFile(file) {
      if (file) {
        const reader = new FileReader();
        reader.readAsText(file);
        reader.onload = () => {
          //1- Check for size and other validations
          const result = reader.result;
          //2- Parse geojson data
          const features = geojsonToFeature(result, {
            dataProjection: "EPSG:4326",
            featureProjection: "EPSG:3857"
          });
          if (!features || features.length === 0) return;
          //3- Check geometry type
          if (
            features[0].getGeometry().getType() !==
            this.selectedLayer.get("editGeometry")
          ) {
            //Geojson not valid
            this.fileInputValidationMessage = this.fileInputValidationMessageEnum.DIFFERENT_GEOMETRY_TYPE;
            return;
          }
          //4- Check field names
          const props = features[0].getProperties();
          const propKeys = Object.keys(props);
          const intersected = propKeys.filter(
            value => !this.reqFields.includes(value)
          );
          if (propKeys.length !== intersected.length + this.reqFields.length) {
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
          //4- Transform features
          features.forEach(feature => {
            //Set current userid
            feature.set("userid", this.userId);
            //Clone geometry and change name to 'geom' (should be the same as geoserver layer geometry name)
            feature.set("geom", feature.getGeometry().clone());
            feature.setGeometryName("geom");
            //Add an extra attribute to distinguish between local features from file upload and those that are laoded from the DB.
            feature.set("user_uploaded", true);
            //Remove previously geometry object
            feature.unset("geometry");
          });
          //Add features to the edit layer to let the user interact
          if (this.olEditCtrl.source) {
            this.olEditCtrl.source.addFeatures(features);
            this.map.getView().fit(this.olEditCtrl.source.getExtent());
            this.fileInputFeaturesCache = [...features];
          }
          //5- Upload features to DB
          //Feature will be uplaaded when upload button is clicked
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
      editLayerSource.getFeatures().forEach(feature => {
        if (feature.get("user_uploaded")) {
          editLayerSource.removeFeature(feature);
        }
      });
      this.fileInputFeaturesCache = [];
      this.fileInputValidationMessage = this.fileInputValidationMessageEnum.FILE_VALID_OR_NO_FILE;
      this.file = null;
      this.missingFieldsNames = "";
    },
    /**
     * Upload user uploaded features to DB using a wfs-t
     */
    uploadUserFeaturesToDB(featuresToUpload) {
      const formatGML = {
        featureNS: "muc",
        featureType: `${this.layerName}_modified`,
        srsName: "urn:x-ogc:def:crs:EPSG:4326"
      };
      //Features should be reprojected in 4326 again
      featuresToUpload.forEach(feature => {
        feature.getGeometry().transform("EPSG:3857", "EPSG:4326");
      });
      const payload = wfsTransactionParser(
        featuresToUpload,
        null,
        null,
        formatGML
      );
      http
        .post("geoserver/wfs", new XMLSerializer().serializeToString(payload), {
          headers: { "Content-Type": "text/xml" }
        })
        .then(response => {
          const result = readTransactionResponse(response.data);
          const totalInserted = result.transactionSummary.totalInserted;
          const total = this.fileInputFeaturesCache.length;
          this.fileInputFeaturesCache = [];
          this.file = null;
          if (totalInserted === total) {
            this.fileInputValidationMessage = this.fileInputValidationMessageEnum.ALL_FEATURES_UPLOADED;
          } else if (totalInserted > 0 && totalInserted < total) {
            this.fileInputValidationMessage = this.fileInputValidationMessageEnum.NOT_ALL_UPLOADED;
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
        this.olEditCtrl.isSnapGuideActive = true;
      } else {
        this.olEditCtrl.removeSnapGuideInteraction();
        this.olEditCtrl.isSnapGuideActive = false;
      }
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
        editLayerHelper.filterResults(response, me.olEditCtrl.getLayerSource());
      }
    },

    /**
     * Open modify attribute popup
     */
    openModifyAttributePopup(evt) {
      const features = this.olEditCtrl.source.getFeaturesAtCoordinate(
        evt.coordinate
      );
      this.olEditCtrl.highlightSource.clear();
      if (features.length > 0) {
        const feature = features[0];
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
    },
    /**
     * Modify interaction end event handler
     */
    onModifyEnd() {
      let props = {};
      Object.keys(this.schema[this.layerName].properties).forEach(key => {
        props[key] = null;
      });
      this.olEditCtrl.transact(props);
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
     * Feature change event handler
     */
    onFeatureChange(evt) {
      const me = this;
      //Exclude features from file input as we add this feature later when user click upload button
      if (evt.feature.get("user_uploaded")) return;
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
      if (["pois", "buildings"].includes(evt.feature.get("layerName"))) {
        evt.feature.set("status", 1);
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
      if (this.fileInputFeaturesCache.length > 0) {
        this.uploadUserFeaturesToDB(this.fileInputFeaturesCache);
      }
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

      if (item.type === "Deleted") {
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
        editLayerHelper.commitDelete(
          "update",
          this.userId,
          editLayerHelper.featuresIDsToDelete
        );
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
      this.$refs.confirm
        .open(
          this.$t("appBar.edit.deleteAllTitle"),
          this.$t("appBar.edit.deleteAllMessage"),
          { color: "green" }
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
                layer_names: ["ways", "pois"]
              })
              .then(response => {
                this.isDeleteAllBusy = false;
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
          const status = prop.status ? "Uploaded" : "NotUploaded";
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
      });

      deletedFeatures.forEach(f => {
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
        const status = prop.status === 1 ? "Uploaded" : "NotUploaded";
        const type = "Deleted";
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
      });
      this.scenarioDataTable = scenarioDataTable;
      this.isTableLoading = false;
    }, 900),
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
      toggleSnackbar: "TOGGLE_SNACKBAR"
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
    layerName() {
      return this.selectedLayer.getSource().getParams().LAYERS;
    },
    reqFields() {
      const layerSchema = this.schema[this.layerName];
      const layerFieldsKeys = Object.keys(layerSchema.properties);
      return layerFieldsKeys.filter(
        el =>
          !["original_id", "id", "userid"].includes(el) &&
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
    ...mapFields("isochrones", {
      scenarioDataTable: "scenarioDataTable"
    })
  },
  created() {
    this.layerConf = this.$appConfig.layerConf;
    this.isFileUploadEnabled = this.$appConfig.componentConf.edit.enableFileUpload;
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
</style>
