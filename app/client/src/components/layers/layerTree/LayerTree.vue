<template>
  <v-flex xs12 sm8 md4>
    <vue-scroll>
      <v-tabs-items v-model="tab" id="tabItems">
        <v-tab-item :key="1" :eager="true">
          <v-expansion-panels accordion multiple>
            <v-expansion-panel
              v-for="(layerGroup, i) in layers"
              :key="i"
              expand
            >
              <v-expansion-panel-header
                class="elevation-2"
                expand-icon=""
                v-slot="{ open }"
              >
                <v-layout row wrap align-center>
                  <v-flex xs1>
                    <v-icon small>fas fa-layer-group</v-icon>
                  </v-flex>
                  <v-flex xs10>
                    <div>{{ translate("layerGroup", layerGroup.name) }}</div>
                  </v-flex>
                  <v-flex xs1>
                    <v-icon v-html="open ? 'remove' : 'add'"></v-icon>
                  </v-flex>
                </v-layout>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <!-- LAYERS -->
                <v-expansion-panels readonly>
                  <v-expansion-panel
                    v-for="(item, i) in layerGroup.children"
                    :key="i"
                    :disabled="isLayerBusy(item.mapLayer)"
                    :class="{
                      'expansion-panel__container--active':
                        item.showOptions === true
                    }"
                  >
                    <v-expansion-panel-header
                      expand-icon=""
                      @click="toggleLayerVisibility(item, layerGroup)"
                      :style="
                        item.mapLayer.get('docUrl') ? 'overflow:hidden;' : ''
                      "
                      v-slot="{}"
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

                      <v-layout row class="pl-2" wrap align-center>
                        <v-flex xs2>
                          <v-icon
                            :class="{
                              'active-icon':
                                item.mapLayer.getVisible() === true,
                              'expansion-panel__container--active':
                                item.showOptions === true
                            }"
                            >done</v-icon
                          >
                        </v-flex>
                        <v-flex xs9>
                          <span>{{ translate("layerName", item.name) }}</span>
                        </v-flex>
                        <v-flex xs1>
                          <v-icon
                            v-show="item.mapLayer.getVisible()"
                            small
                            style="width: 30px; height: 30px"
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
                      style="background-color: white"
                      transition="slide-y-reverse-transition"
                    >
                      <InLegend
                        :layerName="translate('layerName', item.name)"
                        :item="item"
                        :openStyleDialog="openStyleDialog"
                      ></InLegend>
                      <v-layout row style="width: 100%; padding-left: 10px">
                        <v-flex
                          class="xs2"
                          style="text-align: center"
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
                </v-expansion-panels>
                <!-- ---- -->
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
          <documentation-dialog
            :color="activeColor.primary"
            :visible="showDocumentationDialog"
            :item="selectedDocumentationItem"
            @close="showDocumentationDialog = false"
          ></documentation-dialog>
        </v-tab-item>
        <v-tab-item :key="2" :eager="true">
          <LayerOrder
            :layers="layers"
            :translate="translate"
            :isLayerBusy="isLayerBusy"
            :toggleLayerOptions="toggleLayerOptions"
            :changeLayerOpacity="changeLayerOpacity"
            :openDocumentation="openDocumentation"
            :resetLayerStyle="resetLayerStyle"
          ></LayerOrder>
        </v-tab-item>
      </v-tabs-items>
    </vue-scroll>
    <span v-if="styleDialogStatus">
      <StyleDialog
        :item="currentItem"
        :translate="translate"
        :key="styleDialogKey"
        :styleDialogStatus="styleDialogStatus"
        :ruleIndex="ruleIndex"
      >
      </StyleDialog>
    </span>
  </v-flex>
</template>

<script>
import { Mapable } from "../../../mixins/Mapable";
import { Group, Vector } from "ol/layer.js";
import { mapGetters, mapMutations } from "vuex";
import DocumentationDialog from "../../other/DocumentationDialog";
import { EventBus } from "../../../EventBus";
import Legend from "../../viewer/ol/controls/Legend";
import InLegend from "../../viewer/ol/controls/InLegend";
import LayerOrder from "../layerOrder/LayerOrder";
import StyleDialog from "../changeStyle/StyleDialog";

