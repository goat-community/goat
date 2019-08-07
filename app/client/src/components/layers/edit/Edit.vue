<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-subheader>
        <span class="title">Edit</span>
      </v-subheader>
      <v-card-text class="pr-16 pl-16 pt-0 pb-0">
        <v-divider></v-divider>

        <v-select
          class="mt-4"
          :items="editableLayers"
          v-model="selectedLayer"
          item-text="values_.title"
          item-value="values_.name"
          return-object
          solo
          label="Layer to edit"
        >
        </v-select>
        <v-divider></v-divider>
        <v-flex xs12 v-show="selectedLayer != null" class="mt-1 pt-0 mb-4">
          <p class="mb-1">Select features</p>
          <v-btn-toggle v-model="toggleSelection">
            <v-btn text>
              <v-icon>far fa-dot-circle</v-icon>
            </v-btn>
            <v-btn text v-show="false">
              <v-icon>far fa-hand-pointer</v-icon>
            </v-btn>
          </v-btn-toggle>
        </v-flex>
        <v-flex xs12 v-show="selectedLayer != null" class="mt-1 pt-0">
          <v-divider class="mb-1"></v-divider>
          <p class="mb-1">Edit Tools</p>
          <v-btn-toggle v-model="toggleEdit">
            <v-btn text>
              <v-icon medium>add</v-icon>
            </v-btn>
            <v-btn text>
              <v-icon>far fa-edit</v-icon>
            </v-btn>
            <v-btn text>
              <v-icon>far fa-trash-alt</v-icon>
            </v-btn>
          </v-btn-toggle>
          <v-divider class="mt-4"></v-divider>
        </v-flex>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          v-show="selectedLayer != null"
          class="white--text"
          color="green"
          @click="clear"
        >
          Clear
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
          <b>Are you sure you want to delete the selected feature ?</b>
        </div>
        <div v-else-if="popup.selectedInteraction === 'add'">
          <span>Select way type: </span>
          <v-select
            :items="waysTypes.values"
            item-text="display"
            item-value="value"
            v-model="waysTypes.active"
            @change="updateSelectedWaysType"
            label="Way Type"
            solo
            required
            class="pt-2 ma-0"
          ></v-select>
        </div>
      </template>
      <template v-slot:actions>
        <template v-if="popup.selectedInteraction === 'delete'">
          <v-btn
            color="primary darken-1"
            @click="olEditCtrl.deleteFeature()"
            text
            >Yes</v-btn
          >
          <v-btn color="grey" text @click="olEditCtrl.closePopup()"
            >Cancel</v-btn
          >
        </template>
        <template v-else-if="popup.selectedInteraction === 'add'">
          <v-btn
            color="primary darken-1"
            @click="olEditCtrl.commitFeature()"
            text
            >Save</v-btn
          >
          <v-btn color="grey" text @click="olEditCtrl.closePopup()"
            >Cancel</v-btn
          >
        </template>
      </template>
    </overlay-popup>
  </v-flex>
</template>

<script>
import { EventBus } from "../../../EventBus";
import { Mapable } from "../../../mixins/Mapable";
import { InteractionsToggle } from "../../../mixins/InteractionsToggle";
import LayerUtils from "../../../utils/Layer";

import OlEditController from "../../../controllers/OlEditController";
import OlSelectController from "../../../controllers/OlSelectController";

import OlWaysLayerHelper from "../../../controllers/OlWaysLayerHelper";

import Overlay from "../../ol/Overlay";
import WaysLayerHelper from "../../../controllers/OlWaysLayerHelper";

export default {
  components: {
    "overlay-popup": Overlay
  },
  mixins: [InteractionsToggle, Mapable],
  data: () => ({
    interactionType: "edit-interaction",
    selectedLayer: null,
    selectedFeatures: [],
    editableLayers: [],
    toggleSelection: undefined,
    toggleEdit: undefined,
    popup: {
      title: "",
      isVisible: false,
      el: null,
      selectedInteraction: null
    },
    waysTypes: {
      values: [
        { display: "Bridge", value: "bridge" },
        { display: "Road", value: "road" }
      ],
      active: "road"
    }
  }),
  watch: {
    selectedLayer: value => {
      console.log(value);
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
      const editableLayers = LayerUtils.getAllChildLayers(me.map).filter(
        layer => layer.get("canEdit")
      );
      me.editableLayers = [...editableLayers];

      //Initialize ol select controllers.
      me.olSelectCtrl = new OlSelectController(me.map);
      me.olSelectCtrl.createSelectionLayer();

      //Initialize ol edit controller
      me.olEditCtrl = new OlEditController(me.map);
      me.olEditCtrl.createEditLayer();
    },

    /**
     * Toggle the select interaction
     */
    toggleSelectInteraction(state) {
      const me = this;

      //Close other interactions.
      EventBus.$emit("ol-interaction-activated", me.interactionType);

      let selectionType;
      switch (state) {
        case 0:
          selectionType = "single";
          break;
        case 1:
          selectionType = "multiple";
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

      let editType;
      switch (state) {
        case 0:
          editType = "add";
          break;
        case 1:
          editType = "modify";
          break;
        case 2:
          editType = "delete";
          break;
        default:
          break;
      }
      if (editType !== undefined) {
        me.olEditCtrl.addInteraction(editType);
      } else {
        me.olEditCtrl.removeInteraction();
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
        //Selected layer is the road network (ways)
        OlWaysLayerHelper.filterResults(
          response,
          me.olEditCtrl.getLayerSource()
        );
      } else {
        console.log(response);
      }
    },

    /**
     * Changes ways type between road or bridge
     */
    updateSelectedWaysType(value) {
      WaysLayerHelper.selectedWayType = value;
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
    }
  }
};
</script>
