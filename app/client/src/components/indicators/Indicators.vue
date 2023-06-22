<template>
  <v-flex xs12 sm8 md4>
    <vue-scroll>
      <template>
        <!-- INDICATOR LAYERS -->
        <v-expansion-panels readonly>
          <v-expansion-panel
            v-for="(layer, i) in indicatorLayers"
            :key="i"
            :disabled="isIndicatorLayerDisabled(layer)"
            class="layer-row"
            :style="{
              backgroundColor: isIndicatorLayerDisabled(layer)
                ? '#ECECEC'
                : '#ffffff'
            }"
            :class="{
              'expansion-panel__container--active':
                layer.get('showOptions') === true
            }"
          >
            <v-expansion-panel-header
              expand-icon=""
              v-slot="{}"
              class="pl-0 ml-0"
            >
              <v-layout row class="pl-0 ml-0" wrap align-center>
                <v-flex class="checkbox" xs1>
                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-btn
                        v-on="on"
                        @click.stop="openDocumentation(layer)"
                        v-show="layer.get('docUrl')"
                        class="ma-0 pb-0"
                        small
                        text
                        icon
                      >
                        <i class="fas fa-info"></i>
                      </v-btn>
                    </template>
                    <span>{{ $t(`map.tooltips.openDocumentation`) }}</span>
                  </v-tooltip>
                </v-flex>
                <v-flex class="checkbox" xs1>
                  <v-checkbox
                    :color="appColor.secondary"
                    :input-value="layer.getVisible()"
                    @change="toggleLayerVisibility(layer)"
                  ></v-checkbox>
                </v-flex>
                <v-flex xs7 class="light-text">
                  <h4 class="pl-2">
                    {{ translate("layerName", layer.get("name")) }}
                  </h4>
                </v-flex>
                <v-row xs2 class="light-text pr-2 justify-end">
                  <v-menu offset-y>
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn
                        :disabled="
                          !layer.getVisible() || !active_indicator_taskId
                        "
                        fab
                        icon
                        class="elevation-0"
                        v-on="on"
                        v-bind="attrs"
                        small
                      >
                        <v-icon small>fa-solid fa-download</v-icon>
                      </v-btn>
                    </template>
                    <v-list>
                      <v-list-item
                        v-for="(type, index) in downloadTypes"
                        @click="downloadIndicator(type, layer)"
                        :key="index"
                      >
                        <v-list-item-title>{{ type }}</v-list-item-title>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </v-row>
                <v-flex xs1>
                  <v-icon
                    v-show="layer.getVisible()"
                    small
                    style="width: 30px; height: 30px"
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
                    @click.stop="toggleIndicatorLayerOptions(layer)"
                  ></v-icon>
                </v-flex>
              </v-layout>
            </v-expansion-panel-header>
            <v-card
              class="pt-2"
              v-show="layer.get('showOptions') === true"
              style="background-color: white"
              transition="slide-y-reverse-transition"
            >
              <InLegend :layer="layer"></InLegend>
              <v-layout row style="width: 100%; padding-left: 10px">
                <v-flex
                  class="xs2"
                  style="text-align: center"
                  v-if="
                    ['VECTORTILE', 'VECTOR', 'MVT', 'GEOBUF'].includes(
                      layer.get('type').toUpperCase()
                    )
                  "
                >
                  <v-icon
                    v-ripple
                    style="
                            color: #b0b0b0;
                            margin-top: 3px;
                            cursor: pointer;
                          "
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
          </v-expansion-panel>
        </v-expansion-panels>
      </template>
      <v-card-actions v-if="unCalculatedDataUploadIds.length > 0">
        <v-spacer></v-spacer>
        <v-btn
          :loading="isRecomputingIndicator"
          class="white--text"
          @click="recomputeIndicators"
          :color="appColor.primary"
        >
          <v-icon left>fas fa-refresh</v-icon
          >{{ $t("indicators.recomputeIndicators") }}</v-btn
        >
      </v-card-actions>
    </vue-scroll>
    <span v-if="styleDialogStatus">
      <StyleDialog
        type="layer"
        :item="currentItem"
        :translate="translate"
        :key="styleDialogKey"
        :styleDialogStatus="styleDialogStatus"
      ></StyleDialog>
    </span>
    <documentation-dialog
      :color="appColor.primary"
      :visible="showDocumentationDialog"
      :item="selectedDocumentationLayer"
      @close="showDocumentationDialog = false"
    ></documentation-dialog>
    <span v-if="timePickerDialogStatus">
      <TimePicker
        :status="timePickerDialogStatus"
        :translate="translate"
        @changeStatus="changeTimePickerDialogStatus"
        @updateTimeIndicators="refreshVisibleIndicators(updateIndicators.time)"
      ></TimePicker>
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
import StyleDialog from "../styling/StyleDialog.vue";
import TimePicker from "./TimePicker.vue";
import InLegend from "../viewer/ol/controls/InLegend.vue";
import ApiService from "../../services/api.service";
import { GET_USER_CUSTOM_DATA } from "../../store/actions.type";
import DocumentationDialog from "../other/DocumentationDialog.vue";
import JSZip from "jszip";
import { saveAs } from "file-saver";
export default {
  mixins: [Mapable, Legend, LayerTree],
  components: {
    InLegend,
    StyleDialog,
    TimePicker,
    DocumentationDialog
  },
  data: () => ({
    indicatorLayers: [],
    interactionType: "indicator-interaction",
    indicatorsWithAmenities: [
      "heatmap_accessibility_population",
      "heatmap_local_accessibility"
    ],
    updateIndicators: {
      poi: ["heatmap_local_accessibility", "heatmap_accessibility_population"],
      population: ["heatmap_accessibility_population", "heatmap_population"],
      time: ["pt_station_count", "pt_oev_gueteklasse"]
    },
    currentItem: null,
    styleDialogKey: 0,
    styleDialogStatus: false,
    timePickerDialogStatus: false,
    showDocumentationDialog: false,
    selectedDocumentationLayer: null,
    downloadTypes: [
      "GeoJson",
      "CSV",
      "Geobuf",
      "Shapefile",
      "GeoPackage",
      "KML",
      "XLSX"
    ]
  }),
  mounted() {
    EventBus.$on("updateStyleDialogStatusForLayerOrder", value => {
      this.styleDialogStatus = value;
    });

    this.updateLayerMaxResolution();
  },
  computed: {
    ...mapGetters("app", {
      appColor: "appColor",
      appConfig: "appConfig",
      calculationMode: "calculationMode",
      unCalculatedDataUploadIds: "unCalculatedDataUploadIds"
    }),
    ...mapGetters("poisaois", {
      selectedPoisOnlyKeys: "selectedPoisOnlyKeys",
      selectedAoisOnlyKeys: "selectedAoisOnlyKeys"
    }),
    ...mapGetters("scenarios", {
      activeScenario: "activeScenario"
    }),
    ...mapFields("map", {
      indicatorCancelToken: "indicatorCancelToken"
    }),
    ...mapFields("app", {
      isRecomputingIndicator: "isRecomputingIndicator"
    }),
    ...mapFields("indicators", {
      active_indicator_taskId: "active_indicator_taskId"
    })
  },
  methods: {
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
    }),
    changeTimePickerDialogStatus() {
      this.indicatorLayers.forEach(layer => {
        if (this.updateIndicators.time.includes(layer.get("name")))
          if (layer.getVisible() === true) {
            this.toggleLayerVisibility(layer);
          }
      });
      this.timePickerDialogStatus = false;
    },
    onMapBound() {
      this.map
        .getLayers()
        .getArray()
        .forEach(layer => {
          if (layer.get("group") && layer.get("group") === "indicator") {
            this.indicatorLayers.push(layer);
            layer.set("attributeDisplayStatusKey", 0);
          }
        });
      EventBus.$on("update-indicator", updateIndicatorsLinkedTo => {
        this.refreshIndicator(updateIndicatorsLinkedTo);
      });
    },
    toggleIndicatorLayerOptions(layer) {
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
    toggleLayerVisibility(layer) {
      if (this.indicatorCancelToken instanceof Function) {
        this.indicatorCancelToken("cancelled");
        this.indicatorCancelToken = null;
      }
      //Turn off other indicators.
      this.indicatorLayers.forEach(lc => {
        if (lc.get("name") === layer.get("name")) return;
        lc.setVisible(false);
        lc.set("showOptions", false);
      });
      layer.setVisible(!layer.getVisible());
      if (layer.getVisible() === false) {
        layer.set("showOptions", false);
      } else {
        if (this.indicatorCancelToken instanceof Function) {
          this.indicatorCancelToken("cancelled");
          this.indicatorCancelToken = null;
        }
        layer.getSource().refresh();
        this.checkIfIndicatorNeedsPoisAois(layer);
        layer.set("showOptions", true);
      }
      if (
        this.updateIndicators.time.includes(layer.get("name")) &&
        layer.getVisible()
      ) {
        this.timePickerDialogStatus = true;
      } else {
        this.timePickerDialogStatus = false;
      }
    },
    refreshVisibleIndicators(selected) {
      let indicatorLayers = this.indicatorLayers;
      if (selected && Array.isArray(selected)) {
        indicatorLayers = indicatorLayers.filter(layer =>
          selected.includes(layer.get("name"))
        );
      }
      indicatorLayers.forEach(layer => {
        if (layer.getVisible()) {
          this.checkIfIndicatorNeedsPoisAois(layer);
          if (this.indicatorCancelToken instanceof Function) {
            this.indicatorCancelToken("cancelled");
            this.indicatorCancelToken = null;
          }
          layer.getSource().refresh();
        }
      });
    },
    refreshIndicator(groups) {
      if (this.indicatorCancelToken instanceof Function) {
        this.indicatorCancelToken("cancelled");
        this.indicatorCancelToken = null;
      }
      groups.forEach(group => {
        if (this.updateIndicators[group]) {
          this.updateIndicators[group].forEach(indicatorName => {
            this.indicatorLayers.forEach(layer => {
              if (layer.get("name") === indicatorName && layer.getVisible()) {
                this.checkIfIndicatorNeedsPoisAois(layer);
                if (this.indicatorCancelToken instanceof Function) {
                  this.indicatorCancelToken("cancelled");
                  this.indicatorCancelToken = null;
                }
                layer.getSource().refresh();
              }
            });
          });
        }
      });
    },
    recomputeIndicators() {
      this.isRecomputingIndicator = true;
      let queryParam = "";
      this.unCalculatedDataUploadIds.forEach((id, index) => {
        if (id && index !== this.unCalculatedDataUploadIds.length - 1) {
          queryParam += `id=${id}&`;
        } else if (id) {
          queryParam += `id=${id}`;
        }
      });
      ApiService.get_(`/indicators/compute/data-upload?${queryParam}`)
        .then(() => {
          this.toggleSnackbar({
            type: this.appColor.primary,
            message: this.$t("indicators.indicatorsComputedSuccessfully"),
            state: true,
            timeout: 3000
          });
        })
        .catch(() => {
          this.toggleSnackbar({
            type: this.appColor.primary,
            message: this.$t("indicators.indicatorsComputationFailed"),
            state: true,
            timeout: 3000
          });
        })
        .finally(() => {
          this.$store.dispatch(`app/${GET_USER_CUSTOM_DATA}`);
          this.isRecomputingIndicator = false;
        });
    },
    checkIfIndicatorNeedsPoisAois(layer) {
      this.toggleSnackbar({ state: false });
      if (
        this.selectedPoisOnlyKeys.length === 0 &&
        this.selectedAoisOnlyKeys.length === 0 &&
        this.indicatorsWithAmenities.includes(layer.get("name"))
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
    isIndicatorLayerDisabled(layer) {
      if (
        this.indicatorsWithAmenities.includes(layer.get("name")) &&
        this.unCalculatedDataUploadIds.length > 0
      ) {
        layer.setVisible(false);
        layer.set("showOptions", false);
        return true;
      } else {
        return false;
      }
    },
    openDocumentation(layer) {
      this.showDocumentationDialog = true;
      this.selectedDocumentationLayer = layer;
    },
    downloadIndicator(type, layer) {
      const baseUrl_ = "indicators";
      const requestUrl = `${baseUrl_}/result/${
        this.active_indicator_taskId
      }?return_type=${type.toLowerCase()}`;

      let promise = ApiService.get_(requestUrl, {
        responseType: "blob",
        headers: {
          "Content-Type": "application/json"
        }
      });

      promise
        .then(data => {
          const zip = new JSZip();
          zip.file(
            `indicator-export_${layer.get("name")}.${type.toLowerCase()}`,
            data.data
          );

          zip.generateAsync({ type: "blob" }).then(function(content) {
            // Save the zip file
            saveAs(content, `indicator-export_${layer.get("name")}.zip`);
          });
        })
        .catch(err => {
          console.log(err);
        });
    }
  },
  watch: {
    selectedPoisOnlyKeys() {
      this.refreshVisibleIndicators(this.updateIndicators.poi);
    },
    activeScenario() {
      this.refreshVisibleIndicators();
    },
    "calculationMode.active": function() {
      this.refreshVisibleIndicators();
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