export default {
  mixins: [Mapable, Legend],
  data: () => ({
    layers: [],
    showDocumentationDialog: false,
    selectedDocumentationItem: null,
    layerOrderKey: 1,
    currentItem: {
      showOptions: false,
      name: ""
    },
    styleDialogKey: 0,
    styleDialogStatus: false,
    ruleIndex: undefined
  }),
  components: {
    DocumentationDialog,
    LayerOrder,
    InLegend,
    StyleDialog
  },
  computed: {
    ...mapGetters("pois", {
      selectedPois: "selectedPois"
    }),
    ...mapGetters("app", {
      activeColor: "activeColor",
      tab: "layerTabIndex"
    }),
    ...mapGetters("map", {
      busyLayers: "busyLayers"
    })
  },
  mounted() {
    EventBus.$on("updateStyleDialogStatusForLayerTree", value => {
      this.styleDialogStatus = value;
    });
  },
  methods: {
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     * and registers the current map layers.
     */
    isLayerBusy(treeLayer) {
      let isBusy = false;
      this.busyLayers.forEach(bl => {
        if (bl.get("name") === treeLayer.get("name")) {
          isBusy = true;
        }
      });
      return isBusy;
    },
    onMapBound() {
      const me = this;
      const localVectorLayers = {
        name: "Vector Layers",
        id: 100,
        isExpanded: [false],
        children: []
      };
      this.resetZIndex();
      me.map
        .getLayers()
        .getArray()
        .forEach((layer, index) => {
          let obj = me.getMapLayerObj(layer, index);
          if (
            layer instanceof Group &&
            layer.get("name") != "undefined" &&
            layer.get("name") != "osmMappingLayers"
          ) {
            me.layers.push(obj);
          } else if (
            layer instanceof Vector &&
            layer.get("name") != "undefined" &&
            layer.get("displayInLayerList") === true
          ) {
            localVectorLayers.children.push(obj);
          }
        });
      //Check if there are any vector layers currently in the map
      if (localVectorLayers.children.length > 0) {
        me.layers.push(localVectorLayers);
      }
    },
    getMapLayerObj(layer, index) {
      const me = this;
      const obj = {};
      if (layer instanceof Group) {
        obj.name = layer.get("name") ? layer.get("name") : "Layer Group";
        obj.id = index;
        obj.isExpanded = [true];
        obj.children = [];
        const layers = layer.getLayers().getArray();
        layers.forEach((layer, index) => {
          if (layer instanceof Group) {
            me.getMapLayerObj(layer);
          } else {
            if (layer.get("displayInLayerList")) {
              let layerOpt = {
                id: index,
                name: layer.get("name") || "Unnamed layer",
                showOptions: false,
                mapLayer: layer,
                layerTreeKey: 0,
                layerOrderKey: layer.getZIndex(),
                attributeDisplayStatusKey: 0,
                styleComponentResetKey: 0
              };
              obj.children.push(layerOpt);
            }
          }
        });
      } else if (layer instanceof Vector) {
        obj.id = index;
        obj.name = layer.get("name");
        obj.showOptions = false;
        obj.mapLayer = layer;
      }
      return obj;
    },
    resetZIndex() {
      let tempLayers = [];
      this.map
        .getLayers()
        .getArray()
        .forEach(g => {
          if (g.getLayers) {
            g.getLayers()
              .getArray()
              .forEach(l => {
                tempLayers.push(l);
              });
          } else {
            tempLayers.push(g);
          }
        });
      tempLayers.sort((a, b) => (a.getZIndex() < b.getZIndex() ? -1 : 1));
      tempLayers.forEach(layer => {
        if (layer.get("group") === "backgroundLayers") {
          layer.setZIndex(-1);
        } else {
          layer.setZIndex(this.layerOrderKey);
          this.layerOrderKey += 1;
        }
      });
    },
    doNothing() {},
    resetLayerStyle(item) {
      /*
        Function to reset the style of layer
      */
      //Get original style for layer
      let source = this.filterStylesOnActiveModeByLayerName(
        item.mapLayer.get("name"),
        true
      ).rules;

      //Get present style for layer
      let target = this.filterStylesOnActiveModeByLayerName(
        item.mapLayer.get("name")
      ).rules;
      let kind = source[0].symbolizers[0].kind;
      for (let i = 0; i < source.length; i++) {
        let sourceStyle = source[i];
        let targetStyle = target[i];
        if (kind === "Fill") {
          //Assign original style to present style to reset
          targetStyle.symbolizers[0].color = sourceStyle.symbolizers[0].color;
          targetStyle.symbolizers[0].outlineWidth =
            sourceStyle.symbolizers[0].outlineWidth;
          targetStyle.symbolizers[0].outlineColor =
            sourceStyle.symbolizers[0].outlineColor;
        } else if (kind === "Line") {
          //Assign original style to present style to reset
          targetStyle.symbolizers[0].color = sourceStyle.symbolizers[0].color;
          targetStyle.symbolizers[0].width = sourceStyle.symbolizers[0].width;
        } else if (kind === "Icon") {
          //Assign original style to present style to reset
          targetStyle.symbolizers[0].size = sourceStyle.symbolizers[0].size;
          targetStyle.symbolizers[0].image = sourceStyle.symbolizers[0].image;
        }
      }
      item.mapLayer.getSource().changed();
      item.styleComponentResetKey += 1;
      item.layerTreeKey += 1;
    },
    openStyleDialog(item, ruleIndex) {
      //This function is used for opening Style Setting dialog component for a layer
      EventBus.$emit("updateStyleDialogStatusForLayerOrder", false);
      this.styleDialogStatus = true;
      this.ruleIndex = ruleIndex;
      this.currentItem.layerTreeKey += 1;
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
    toggleLayerVisibility(clickedLayer, layerGroup) {
      //Turn off other layers if layer group is background layers.
      if (
        layerGroup.name === "backgroundLayers" ||
        layerGroup.name === "accessbilityBasemaps"
      ) {
        layerGroup.children.forEach(layer => {
          if (layer.id === clickedLayer.id) return;
          layer.showOptions = false;
          layer.mapLayer.setVisible(false);
        });
      }
      if (layerGroup.name === "accessbilityBasemaps") {
        this.toggleSnackbar({
          type: "error",
          message: "selectAmenities",
          state: false,
          timeout: 0
        });
      }
      if (
        clickedLayer.mapLayer.get("requiresPois") === true &&
        this.selectedPois.length === 0
      ) {
        if (clickedLayer.mapLayer.getVisible() === false) {
          this.toggleSnackbar({
            type: "error",
            message: "selectAmenities",
            state: true,
            timeout: 60000
          });
        }
      }
      clickedLayer.mapLayer.setVisible(!clickedLayer.mapLayer.getVisible());
      if (clickedLayer.mapLayer.getVisible() === false) {
        clickedLayer.showOptions = false;
      }
      EventBus.$emit("toggleLayerVisiblity", clickedLayer.mapLayer);
    },
    openDocumentation(item) {
      this.showDocumentationDialog = true;
      this.selectedDocumentationItem = item;
    },
    toggleLayerOptions(item) {
      item.showOptions = !item.showOptions;
    },
    changeLayerOpacity(value, layer) {
      layer.setOpacity(value);
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
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
    })
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

.expansion-panel__container--active {
  background-color: #2bb381 !important;
  color: white !important;
}

.v-expansion-panel-content >>> .v-expansion-panel-content__wrap {
  padding: 0px;
}

.v-expansion-panel-content >>> .v-input__slot {
  margin-bottom: 0px;
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
