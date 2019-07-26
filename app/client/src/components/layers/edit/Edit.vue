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
          <p class="mb-1">Select</p>
          <v-btn-toggle>
            <v-btn text @click="selectLayerFeatures('single')">
              <v-icon>far fa-hand-pointer</v-icon>
            </v-btn>
            <v-btn text @click="selectLayerFeatures('multiple')">
              <v-icon>far fa-dot-circle</v-icon>
            </v-btn>
          </v-btn-toggle>
        </v-flex>
        <v-flex xs12 v-show="selectedLayer != null" class="mt-1 pt-0">
          <p class="mb-1">Tools</p>
          <v-btn-toggle>
            <v-btn text>
              <v-icon medium>timeline</v-icon>
            </v-btn>
            <v-btn text>
              <v-icon>far fa-edit</v-icon>
            </v-btn>

            <v-btn text>
              <v-icon>far fa-trash-alt</v-icon>
            </v-btn>
          </v-btn-toggle>
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
  </v-flex>
</template>

<script>
import { Mapable } from "../../../mixins/Mapable";
import LayerUtils from "../../../utils/Layer";

import OlEditController from "./OlEditController";
import OlSelectController from "./OlSelectController";

export default {
  mixins: [Mapable],
  data: () => ({
    selectedLayer: null,
    selectedFeatures: [],
    editableLayers: []
  }),
  watch: {
    selectedLayer: value => {
      console.log(value);
    }
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
      //Initialize ol select and edit controllers.
      me.olSelectCtrl = new OlSelectController(me.map);
      me.olEditCtrl = new OlEditController(me.map);
    },
    selectLayerFeatures(type) {
      console.log(type);
    },
    clear() {}
  }
};
</script>
