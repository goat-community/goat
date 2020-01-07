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
                <v-btn v-on="on" text>
                  <v-icon medium>add</v-icon>
                </v-btn>
              </template>
              <span>{{ $t("appBar.edit.drawFeatureTooltip") }}</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-btn v-on="on" text>
                  <v-icon>far fa-edit</v-icon>
                </v-btn>
              </template>
              <span>{{ $t("appBar.edit.modifyFeatureTooltip") }}</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <v-btn v-on="on" text>
                  <v-icon>far fa-trash-alt</v-icon>
                </v-btn>
              </template>
              <span>{{ $t("appBar.edit.deleteFeature") }}</span>
            </v-tooltip>
          </v-btn-toggle>
        </v-flex>
        <v-flex xs12 v-show="selectedLayer != null" class="mt-1 pt-0 mb-0">
          <v-divider class="mb-1"></v-divider>
          <p class="mb-1">Upload your data</p>
          <v-file-input
            :rules="uploadRules"
            @change="readFile"
            accept=".json"
            label="File input"
          ></v-file-input>
          <v-divider></v-divider>
        </v-flex>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn
          v-show="selectedLayer != null"
          class="white--text"
          color="green"
          @click="uploadFeatures"
        >
          <v-icon left>cloud_upload</v-icon>{{ $t("appBar.edit.uploadBtn") }}
        </v-btn>
        <v-btn
          v-show="selectedLayer != null"
          class="white--text"
          color="green"
          @click="clear"
        >
          <v-icon left>delete</v-icon>{{ $t("appBar.edit.clearBtn") }}
        </v-btn>
      </v-card-actions>
    </v-card>
    <!-- Popup overlay  -->
    <overlay-popup :title="popup.title" v-show="popup.isVisible" ref="popup">
      <v-btn icon>
        <v-icon>close</v-icon>
      </v-btn>
      <template v-slot:close>
        <v-btn @click="olEditCtrl.closePopup()" icon>
          <v-icon>close</v-icon>
        </v-btn>
      </template>
      <template v-slot:body>
        <div v-if="popup.selectedInteraction === 'delete'">
          <b>{{ $t("appBar.edit.popup.deleteFeatureMsg") }}</b>
        </div>
        <div v-else-if="popup.selectedInteraction === 'add'">
          <v-form v-model="formValid">
            <v-jsonschema-form
              v-if="schema[layerName]"
              :schema="schema[layerName]"
              :model="dataObject"
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
          <v-btn color="grey" text @click="cancel()">{{
            $t("buttonLabels.cancel")
          }}</v-btn>
        </template>
        <template v-else-if="popup.selectedInteraction === 'add'">
          <v-btn
            color="primary darken-1"
            :disabled="formValid === false"
            @click="ok('add')"
            text
            >{{ $t("buttonLabels.save") }}</v-btn
          >
          <v-btn color="grey" text @click="cancel()">{{
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
import { InteractionsToggle } from "../../../mixins/InteractionsToggle";
import { getAllChildLayers, getPoisListValues } from "../../../utils/Layer";

import OlEditController from "../../../controllers/OlEditController";
import OlSelectController from "../../../controllers/OlSelectController";

import editLayerHelper from "../../../controllers/OlEditLayerHelper";
import { mapFeatureTypeProps } from "../../../utils/Layer";

import Overlay from "../../ol/Overlay";
import http from "axios";

import VJsonschemaForm from "../../other/dynamicForms/index";
import { geojsonToFeature } from "../../../utils/MapUtils";

export default {
  components: {
    "overlay-popup": Overlay,
    VJsonschemaForm
  },
  mixins: [InteractionsToggle, Mapable],
  data: () => ({
    interactionType: "edit-interaction",
    selectedLayer: null,
    selectedFeatures: [],
    editableLayers: [],
    toggleSelection: undefined,
    toggleEdit: undefined,

    //Popup configuration
    popup: {
      title: "",
      isVisible: false,
      el: null,
      selectedInteraction: null
    },

    //Upload field.
    uploadRules: [
      value =>
        !value || value.size < 1000000 || "File size should be less than 1 MB!"
    ],

    //Edit form
    listValues: {},
    hiddenProps: ["userid", "id", "original_id", "class_id", "status"],
    schema: {},
    dataObject: {},
    formValid: false
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
      me.olEditCtrl.createEditLayer();
    },

    readFile(file) {
      if (file) {
        const reader = new FileReader();
        reader.readAsText(file);
        console.log(this.schema);
        reader.onload = function() {
          //STEPS
          //1- Check for size and other validations
          //2- Parse geojson data
          const result = reader.result;
          console.log(result);
          const features = geojsonToFeature(result, {
            dataProjection: "EPSG:4326"
          });
          console.log(features);
          //3- Check field names and geometry (fields should match and geometry type + crs have to be the same as the selected layer)
          //4- Push the features to FeaturesToCommit array
          //5- Transact using WFS
        };
        reader.onerror = function() {
          console.log(reader.error);
        };
      }
    },

    /**
     * Toggle the select interaction
     */
    toggleSelectInteraction(state) {
      const me = this;

      //Close other interactions.
      if (state != undefined) {
        EventBus.$emit("ol-interaction-activated", me.interactionType);
      } else {
        EventBus.$emit("ol-interaction-stoped", me.interactionType);
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
        case 0:
          editType = "add";
          startCb = this.onDrawStart;
          endCb = this.onDrawEnd;
          break;
        case 1:
          editType = "modify";
          startCb = this.onModifyStart;
          endCb = this.onModifyEnd;
          break;
        case 2:
          editType = "delete";
          break;
        default:
          break;
      }
      if (editType !== undefined) {
        me.olEditCtrl.addInteraction(editType, startCb, endCb);
        EventBus.$emit("ol-interaction-activated", me.interactionType);
      } else {
        me.olEditCtrl.removeInteraction();
        EventBus.$emit("ol-interaction-stoped", me.interactionType);
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
      this.olEditCtrl.featuresToCommit.push(feature);
      this.olEditCtrl.highlightSource.addFeature(feature);
      const featureCoordinates = feature.getGeometry().getCoordinates();
      const popupCoordinate = Array.isArray(featureCoordinates[0])
        ? featureCoordinates[0]
        : featureCoordinates;
      this.olEditCtrl.popupOverlay.setPosition(popupCoordinate);
      this.olEditCtrl.popup.title = "attributes";
      this.olEditCtrl.popup.selectedInteraction = "add";
      this.olEditCtrl.popup.isVisible = true;
    },

    /**
     * Changes ways type between road or bridge
     */
    updateSelectedWaysType(value) {
      editLayerHelper.selectedWayType = value;
    },

    /**
     * Get Layer attribute fields
     */
    getlayerFeatureTypes() {
      if (this.schema[this.layerName]) return;
      http
        .get(
          `geoserver/wfs?request=describeFeatureType&typename=${this.layerName}_modified&outputFormat=application/json`
        )
        .then(response => {
          const props = response.data.featureTypes[0].properties;
          const jsonSchema = mapFeatureTypeProps(
            props,
            this.hiddenProps,
            this.layerName.split(":")[1],
            this.listValues
          );
          this.schema[this.layerName] = jsonSchema;
        });
    },

    /**
     * Clears all the selection
     */
    clearSelection() {
      const me = this;
      me.olEditCtrl.clear();
      me.olSelectCtrl.clear();
    },

    uploadFeatures() {
      this.olEditCtrl.uploadFeatures();
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
     * Stop edit and select interactions (Doesn't deletes the features)
     */
    stop() {
      const me = this;
      me.olSelectCtrl.removeInteraction();
      me.olEditCtrl.removeInteraction();
      EventBus.$emit("ol-interaction-stoped", me.interactionType);
    },
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
    ok(type) {
      if (type === "add") {
        this.olEditCtrl.transact(this.dataObject);
        this.olEditCtrl.closePopup();
      } else {
        this.olEditCtrl.deleteFeature();
      }
    },
    cancel() {
      this.olEditCtrl.closePopup();
    }
  },
  computed: {
    layerName() {
      return this.selectedLayer.getSource().getParams().LAYERS;
    },
    options() {
      return {
        debug: false,
        disableAll: false,
        autoFoldObjects: true
      };
    }
  },
  created() {
    this.listValues = this.$appConfig.listValues;
    //Edge Case (get all pois keys)
    if (
      this.listValues.pois_info.amenity &&
      this.listValues.pois_info.amenity.values === "*"
    ) {
      const poisListValues = getPoisListValues(
        this.$appConfig.componentData.pois.allPois
      );
      this.listValues.pois_info.amenity.values = poisListValues;
    }
  }
};
</script>
