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
        <v-flex xs12 v-show="selectedLayer != null" class="mt-1 pt-0">
          <p>Tools</p>
          <v-btn-toggle rounded>
            <v-btn text>
              <v-icon>fas fa-plus</v-icon>
            </v-btn>
            <v-btn text>
              <v-icon>fas fa-pen</v-icon>
            </v-btn>
            <v-btn text>
              <v-icon>far fa-dot-circle</v-icon>
            </v-btn>
            <v-btn text>
              <v-icon>fas fa-trash-alt</v-icon>
            </v-btn>
          </v-btn-toggle>
        </v-flex>
      </v-card-text>
    </v-card>
  </v-flex>
</template>

<script>
import { Mapable } from "../../../mixins/Mapable";
import LayerUtils from "../../../utils/Layer";

export default {
  mixins: [Mapable],
  data: () => ({
    selectedLayer: null,
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

      console.log(me.editableLayers[0]);
    }
  }
};
</script>
