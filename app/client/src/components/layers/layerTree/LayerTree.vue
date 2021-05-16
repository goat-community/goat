<template>
  <v-flex xs12 sm8 md4>
    <v-divider></v-divider>

    <v-expansion-panels accordion multiple>
      <v-expansion-panel v-for="(layerGroup, i) in layers" :key="i" expand>
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
                'expansion-panel__container--active': item.showOptions === true
              }"
            >
              <v-expansion-panel-header
                expand-icon=""
                @click="toggleLayerVisibility(item, layerGroup)"
                :style="item.mapLayer.get('docUrl') ? 'overflow:hidden;' : ''"
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
                        'active-icon': item.mapLayer.getVisible() === true,
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
                <div v-if="item.mapLayer.get('legendGraphicUrl')">
                  <img
                    crossorigin="anonymous"
                    style="max-width:100%;padding-left:50px"
                    :src="item.mapLayer.get('legendGraphicUrl')"
                    class="white--text mt-0 pt-0"
                  />
                </div>
                <div v-else>
                  <div v-if="item.mapLayer.get('type') === 'WMS'">
                    <template
                      v-for="(layerName, index2) in item.mapLayer
                        .getSource()
                        .getParams()
                        .LAYERS.split(',')"
                    >
                      <div :key="index2">
                        <img
                          crossorigin="anonymous"
                          style="max-width:100%; padding-left:50px;"
                          :src="getWMSLegendImageUrl(item.mapLayer, layerName)"
                          class="white--text mt-0 pt-0"
                        />
                        <br />
                      </div>
                    </template>
                  </div>
                  <div :key="legendRerenderOnActiveMode">
                    <div
                      v-if="
                        ['VECTORTILE', 'VECTOR'].includes(
                          item.mapLayer.get('type')
                        ) && styleRules[item.mapLayer.get('name')]
                      "
                      style="text-align: center; padding: 20px;"
                      :key="item.layerTreeKey"
                    >
                      <div v-if="styleRules[item.mapLayer.get('name')]">
                        <v-layout
                          v-for="(rule,
                          ith) in filterStylesOnActiveModeByLayerName(
                            item.mapLayer.get('name')
                          ).rules"
                          :key="ith"
                          class="pl-2"
                          row
                          wrap
                          align-center
                        >
                          <v-flex
                            xs1
                            v-if="
                              filterStylesOnActiveModeByLayerName(
                                item.mapLayer.get('name')
                              ).rules[ith].symbolizers[0].kind === `Fill`
                            "
                          >
                            <FillVectorStyle :item="item" :ruleIndex="ith">
                            </FillVectorStyle>
                          </v-flex>
                          <v-flex
                            xs1
                            v-else-if="
                              filterStylesOnActiveModeByLayerName(
                                item.mapLayer.get('name')
                              ).rules[ith].symbolizers[0].kind === `Line`
                            "
                          >
                            <LineVectorStyle :item="item" :ruleIndex="ith">
                            </LineVectorStyle>
                          </v-flex>
                          <v-flex
                            xs1
                            v-else-if="
                              filterStylesOnActiveModeByLayerName(
                                item.mapLayer.get('name')
                              ).rules[ith].symbolizers[0].kind === `Icon`
                            "
                          >
                            <IconVectorStyle :item="item" :ruleIndex="ith">
                            </IconVectorStyle>
                          </v-flex>
                          <v-flex xs1>
                            <v-checkbox
                              v-if="
                                filterStylesOnActiveModeByLayerName(
                                  item.mapLayer.get('name')
                                ).rules.length > 1
                              "
                              color="success"
                              :input-value="isLayerAttributeVisible(item, ith)"
                              @change="
                                attributeLevelRendering(
                                  styleRules[item.mapLayer.get('name')].style
                                    .rules[ith].filter[0],
                                  item,
                                  ith
                                )
                              "
                            >
                            </v-checkbox>
                          </v-flex>
                          <v-flex xs10>
                            <span
                              class="justify-start"
                              style="padding-right: 50px"
                              :ref="`legend-vector-${item.name + ith}`"
                              v-html="renderLegend(item, ith)"
                            >
                            </span>
                          </v-flex>
                        </v-layout>
                        <!-- {{styleRules[item.mapLayer.get("name")].style.rules}} -->
                      </div>
                    </div>
                  </div>
                </div>
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
  </v-flex>
