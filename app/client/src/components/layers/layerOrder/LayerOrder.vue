<template>
  <div>
    <v-expansion-panels readonly>
      <draggable
        v-model="getVisibleLayers"
        :move="onMove"
        style="width:100%;"
        handle=".handle"
      >
        <v-expansion-panel
          v-for="(layer, i) in getVisibleLayers"
          :key="i"
          class="layer-row"
          :class="{
            'expansion-panel__container--active':
              layer.get('showOptions') === true
          }"
        >
          <v-expansion-panel-header expand-icon="" v-slot="{}" class="handle">
            <v-layout row class="pl-1" wrap align-center>
              <v-flex class="checkbox" xs1>
                <v-simple-checkbox
                  :color="appColor.primary"
                  :value="layer.getVisible()"
                  @input="toggleLayerVisibility(layer)"
                ></v-simple-checkbox>
              </v-flex>
              <v-flex xs10 class="light-text">
                <h4 class="pl-2">
                  {{ translate("layerName", layer.get("name")) }}
                </h4>
              </v-flex>
              <v-flex xs1>
                <v-icon
                  v-show="
                    layer.getVisible() && layer.get('name') !== 'study_area'
                  "
                  small
                  style="width: 30px; height: 30px;"
                  v-html="
                    layer.get('showOptions') === false
                      ? 'fas fa-chevron-down'
                      : 'fas fa-chevron-up'
                  "
                  :class="{
                    'expansion-panel__container--active':
                      layer.get('showOptions') === true
                  }"
                  @click.stop="toggleLayerOptions(layer)"
                ></v-icon>
              </v-flex>
            </v-layout>
          </v-expansion-panel-header>
          <v-card
            class="pt-2"
            v-show="
              layer.get('showOptions') === true &&
                layer.get('name') !== 'study_area'
            "
            style="background-color: white;"
            transition="slide-y-reverse-transition"
          >
            <InLegend
              v-if="layer.get('showOptions') === true"
              :layer="layer"
            ></InLegend>
            <v-layout row style="width:100%;padding-left: 10px;">
              <v-flex
                class="xs2"
                style="text-align:center;"
                v-if="
                  ['VECTORTILE', 'VECTOR', 'MVT'].includes(
                    layer.get('type').toUpperCase()
                  )
                "
              >
                <v-icon
                  v-ripple
                  style="color:#B0B0B0;margin-top:3px;cursor:pointer"
                  dark
                  @click="openStyleDialog(item)"
                >
                  fas fa-cog
                </v-icon>
              </v-flex>
              <v-flex
                :class="{
                  xs10:
                    ['VECTORTILE', 'VECTOR', 'MVT'].includes(
                      layer.get('type').toUpperCase()
                    ) == true,
                  xs12: false
                }"
              >
                <v-slider
                  :value="layer.getOpacity()"
                  class="mx-5"
                  step="0.05"
                  min="0"
                  max="1"
                  @input="changeLayerOpacity($event, layer)"
                  :label="$t('layerTree.settings.transparency')"
                  :color="appColor.secondary"
                ></v-slider>
              </v-flex>
            </v-layout>
          </v-card>
        </v-expansion-panel>
        <v-divider></v-divider>
      </draggable>
    </v-expansion-panels>
    <span v-if="styleDialogStatus">
      <StyleDialog
        :item="currentItem"
        :translate="translate"
        :key="styleDialogKey"
        :styleDialogStatus="styleDialogStatus"
        @styleDialogStatus="styleDialogStatus = $event"
      >
      </StyleDialog>
    </span>
  </div>
</template>

<script>
import draggable from "vuedraggable";
import InLegend from "../../viewer/ol/controls/InLegend";
import StyleDialog from "../changeStyle/StyleDialog.vue";
import { EventBus } from "../../../EventBus";
import { mapGetters } from "vuex";

export default {
  props: ["map", "translate", "toggleLayerOptions", "changeLayerOpacity"],
  data: () => ({
    allLayers: [],
    currentItem: {
      showOptions: false,
      name: ""
    },
    styleDialogKey: 0,
    styleDialogStatus: false
  }),
  components: {
    draggable,
    InLegend,
    StyleDialog
  },
  computed: {
    getVisibleLayers: {
      //Get visible layers
      get: function() {
        return this.allLayers.filter(
          layer =>
            layer.getVisible() === true &&
            !["basemap", "heatmap"].includes(layer.get("group"))
        );
      },
      set: function() {
        //Sort layers in decreasing order based on zIndex
        this.sortLayerArray(this.allLayers);
      }
    },
    ...mapGetters("app", {
      appColor: "appColor"
    })
  },
  created() {
    //Get list of all map layers
    this.allLayers = this.map
      .getLayers()
      .getArray()
      .filter(l => l.get("type") && l.get("displayInLayerList") !== false);
  },
  mounted() {
    EventBus.$on("updateStyleDialogStatusForLayerOrder", value => {
      this.styleDialogStatus = value;
    });
  },
  methods: {
    openStyleDialog(item) {
      //This function is used for opening Style Setting dialog component for a layer
      EventBus.$emit("updateStyleDialogStatusForLayerOrder", false);
      this.styleDialogStatus = true;
      if (
        this.currentItem &&
        this.currentItem.get("name") !== item.get("name")
      ) {
        this.styleDialogKey += 1;
      }
      if (
        this.currentItem &&
        this.currentItem.get("layerTreeKey") >= 0 &&
        this.currentItem.get("name") !== item.get("name")
      ) {
        this.currentItem.set(
          "layerTreeKey",
          this.currentItem.get("layerTreeKey") + 1
        );
      }
      this.currentItem = item;
    },
    sortLayerArray(layers) {
      //Sort layer arrays based on zIndex
      layers.sort((a, b) => (a.layerOrderKey > b.layerOrderKey ? -1 : 1));
    },
    toggleLayerVisibility(layer) {
      layer.setVisible(!layer.getVisible());
      if (layer.get("showOptions")) {
        layer.set("showOptions", false);
      }
    },
    onMove({ draggedContext, relatedContext }) {
      //Get dragged and target layers on item move event
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
<style lang="css" scoped>
.v-expansion-panel__header {
  cursor: default;
}
.active-icon {
  color: #30c2ff;
}

.v-expansion-panel-content >>> .v-expansion-panel-content__wrap {
  padding: 0px;
}

.v-expansion-panel-content >>> .v-input__slot {
  margin-bottom: 0px;
}

.checkbox >>> .v-input__control {
  height: 25px;
}

.layer-row >>> .v-expansion-panel-header {
  cursor: auto;
}
</style>
