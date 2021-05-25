<template>
  <div>
    <draggable class="list-group" v-model="getVisibleLayers" :move="onMove">
      <div v-for="(item, i) in getVisibleLayers" :key="i">
        <v-flex xs12 style="padding: 10px; margin-left: 10px; cursor:pointer;">
          {{ translate("layerName", item.name) }}
        </v-flex>
        <v-divider></v-divider>
      </div>
    </draggable>
  </div>
</template>

<script>
import LayerTree from "../layerTree/LayerTree";
import draggable from "vuedraggable";

export default {
  mixins: [LayerTree],
  data: () => ({
    allLayers: []
  }),
  components: {
    draggable
  },
  computed: {
    getVisibleLayers: {
      //Get visible layers
      get: function() {
        return this.allLayers.filter(
          layer =>
            layer.mapLayer.getVisible() === true &&
            layer.mapLayer.get("group") !== "backgroundLayers"
        );
      },
      set: function() {
        this.sortLayerArray(this.allLayers);
      }
    }
  },
  created() {
    //Get list of all map layers
    for (let i = this.layers.length - 1; i >= 0; i--) {
      for (let j = this.layers[i].children.length - 1; j >= 0; j--) {
        this.allLayers.push(this.layers[i].children[j]);
      }
    }
  },
  methods: {
    sortLayerArray(layers) {
      //Sort layer arrays based on zIndex
      layers.sort((a, b) => (a.layerOrderKey > b.layerOrderKey ? -1 : 1));
    },
    onMove({ draggedContext, relatedContext }) {
      //Get dragged and target layers
      let draggedElement = draggedContext.element;
      let relatedElement = relatedContext.element;
      this.reOrderLayers(draggedElement, relatedElement);
    },
    reOrderLayers(draggedElement, relatedElement) {
      //Reorder the layers
      let start = draggedElement.layerOrderKey;
      let end = relatedElement.layerOrderKey;
      if (start > end) {
        for (let i = 0; i < this.allLayers.length; i++) {
          if (
            this.allLayers[i].layerOrderKey >= end &&
            this.allLayers[i].layerOrderKey < start
          ) {
            this.allLayers[i].mapLayer.setZIndex(
              this.allLayers[i].layerOrderKey + 1
            );
            this.allLayers[i].layerOrderKey += 1;
          }
        }
      } else if (start < end) {
        for (let i = 0; i < this.allLayers.length; i++) {
          if (
            this.allLayers[i].layerOrderKey > start &&
            this.allLayers[i].layerOrderKey <= end
          ) {
            this.allLayers[i].mapLayer.setZIndex(
              this.allLayers[i].layerOrderKey - 1
            );
            this.allLayers[i].layerOrderKey -= 1;
          }
        }
      }
      draggedElement.mapLayer.setZIndex(end);
      draggedElement.layerOrderKey = end;
    }
  }
};
</script>