</template>

<script>
import { Mapable } from "../../../mixins/Mapable";
import { Group, Vector } from "ol/layer.js";
import { mapGetters, mapMutations } from "vuex";
import DocumentationDialog from "../../other/DocumentationDialog";
import { EventBus } from "../../../EventBus";
import LegendRenderer from "../../../utils/LegendRenderer";
import Legend from "../../viewer/ol/controls/Legend";
import FillVectorStyle from "../changeStyle/FillVectorStyle";
import LineVectorStyle from "../changeStyle/LineVectorStyle";
import IconVectorStyle from "../changeStyle/IconVectorStyle";

export default {
  mixins: [Mapable, Legend],
  data: () => ({
    layers: [],
    styleRules: null,
    showDocumentationDialog: false,
    selectedDocumentationItem: null,
    legendRerenderOnActiveMode: 0
  }),
  components: {
    DocumentationDialog,
    FillVectorStyle,
    LineVectorStyle,
    IconVectorStyle
  },
  computed: {
    ...mapGetters("pois", {
      selectedPois: "selectedPois"
    }),
    ...mapGetters("app", {
      activeColor: "activeColor"
    }),
    ...mapGetters("map", {
      busyLayers: "busyLayers"
    })
  },
  watch: {
    //Rerendering the legend part when calculationModes value changes
    "calculationOptions.calculationModes.active": function() {
      this.legendRerenderOnActiveMode += 1;
    }
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
          //Deep copying the styleobj
          me.styleRules = JSON.parse(JSON.stringify(me.$appConfig.stylesObj));
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
                layerTreeKey: 0
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
    doNothing() {},
    isLayerAttributeVisible(item, ith) {
      //Checkbox will be checked or unchecked based on layer attribute visibility.
      const name = item.mapLayer.get("name");
      const attributeStyle = this.filterStylesOnActiveModeByLayerName(name)
        .rules[ith].filter[0];
      if (!attributeStyle) {
        return false;
      }
      return true;
    },
    attributeLevelRendering(filter, item, ith) {
      //Display or hide layer on attribute level.
      const name = item.mapLayer.get("name");
      const styleFilter = this.filterStylesOnActiveModeByLayerName(name).rules[
        ith
      ];
      if (styleFilter.filter[0]) {
        styleFilter.filter[0] = "";
      } else {
        styleFilter.filter[0] = filter;
      }
      item.mapLayer.getSource().changed();
    },
    renderLegend(item, index) {
      //Render individual legend on attribue level.
      setTimeout(() => {
        item = item.mapLayer;
        const styleObj = this.$appConfig.stylesObj;
        const name = item.get("name");
        let styleTranslation = this.$appConfig.stylesObj[name].translation;
        const currentLocale = this.$i18n.locale;
        if (styleObj[name] && styleObj[name].format === "geostyler") {
          let el = this.$refs[`legend-vector-${name + index}`];
          el = el ? el : [];
          if (el.length) {
            if (Array.isArray(el) && el.length > 0) {
              el = el[0];
            }
            // Remove existing svg elements on update (Workaround)
            if (el && el.childNodes.length > 0) {
              el.removeChild(el.childNodes[0]);
            }
            const style = this.filterStylesOnActiveModeByLayerName(name);
            let iStyle = style.rules[index];
            const renderer = new LegendRenderer({
              maxColumnWidth: 240,
              overflow: "auto",
              styles: [
                {
                  name: style.name,
                  rules: [iStyle]
                }
              ],
              size: [230, 300],
              translation: { styleTranslation, currentLocale }
            });
            renderer.render(el);
          }
        }
      }, 100);
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
