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
      :key="treeViewKey"
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
      item-disabled="isLocked"
      :selected-color="appColor.primary"
      active-class="grey lighten-4 indigo--text "
      on-icon="check_box"
      off-icon="check_box_outline_blank"
      indeterminate-icon="indeterminate_check_box"
    >
      <template v-slot:prepend="{ item }">
        <v-tooltip
          top
          :disabled="Array.isArray(item.children) || !!aoisConfig[item.value]"
        >
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
      @close="showHeatmapOptionsDialog = false"
    />
    <icon-picker
      :color="appColor.primary"
      :visible="showIconPickerDialog"
      :selectedIcon="selectedIcon"
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
// Child components
import HeatmapOptions from "./HeatmapOptions";
import IconPicker from "../../other/IconPicker";
import UserDataUploadDialog from "../../core/UserDataUploadDialog.vue";

// TODO: Fix sensitivity settings for every pois

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
    toggleHeatmapDialog(amenity) {
      this.selectedAmenity = amenity;
      this.showHeatmapOptionsDialog = true;
    },
    toggleIconPickerDialog(icon) {
      // Disable icon style change for groups and aois
      if (icon.children || this.aoisConfig[icon.value]) {
        return;
      }
      this.selectedIcon = icon;
      this.showIconPickerDialog = true;
    },
    isSensitivityEnabled(item) {
      if (this.aoisConfig[item.value]) {
        return false;
      }
      return true;
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
    getIconColor(item) {
      if (!item.color) {
        return "grey";
      }
      return item.color[0];
    },
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
    })
  },
  watch: {
    open() {
      console.log("opened....");
    },
    uploadedData() {
      this.treeViewKey += 1;
    }
  },
  computed: {
    ...mapGetters("app", {
      appColor: "appColor",
      poisAoisTree: "poisAoisTree",
      uploadedData: "uploadedData",
      aoisConfig: "aoisConfig"
    }),
    ...mapFields("app", {
      calculationMode: "calculationMode",
      layerTabIndex: "layerTabIndex"
    }),
    ...mapFields("poisaois", {
      poisAoisLayer: "poisAoisLayer",
      selectedPoisAois: "selectedPoisAois",
      poisAois: "poisAois",
      treeViewKey: "treeViewKey"
    })
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
