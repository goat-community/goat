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
          v-for="(item, i) in getVisibleLayers"
          :key="i"
          class="layer-row"
          :disabled="isLayerBusy(item.mapLayer)"
          :class="{
            'expansion-panel__container--active': item.showOptions === true
          }"
        >
          <v-expansion-panel-header
            expand-icon=""
            v-slot="{}"
            :style="item.mapLayer.get('docUrl') ? 'overflow:hidden;' : ''"
            class="handle"
          >
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <div
                  v-on="on"
                  v-if="item.mapLayer.get('docUrl')"
                  class="documentation elevation-1"
                  @click.stop="openDocumentation(item)"
                >
                  <i class="info-icon fas fa-info fa-sm"></i>
                </div>
              </template>
              <span>{{ $t(`map.tooltips.openDocumentation`) }}</span>
            </v-tooltip>
            <v-layout row class="pl-1" wrap align-center>
              <v-flex class="checkbox" xs1>
                <v-simple-checkbox
                  v-if="item.name !== 'study_area_crop'"
                  :color="activeColor.primary"
                  :value="item.mapLayer.getVisible()"
                  @input="toggleLayerVisibility(item)"
                ></v-simple-checkbox>
              </v-flex>
              <v-flex xs10 class="light-text">
                <h4 class="pl-2">{{ translate("layerName", item.name) }}</h4>
              </v-flex>
              <v-flex xs1>
                <v-icon
                  v-if="item.name !== 'study_area_crop'"
                  v-show="item.mapLayer.getVisible()"
                  small
                  style="width: 30px; height: 30px;"
                  v-html="
                    item.showOptions === false
                      ? 'fas fa-chevron-down'
                      : 'fas fa-chevron-up'
                  "
                  :class="{
                    'expansion-panel__container--active':
                      item.showOptions === true
                  }"
                  @click.stop="toggleLayerOptions(item)"
                ></v-icon>
              </v-flex>
            </v-layout>
          </v-expansion-panel-header>
          <v-card
            class="pt-2"
            v-show="item.showOptions === true"
            style="background-color: white;"
            transition="slide-y-reverse-transition"
          >
            <InLegend
              :layerName="translate('layerName', item.name)"
              :item="item"
              :openStyleDialog="openStyleDialog"
            ></InLegend>
            <v-layout row style="width:100%;padding-left: 10px;">
              <v-flex
                class="xs2"
                style="text-align:center;"
                v-if="
                  ['VECTORTILE', 'VECTOR'].includes(
                    item.mapLayer.get('type')
                  ) && $appConfig.stylesObj[item.mapLayer.get('name')]
                "
              >
                <v-icon
                  v-ripple
                  @click="resetLayerStyle(item)"
                  class="toolbar-icons mr-2"
                  style="cursor: pointer"
                >
                  fas fa-sync-alt
                </v-icon>
              </v-flex>
              <v-flex
                :class="{
                  xs10:
                    ['VECTORTILE', 'VECTOR'].includes(
                      item.mapLayer.get('type')
                    ) == true &&
                    $appConfig.stylesObj[item.mapLayer.get('name')],
                  xs12: false
                }"
              >
                <v-slider
                  :value="item.mapLayer.getOpacity()"
                  class="mx-5"
                  step="0.05"
                  min="0"
                  max="1"
                  @input="changeLayerOpacity($event, item.mapLayer)"
                  :label="$t('layerTree.settings.transparency')"
                  color="#30C2FF"
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
        :ruleIndex="ruleIndex"
        @styleDialogStatus="styleDialogStatus = $event"
      >
      </StyleDialog>
    </span>
  </div>
</template>

<script>
// import LayerTree from "../layerTree/LayerTree";
import draggable from "vuedraggable";
import InLegend from "../../viewer/ol/controls/InLegend";
import StyleDialog from "../changeStyle/StyleDialog.vue";
import { EventBus } from "../../../EventBus";
import { mapGetters } from "vuex";

export default {
  // mixins: [LayerTree],
  props: [
    "layers",
    "translate",
    "isLayerBusy",
    "toggleLayerOptions",
    "changeLayerOpacity",
    "openDocumentation",
    "resetLayerStyle"
  ],
  data: () => ({
    allLayers: [],
    currentItem: {
      showOptions: false,
      name: ""
    },
    styleDialogKey: 0,
    styleDialogStatus: false,
    ruleIndex: undefined
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
            layer.mapLayer.getVisible() === true &&
            layer.mapLayer.get("group") !== "backgroundLayers"
        );
      },
      set: function() {
        //Sort layers in decreasing order based on zIndex
        this.sortLayerArray(this.allLayers);
      }
    },
    ...mapGetters("app", {
      activeColor: "activeColor"
    })
  },
  mounted() {
    EventBus.$on("updateStyleDialogStatusForLayerOrder", value => {
      this.styleDialogStatus = value;
    });

    //Get list of all map layers
    for (let i = this.layers.length - 1; i >= 0; i--) {
      for (let j = this.layers[i].children.length - 1; j >= 0; j--) {
        this.allLayers.push(this.layers[i].children[j]);
      }
    }
    this.sortLayerArray(this.allLayers);
  },
  methods: {
    openStyleDialog(item, ruleIndex) {
      //This function is used for opening Style Setting dialog component for a layer
      EventBus.$emit("updateStyleDialogStatusForLayerTree", false);
      this.styleDialogStatus = true;
      this.ruleIndex = ruleIndex;
      if (this.currentItem.name !== item.name) {
        this.styleDialogKey += 1;
      }
      if (
        this.currentItem.layerTreeKey >= 0 &&
        this.currentItem.name !== item.name
      ) {
        this.currentItem.layerTreeKey += 1;
      }
      this.currentItem = item;
    },
    sortLayerArray(layers) {
      //Sort layer arrays based on zIndex
      layers.sort((a, b) => (a.layerOrderKey > b.layerOrderKey ? -1 : 1));
    },
    toggleLayerVisibility(item) {
      item.mapLayer.setVisible(!item.mapLayer.getVisible());
      if (item.showOptions) {
        item.showOptions = false;
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

.documentation {
  content: "";
  position: absolute;
  top: -5px;
  right: -30px;
  height: 30px;
  width: 60px;
  opacity: 0.8;
  background: #2bb381;
  transform: rotate(45deg);
  z-index: 20;
  cursor: pointer;
}
.info-icon {
  position: absolute;
  top: 16px;
  left: 18px;
  color: white;
  -webkit-transform: rotate(-45deg);
  -moz-transform: rotate(-45deg);
  -ms-transform: rotate(-45deg);
  -o-transform: rotate(-45deg);
  transform: rotate(-45deg);
}
</style>
