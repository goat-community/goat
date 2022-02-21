<template>
  <div>
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
        <v-icon class="ml-1" :color="getIconColor(item)" dense>
          {{ item.icon }}
        </v-icon>
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
              class="mr-2 mt-1 user-data-icon"
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
  </div>
</template>

<script>
import { Mapable } from "../../../mixins/Mapable";
import { mapGetters } from "vuex";
import { mapMutations } from "vuex";

//Ol imports
import VectorSource from "ol/source/Vector";
import VectorLayer from "ol/layer/Vector";

// Child components
import HeatmapOptions from "./HeatmapOptions";

export default {
  mixins: [Mapable],
  components: {
    "heatmap-options": HeatmapOptions
  },
  data() {
    return {
      selectedPoisAois: [],
      open: [],
      poisAoisLayer: null,
      showHeatmapOptionsDialog: false,
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
        displayInLegend: false,
        zIndex: 100,
        source: new VectorSource()
      });
      this.map.addLayer(vector);
      this.poisAoisLayer = vector;
    },
    treeViewChanged(item) {
      console.log(item);
    },
    toggleHeatmapDialog(amenity) {
      this.selectedAmenity = amenity;
      this.showHeatmapOptionsDialog = true;
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
    }
  },
  computed: {
    ...mapGetters("app", {
      appColor: "appColor",
      poisAoisTree: "poisAoisTree"
    })
  },
  created() {}
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
