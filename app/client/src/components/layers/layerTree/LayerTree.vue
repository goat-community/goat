<template>
  <v-flex xs12 sm8 md4>
    <v-divider></v-divider>
    <vue-scroll>
      <v-tabs-items v-model="layerTabIndex">
        <v-tab-item :eager="true">
          <v-expansion-panels accordion multiple>
            <v-expansion-panel
              v-for="(layerGroup, i) in layerGroupsArr"
              :key="i"
              expand
            >
              <v-expansion-panel-header
                class="elevation-2"
                expand-icon=""
                v-slot="{ open }"
              >
                <v-layout row wrap align-center justify-space-between>
                  <v-flex xs1>
                    <v-icon small>{{
                      getLayerGroupIcon(layerGroup.name)
                    }}</v-icon>
                  </v-flex>
                  <v-flex xs8 class="light-text" style="font-size:medium;">
                    <div>
                      <b>{{ translate("layerGroup", layerGroup.name) }}</b>
                    </div>
                  </v-flex>
                  <v-flex>
                    <ImportExternalLayers
                      @getLayerInfo="layerInfoSubmited"
                      v-if="layerGroup.name === 'external_imports'"
                    />
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
                    v-for="(layer, i) in layerGroup.children"
                    :key="i"
                    class="layer-row"
                    :class="{
                      'expansion-panel__container--active':
                        layer.get('showOptions') === true
                    }"
                  >
                    <v-expansion-panel-header expand-icon="" v-slot="{}">
                      <v-layout row class="pl-1" wrap align-center>
                        <v-flex class="checkbox" xs1>
                          <v-simple-checkbox
                            :color="appColor.secondary"
                            :value="layer.getVisible()"
                            @input="
                              toggleLayerVisibility(layer, layerGroup.children)
                            "
                          ></v-simple-checkbox>
                        </v-flex>
                        <v-flex xs10 class="light-text">
                          <v-layout justify-space-between>
                            <h4 class="pl-2">
                              {{ translate("layerName", layer.get("name")) }}
                            </h4>

                            <v-icon
                              class="mr-2"
                              style="float: right; cursor: pointer;"
                              small
                              @click="deleteExternalLayer(layer)"
                              v-if="layer.get('group') === 'external_imports'"
                              >fas fa-trash-can</v-icon
                            >
                          </v-layout>
                        </v-flex>
                        <v-flex xs1>
                          <v-icon
                            v-show="
                              layer.getVisible() &&
                                layer.get('name') !== 'study_area'
                            "
                            small
                            style="width: 30px; height: 30px;"
                            v-html="
                              layer.get('showOptions')
                                ? 'fas fa-chevron-down'
                                : 'fas fa-chevron-up'
                            "
                            :class="{
                              'expansion-panel__container--active': layer.get(
                                'showOptions'
                              )
                            }"
                            @click.stop="toggleLayerOptions(layer)"
                          ></v-icon>
                        </v-flex>
                      </v-layout>
                    </v-expansion-panel-header>
                    <v-card
                      class="pt-2"
                      v-show="
                        layer.getVisible() &&
                          layer.get('showOptions') === true &&
                          layer.get('name') !== 'study_area'
                      "
                      style="background-color: white;"
                      transition="slide-y-reverse-transition"
                    >
                      <InLegend :layer="layer"></InLegend>
                      <v-layout row style="width:100%;padding-left: 10px;">
                        <v-flex
                          class="xs2"
                          style="text-align:center;"
                          v-if="
                            [
                              'VECTORTILE',
                              'VECTOR',
                              'MVT',
                              'GEOBUF',
                              'WMTS',
                              'WMS'
                            ].includes(layer.get('type').toUpperCase())
                          "
                        >
                          <v-icon
                            v-ripple
                            style="color:#B0B0B0;margin-top:3px;cursor:pointer"
                            dark
                            @click="openStyleDialog(layer)"
                          >
                            fas fa-cog
                          </v-icon>
                        </v-flex>
                        <v-flex
                          :class="{
                            xs10:
                              [
                                'VECTORTILE',
                                'VECTOR',
                                'MVT',
                                'GEOBUF',
                                'WMTS',
                                'WMS'
                              ].includes(layer.get('type').toUpperCase()) ==
                              true,
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
                </v-expansion-panels>
                <!-- ---- -->
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-tab-item>
        <v-tab-item :eager="true">
          <layer-order
            :map="map"
            :translate="translate"
            :toggleLayerOptions="toggleLayerOptions"
            :changeLayerOpacity="changeLayerOpacity"
            :layerGroupsArr="layerGroupsArr"
          ></layer-order>
        </v-tab-item>
      </v-tabs-items>
    </vue-scroll>
    <span v-if="styleDialogStatus">
      <style-dialog
        :item="currentItem"
        :translate="translate"
        :key="styleDialogKey"
        :styleDialogStatus="styleDialogStatus"
      >
      </style-dialog>
    </span>
  </v-flex>
</template>

<script>
//map and state imports
import { Mapable } from "../../../mixins/Mapable";
import { mapGetters } from "vuex";
import { mapFields } from "vuex-map-fields";
import { EventBus } from "../../../EventBus";

//component imports
import InLegend from "../../viewer/ol/controls/InLegend";
import LayerOrder from "../layerOrder/LayerOrder";
import StyleDialog from "../changeStyle/StyleDialog";
import Legend from "../../viewer/ol/controls/Legend";
import ImportExternalLayers from "../importLayers/ImportExternalLayers.vue";

//Openlayer imports
import TileLayer from "ol/layer/Tile";
import TileWMS from "ol/source/TileWMS";

