<template>
  <v-flex xs12 sm8 md4>
    <vue-scroll>
      <template>
        <!-- HEATMAP LAYERS -->
        <v-expansion-panels accordion multiple v-model="heatmapPanel">
          <v-expansion-panel
            v-for="(layerGroupValue, layerGroupKey) in heatmapGroup"
            :key="layerGroupKey"
            expand
          >
            <v-expansion-panel-header
              class="elevation-2"
              expand-icon=""
              v-slot="{ open }"
            >
              <v-layout row wrap align-center>
                <v-flex xs1>
                  <img
                    height="20"
                    width="20"
                    class="mr-3"
                    src="img/layer-style-icons/hexagon.svg"
                  />
                </v-flex>
                <v-flex xs10 class="light-text" style="font-size:medium;">
                  <div>
                    <b>{{ translate("layerGroup", layerGroupKey) }}</b>
                  </div>
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
                  v-for="(layer, i) in layerGroupValue"
                  :key="i"
                  :disabled="isHeatmapDisabled(layer)"
                  class="layer-row"
                  :style="{
                    backgroundColor: isHeatmapDisabled(layer)
                      ? '#ECECEC'
                      : '#ffffff'
                  }"
                  :class="{
                    'expansion-panel__container--active':
                      layer.get('showOptions') === true
                  }"
                >
                  <v-expansion-panel-header expand-icon="" v-slot="{}">
                    <v-layout row class="pl-1" wrap align-center>
                      <v-flex class="checkbox" xs1>
                        <v-checkbox
                          :color="appColor.secondary"
                          :input-value="layer.getVisible()"
                          @change="
                            toggleLayerVisibility(layer, layerGroupValue)
                          "
                        ></v-checkbox>
                      </v-flex>
                      <v-flex xs10 class="light-text">
                        <h4 class="pl-2">
                          {{ translate("layerName", layer.get("name")) }}
                        </h4>
                      </v-flex>
                      <v-flex xs1>
                        <v-icon
                          v-show="layer.getVisible()"
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
                          @click.stop="toggleHeatmapOptions(layer)"
                        ></v-icon>
                      </v-flex>
                    </v-layout>
                  </v-expansion-panel-header>
                  <!-- --- -->
                  <!-- LAYER LEGEND AND SETTINGS  -->
                  <v-card
                    class="pt-2"
                    v-show="layer.get('showOptions') === true"
                    style="background-color: white;"
                    transition="slide-y-reverse-transition"
                  >
                    <InLegend :layer="layer"></InLegend>
                    <v-layout row style="width:100%;padding-left: 10px;">
                      <v-flex
                        class="xs2"
                        style="text-align:center;"
                        v-if="
                          ['VECTORTILE', 'VECTOR', 'MVT', 'GEOBUF'].includes(
                            layer.get('type').toUpperCase()
                          )
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
                            ['VECTORTILE', 'VECTOR', 'MVT', 'GEOBUF'].includes(
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
                  <!-- --- -->
                </v-expansion-panel>
              </v-expansion-panels>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </template>
      <v-card-actions v-if="unCalculatedDataUploadIds.length > 0">
        <v-spacer></v-spacer>
        <v-btn
          :loading="isRecomputingHeatmap"
          class="white--text"
          @click="recomputeHeatmaps"
          :color="appColor.primary"
        >
          <v-icon left>fas fa-refresh</v-icon
          >{{ $t("heatmaps.recomputeHeatmap") }}</v-btn
        >
      </v-card-actions>
    </vue-scroll>
    <span v-if="styleDialogStatus">
      <StyleDialog
        :item="currentItem"
        :translate="translate"
        :key="styleDialogKey"
        :styleDialogStatus="styleDialogStatus"
      ></StyleDialog>
    </span>
  </v-flex>
</template>
<script>
import { mapGetters, mapMutations } from "vuex";
import { EventBus } from "../../EventBus";
import { Mapable } from "../../mixins/Mapable";
import { mapFields } from "vuex-map-fields";
import Legend from "../viewer/ol/controls/Legend";
import LayerTree from "../layers/layerTree/LayerTree";
import StyleDialog from "../layers/changeStyle/StyleDialog.vue";
import InLegend from "../viewer/ol/controls/InLegend.vue";
import ApiService from "../../services/api.service";
import { GET_USER_CUSTOM_DATA } from "../../store/actions.type";

export default {
  mixins: [Mapable, Legend, LayerTree],
  components: {
    InLegend,
    StyleDialog
  },
  data: () => ({
    heatmapPanel: [0],
    heatmapGroup: {},
    interactionType: "heatmap-interaction",
    heatmapsWithPois: [
      "heatmap_accessibility_population",
      "heatmap_local_accessibility"
    ],

    updateHeatmaps: {
      poi: ["heatmap_local_accessibility", "heatmap_accessibility_population"],
      population: ["heatmap_accessibility_population", "heatmap_population"]
    },
    currentItem: null,
    styleDialogKey: 0,
    styleDialogStatus: false
  }),

  mounted() {
    EventBus.$on("updateStyleDialogStatusForLayerOrder", value => {
      this.styleDialogStatus = value;
    });
  },
  computed: {
    ...mapGetters("app", {
      appColor: "appColor",
      appConfig: "appConfig",
      calculationMode: "calculationMode",
      unCalculatedDataUploadIds: "unCalculatedDataUploadIds"
    }),
    ...mapGetters("poisaois", {
      selectedPoisOnlyKeys: "selectedPoisOnlyKeys"
    }),
    ...mapGetters("scenarios", {
      activeScenario: "activeScenario"
    }),
    ...mapFields("map", {
      heatmapCancelToken: "heatmapCancelToken"
    }),
    ...mapFields("app", {
      isRecomputingHeatmap: "isRecomputingHeatmap"
    })
  },
  methods: {
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
    }),
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     * and registers the current map layers.
     */
    onMapBound() {
      this.map
        .getLayers()
        .getArray()
        .forEach(layer => {
          if (layer.get("group") && layer.get("group") === "heatmap") {
            if (!this.heatmapGroup[layer.get("group")]) {
              this.heatmapGroup[layer.get("group")] = [];
            }
            layer.set("attributeDisplayStatusKey", 0);
            this.heatmapGroup[layer.get("group")].push(layer);
          }
        });
      EventBus.$on("update-heatmap", updateHeatmapsLinkedTo => {
        this.refreshHeatmap(updateHeatmapsLinkedTo);
      });
    },
    toggleHeatmapOptions(layer) {
      layer.set("showOptions", !layer.get("showOptions"));
    },
    translate(type, key) {
      const canTranslate = this.$te(`map.${type}.${key}`);
      if (canTranslate) {
        return this.$t(`map.${type}.${key}`);
      } else {
        return key;
      }
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
    toggleLayerVisibility(layer, group) {
      if (this.heatmapCancelToken instanceof Function) {
        this.heatmapCancelToken("cancelled");
        this.heatmapCancelToken = null;
      }
      //Turn off other heatmaps if layer group is heatmap.
      if (layer.get("group") === "heatmap") {
        group.forEach(lc => {
          if (lc.get("name") === layer.get("name")) return;
          lc.setVisible(false);
          lc.set("showOptions", false);
        });
      }
      layer.setVisible(!layer.getVisible());
      if (layer.getVisible() === false) {
        layer.set("showOptions", false);
      } else {
        if (this.heatmapCancelToken instanceof Function) {
          this.heatmapCancelToken("cancelled");
          this.heatmapCancelToken = null;
        }
        layer.getSource().refresh();
        this.checkIfHeatmapNeedsPois(layer);
        layer.set("showOptions", true);
      }
    },
    refreshAllVisibleHeatmaps() {
      this.heatmapGroup["heatmap"].forEach(layer => {
        if (layer.getVisible()) {
          this.checkIfHeatmapNeedsPois(layer);
          if (this.heatmapCancelToken instanceof Function) {
            this.heatmapCancelToken("cancelled");
            this.heatmapCancelToken = null;
          }
          layer.getSource().refresh();
        }
      });
    },
    refreshHeatmap(update) {
      if (this.heatmapCancelToken instanceof Function) {
        this.heatmapCancelToken("cancelled");
        this.heatmapCancelToken = null;
      }
      if (this.updateHeatmaps[update]) {
        this.updateHeatmaps[update].forEach(heatmapName => {
          this.heatmapGroup["heatmap"].forEach(layer => {
            if (layer.get("name") === heatmapName && layer.getVisible()) {
              this.checkIfHeatmapNeedsPois(layer);
              if (this.heatmapCancelToken instanceof Function) {
                this.heatmapCancelToken("cancelled");
                this.heatmapCancelToken = null;
              }
              layer.getSource().refresh();
            }
          });
        });
      }
    },
    recomputeHeatmaps() {
      this.isRecomputingHeatmap = true;
      let queryParam = "";
      this.unCalculatedDataUploadIds.forEach((id, index) => {
        if (id && index !== this.unCalculatedDataUploadIds.length - 1) {
          queryParam += `id=${id}&`;
        } else if (id) {
          queryParam += `id=${id}`;
        }
      });
      ApiService.get_(`/heatmap/compute/data-upload?${queryParam}`)
        .then(() => {
          this.toggleSnackbar({
            type: this.appColor.primary,
            message: this.$t("heatmaps.heatmapComputedSuccessfully"),
            state: true,
            timeout: 3000
          });
        })
        .catch(() => {
          this.toggleSnackbar({
            type: this.appColor.primary,
            message: this.$t("heatmaps.heatmapComputationFailed"),
            state: true,
            timeout: 3000
          });
        })
        .finally(() => {
          this.$store.dispatch(`app/${GET_USER_CUSTOM_DATA}`);
          this.isRecomputingHeatmap = false;
        });
    },
    checkIfHeatmapNeedsPois(layer) {
      this.toggleSnackbar({ state: false });
      if (
        this.selectedPoisOnlyKeys.length === 0 &&
        this.heatmapsWithPois.includes(layer.get("name"))
      ) {
        this.toggleSnackbar({
          type: "error",
          message: this.$t("map.snackbarMessages.selectAmenities"),
          state: true,
          timeout: 4000
        });
        return true;
      } else {
        return false;
      }
    },
    isHeatmapDisabled(layer) {
      if (
        this.heatmapsWithPois.includes(layer.get("name")) &&
        this.unCalculatedDataUploadIds.length > 0
      ) {
        layer.setVisible(false);
        layer.set("showOptions", false);
        return true;
      } else {
        return false;
      }
    }
  },
  watch: {
    selectedPoisOnlyKeys() {
      this.refreshAllVisibleHeatmaps();
    },
    activeScenario() {
      this.refreshAllVisibleHeatmaps();
    },
    "calculationMode.active": function() {
      this.refreshAllVisibleHeatmaps();
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
