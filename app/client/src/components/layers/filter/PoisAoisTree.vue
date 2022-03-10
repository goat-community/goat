<template>
  <div>
    <v-tooltip top>
      <template v-slot:activator="{ on }">
        <v-btn
          v-on="on"
          class="mt-n11 ml-2"
          :color="appColor.primary"
          fab
          dark
          small
          @click="showDataUploadDialog = true"
        >
          <v-icon dark>add</v-icon>
        </v-btn>
      </template>
      <span>Upload POI Dataset</span></v-tooltip
    >

    <v-treeview
      v-model="selectedPoisAois"
      :open="open"
      @update:open="openNode"
      :items="poisAoisTree"
      activatable
      open-on-click
      dense
      selectable
      rounded
      return-object
      item-key="value"
      item-disabled="locked"
      :selected-color="appColor.primary"
      active-class="grey lighten-4 indigo--text "
      on-icon="check_box"
      off-icon="check_box_outline_blank"
      indeterminate-icon="indeterminate_check_box"
      @input="treeViewChanged"
    >
      <template v-slot:prepend="{ item }">
        <v-tooltip top :disabled="Array.isArray(item.children)">
          <template v-slot:activator="{ on }">
            <i
              v-on="on"
              @click="toggleIconPickerDialog(item)"
              :class="
                item.icon +
                  ' v-icon notranslate ml-1 v-icon--dense theme--light grey--text ml-1'
              "
              :style="
                Array.isArray(item.color) && item.color.length > 1
                  ? `--fa-primary-color: ${item.color[0]};--fa-secondary-color: ${item.color[1]};width:20px;`
                  : `color: ${item.color} !important;width:20px;`
              "
            >
            </i>
          </template>
          {{ $t("appBar.filter.poisSettings.changeIcon") }}
        </v-tooltip>
      </template>
      <template v-slot:label="{ item }">
        <div class="tree-label-custom">
          {{
            item.name
              ? item.name
              : $te(`pois.${item.value}`)
              ? $t(`pois.${item.value}`)
              : item.value
          }}
        </div>
      </template>
      <template v-slot:append="{ item, open }">
        <v-tooltip top>
          <template v-slot:activator="{ on }">
            <v-icon
              :ref="item.value"
              v-on="on"
              v-if="item.hasUserData"
              v-show="!open"
              class="mr-2 mt-0 user-data-icon"
              x-small
              :color="appColor.primary"
              >fa-solid fa-circle</v-icon
            > </template
          >{{ $t("appBar.filter.poisSettings.userDataSet") }}</v-tooltip
        >

        <template v-if="isSensitivityEnabled(item) && !item.children">
          <v-tooltip top>
            <template v-slot:activator="{ on }">
              <v-icon
                @click="toggleHeatmapDialog(item)"
                small
                v-on="on"
                class="arrow-icons mr-1"
              >
                fas fa-cog
              </v-icon>
            </template>
            <span>{{ $t("appBar.filter.poisSettings.buttonTooltip") }}</span>
          </v-tooltip>
        </template>
      </template>
    </v-treeview>
    <heatmap-options
      :color="appColor.primary"
      :visible="showHeatmapOptionsDialog"
      :selectedAmenity="selectedAmenity"
      @updated="updateHeatmap"
      @close="showHeatmapOptionsDialog = false"
    />
    <icon-picker
      :color="appColor.primary"
      :visible="showIconPickerDialog"
      :selectedIcon="selectedIcon"
      @updated="updateIcon"
      @close="showIconPickerDialog = false"
    >
    </icon-picker>
    <user-data-upload
      :visible="showDataUploadDialog"
      @close="showDataUploadDialog = false"
    />
  </div>
</template>

<script>
import { Mapable } from "../../../mixins/Mapable";
import { mapGetters } from "vuex";
import { mapMutations } from "vuex";
import { mapFields } from "vuex-map-fields";
//Ol imports
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/VectorImage";
// Child components
import HeatmapOptions from "./HeatmapOptions";
import IconPicker from "../../other/IconPicker";
import UserDataUploadDialog from "../../core/UserDataUploadDialog.vue";