export default {
  mixins: [Mapable, Legend],
  data() {
    return {
      layerGroupsArr: [],
      currentItem: null,
      styleDialogKey: 0,
      styleDialogStatus: false
    };
  },
  computed: {
    ...mapGetters("app", {
      appConfig: "appConfig",
      appColor: "appColor"
    }),
    ...mapFields("app", {
      layerTabIndex: "layerTabIndex"
    })
  },
  components: { LayerOrder, InLegend, StyleDialog, ImportExternalLayers },
  methods: {
    // Layer Import feature
    createExternalLayerGroup() {
      let currentConfig = this.appConfig;
      let imports = {
        external_imports: {
          children: [],
          icon: "fas fa-upload"
        }
      };
      currentConfig.layer_groups.push(imports);
      this.$store.commit("app/setAppConfig", currentConfig);
    },
    layerInfoSubmited({ data, currentHoveredLayer }) {
      if (currentHoveredLayer) {
        this.map.removeLayer(currentHoveredLayer);
      }
      let resultsfromThis = this.appConfig.layer_groups.map(lay => {
        return Object.keys(lay)[0];
      });
      if (!resultsfromThis.includes("external_imports")) {
        this.createExternalLayerGroup();
      }

      let newLayer = new TileLayer({
        source: new TileWMS({
          url: data.url,
          params: {
            layers: data.name
          },
          attribution: data.title
        }),
        group: "external_imports",
        name: data.title,
        visible: true,
        opacity: 1,
        type: "wmts",
        legendGraphicUrls: data.legendUrl,
        showOptions: true
      });

      if (this.layerGroupsArr.length === 5) {
        this.layerGroupsArr.forEach(layerGroup => {
          if (layerGroup.name === "external_imports") {
            let hasLayer = layerGroup.children.filter(
              layer => layer.get("name") === newLayer.get("name")
            );
            if (hasLayer.length === 0) {
              this.map.addLayer(newLayer);

              this.updateLayerArray();
            }
          }
        });
      } else {
        this.map.addLayer(newLayer);

        this.updateLayerArray();
      }
    },

    //updating the sidebar layers
    updateLayerGroups() {
      const layerGroups = this.appConfig.layer_groups;

      let externalGroup = layerGroups.filter(
        layer => Object.keys(layer)[0] === "external_imports"
      );
      if (externalGroup.length === 0) {
        this.createExternalLayerGroup();
      }

      layerGroups.forEach(lg => {
        const layerGroupName = Object.keys(lg)[0];
        if (layerGroupName !== "heatmap") {
          let newObject = {
            name: layerGroupName,
            children: []
          };
          this.layerGroupsArr.push(newObject);
        }
      });

      this.map
        .getLayers()
        .getArray()
        .forEach(layer => {
          if (layer.get("group") && layer.get("group") !== "heatmap") {
            this.layerGroupsArr.forEach((lay, idx) => {
              if (lay.name === layer.get("group")) {
                this.layerGroupsArr[idx].children.push(layer);
              }
            });
          }
        });
    },
    /*
     * This function is executed, after the map is bound (see mixins/Mapable)
     * and registers the current map layers.
     */
    onMapBound() {
      this.updateLayerGroups();
    },
    getLayerGroupIcon(group) {
      const layerGroupConf = this.appConfig.layer_groups.filter(g => g[group]);
      return layerGroupConf[0][group].icon || "fas fa-layer-group";
    },
    translate(type, key) {
      //Checks if key exists and translates it othewise return the input value
      const canTranslate = this.$te(`map.${type}.${key}`);
      if (canTranslate) {
        return this.$t(`map.${type}.${key}`);
      } else if (key === "external_imports") {
        return "External Layers";
      } else {
        return key;
      }
    },
    toggleLayerVisibility(layer, group) {
      const currentState = layer.getVisible();
      //Turn off other layers if layer group is background layers.
      if (layer.get("group") === "basemap") {
        group.forEach(layer => {
          layer.setVisible(false);
        });
      }
      layer.setVisible(!currentState);
      if (layer.getVisible() === false) {
        layer.set("showOptions", false);
      } else {
        layer.set("showOptions", true);
      }
      EventBus.$emit("toggleLayerVisiblity", layer);
    },
    toggleLayerOptions(layer) {
      layer.set("showOptions", !layer.get("showOptions"));
    },
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
    changeLayerOpacity(value, layer) {
      layer.setOpacity(value);
    },
    // Importing built in layers from a local js file
    preventDuplication(newlayer) {
      if (this.layerGroupsArr.length === 5) {
        this.layerGroupsArr.forEach(layerGroup => {
          if (layerGroup.name === "external_imports") {
            let hasLayer = layerGroup.children.filter(
              layer => layer.get("name") === newlayer.get("name")
            );
            if (hasLayer.length === 0) {
              this.map.addLayer(newlayer);
              this.updateLayerArray();
            }
          }
        });
      } else {
        this.map.addLayer(newlayer);
        this.updateLayerArray();
      }
    },
    deleteExternalLayer(layer) {
      this.map.removeLayer(layer);
      this.updateLayerArray();
    },
    updateLayerArray() {
      this.layerGroupsArr = [];
      this.updateLayerGroups();
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

.expansion-panel__container--active {
  background-color: white !important;
}

.checkbox >>> .v-input__control {
  height: 25px;
}

.v-expansion-panel-content >>> .v-expansion-panel-content__wrap {
  padding: 0px;
}

.v-expansion-panel-content >>> .v-input__slot {
  margin-bottom: 0px;
}

.layer-row >>> .v-expansion-panel-header {
  cursor: auto;
}
</style>
