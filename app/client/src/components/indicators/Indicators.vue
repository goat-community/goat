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
            <v-expansion-panel-header expand-icon="" v-slot="{}">
              <v-layout row class="pl-1" wrap align-center>
                <v-flex class="checkbox" xs1>
                  <v-checkbox
                    :color="appColor.secondary"
                    :input-value="layer.getVisible()"
                    @change="toggleLayerVisibility(layer)"
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
        :item="currentItem"
        :translate="translate"
        :key="styleDialogKey"
        :styleDialogStatus="styleDialogStatus"
      ></StyleDialog>
    </span>
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
import StyleDialog from "../layers/changeStyle/StyleDialog.vue";
import TimePicker from "./TimePicker.vue";
import InLegend from "../viewer/ol/controls/InLegend.vue";
import ApiService from "../../services/api.service";
import { GET_USER_CUSTOM_DATA } from "../../store/actions.type";
export default {
  mixins: [Mapable, Legend, LayerTree],
  components: {
    InLegend,
    StyleDialog,
    TimePicker
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
    timePickerDialogStatus: false
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
      indicatorCancelToken: "indicatorCancelToken"
    }),
    ...mapFields("app", {
      isRecomputingIndicator: "isRecomputingIndicator"
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
        this.checkIfIndicatorNeedsPois(layer);
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
          this.checkIfIndicatorNeedsPois(layer);
          if (this.indicatorCancelToken instanceof Function) {
            this.indicatorCancelToken("cancelled");
            this.indicatorCancelToken = null;
          }
          layer.getSource().refresh();
        }
      });
    },
    refreshIndicator(update) {
      if (this.indicatorCancelToken instanceof Function) {
        this.indicatorCancelToken("cancelled");
        this.indicatorCancelToken = null;
      }
      if (this.updateIndicators[update]) {
        this.updateIndicators[update].forEach(indicatorName => {
          this.indicatorLayers.forEach(layer => {
            if (layer.get("name") === indicatorName && layer.getVisible()) {
              this.checkIfIndicatorNeedsPois(layer);
              if (this.indicatorCancelToken instanceof Function) {
                this.indicatorCancelToken("cancelled");
                this.indicatorCancelToken = null;
              }
              layer.getSource().refresh();
            }
          });
        });
      }
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
    checkIfIndicatorNeedsPois(layer) {
      this.toggleSnackbar({ state: false });
      if (
        this.selectedPoisOnlyKeys.length === 0 &&
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