// Other
import ApiService from "../../../services/api.service";
import { geobufToFeatures } from "../../../utils/MapUtils";
import { poisAoisStyle } from "../../../style/OlStyleDefs";
export default {
  mixins: [Mapable],
  components: {
    "heatmap-options": HeatmapOptions,
    "icon-picker": IconPicker,
    "user-data-upload": UserDataUploadDialog
  },
  data() {
    return {
      open: [],
      showHeatmapOptionsDialog: false,
      showDataUploadDialog: false,
      showIconPickerDialog: false,
      selectedIcon: {},
      selectedAmenity: {}
    };
  },

  methods: {
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      this.createPoisAoisLayer();
    },
    /**
     * Creates a vector layer for the pois_aois
     */
    createPoisAoisLayer() {
      const vector = new VectorLayer({
        name: "pois_aois_layer",
        type: "VECTOR",
        displayInLegend: false,
        queryable: true,
        zIndex: 99,
        source: new VectorSource(),
        style: poisAoisStyle
      });
      this.map.addLayer(vector);
      this.poisAoisLayer = vector;
    },
    treeViewChanged(selected) {
      const poisAois = {};
      selected.forEach(item => {
        poisAois[item.value] = true;
      });
      this.poisAois = poisAois;
      this.poisAoisLayer.changed();
    },
    toggleHeatmapDialog(amenity) {
      this.selectedAmenity = amenity;
      this.showHeatmapOptionsDialog = true;
    },
    toggleIconPickerDialog(icon) {
      // Disable icon style change for groups
      if (icon.children) {
        return;
      }
      this.selectedIcon = icon;
      this.showIconPickerDialog = true;
    },
    isSensitivityEnabled() {
      return true;
    },
    updateHeatmap() {
      console.log("update headmap");
    },
    openNode() {
      this.addBackgroundColorToTreeNode();
    },
    addBackgroundColorToTreeNode() {
      this.$nextTick(() => {
        this.$nextTick(() => {
          const elements = document.querySelectorAll(".user-data-icon");
          elements.forEach(element => {
            let parentEl = element.parentElement.parentElement;
            if (element.style.display !== "none") {
              if (
                parentEl.classList.contains("v-treeview-node__root") ||
                parentEl.classList.contains("v-treeview-node")
              ) {
                parentEl.classList.add("tree-node-view-background");
              }
            } else {
              parentEl.classList.remove("tree-node-view-background");
            }
          });
        });
      });
    },
    updateIcon() {
      console.log("update poi user icon...");
    },
    getIconColor(item) {
      if (!item.color) {
        return "grey";
      }
      return item.color[0];
    },
    fetchPoisAois() {
      return new Promise((resolve, reject) => {
        const payload = {
          modus: "default",
          amenities: ["supermarket", "discount_supermarket", "kindergarten"],
          active_upload_ids: [0],
          scenario_id: 0
        };
        ApiService.post(
          `/pois_aois/visualization?return_type=db_geobuf`,
          payload,
          {
            responseType: "arraybuffer",
            headers: {
              Accept: "application/pdf"
            }
          }
        )
          .then(response => {
            resolve(response);
            if (response.data) {
              const olFeatures = geobufToFeatures(response.data, {
                dataProjection: "EPSG:4326",
                featureProjection: "EPSG:3857"
              });
              this.poisAoisLayer.getSource().addFeatures(olFeatures);
            }
          })
          .catch(({ response }) => {
            reject(response);
          });
      });
    },
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
    })
  },
  watch: {
    open() {
      console.log("opened....");
    }
  },
  computed: {
    ...mapGetters("app", {
      appColor: "appColor",
      poisAoisTree: "poisAoisTree"
    }),
    ...mapFields("app", {
      calculationMode: "calculationMode",
      layerTabIndex: "layerTabIndex"
    }),
    ...mapFields("poisaois", {
      poisAoisLayer: "poisAoisLayer",
      selectedPoisAois: "selectedPoisAois",
      poisAois: "poisAois"
    })
  },
  created() {
    this.fetchPoisAois();
  }
};
</script>
<style lang="css">
.arrow-icons {
  color: "#4A4A4A";
}
.arrow-icons:hover {
  cursor: pointer;
  color: #30c2ff;
}

.pois-icon {
  margin-bottom: 15px;
}
.v-treeview-node--leaf {
  margin-left: 30px;
}
.v-treeview-node__content,
.v-treeview-node__label {
  flex-shrink: 1;
}
.tree-label-custom {
  display: block;
  width: 150px;
  word-wrap: break-word;
  overflow-wrap: break-word;
  overflow: hidden;
  text-overflow: ellipsis;
}
.v-treeview-node--leaf > .v-treeview-node__root {
  padding-left: 5px;
  padding-right: 4px;
}

.tree-node-view-background {
  background-color: #f5f5f5;
}
</style>