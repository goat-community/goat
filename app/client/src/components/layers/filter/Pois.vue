<template>
  <div>
    <v-treeview
      v-model="tree"
      :open="open"
      :items="allPois"
      ref="poisTree"
      activatable
      open-on-click
      dense
      selectable
      rounded
      return-object
      item-key="name"
      selected-color="green"
      active-class="grey lighten-4 indigo--text "
      on-icon="check_box"
      off-icon="check_box_outline_blank"
      indeterminate-icon="indeterminate_check_box"
    >
      <template v-slot:prepend="{ item, open }">
        <img v-if="item.icon" class="pois-icon" :src="getPoisIconUrl(item)" />
      </template>
      <template v-slot:label="{ item, open }">
        <div class="tree-label-custom">{{ item.name }}</div>
      </template>
      <template v-slot:append="{ item, open }">
        <template v-if="item.icon">
          <v-icon @click="increaseWeight(item)" small class="arrow-icons mr-1">
            fas fa-arrow-up
          </v-icon>
          <span>{{ item.weight }}</span>
          <v-icon @click="decreaseWeight(item)" small class="arrow-icons mr-1">
            fas fa-arrow-down
          </v-icon>
          <v-icon
            @click="toggleDynamicHeatmapDialog(item)"
            small
            class="arrow-icons ml-1"
          >
            fas fa-pen
          </v-icon>
        </template>
      </template>
    </v-treeview>
    <dynamic-heatmap
      :visible="showDynamicHeatmapDialog"
      :selectedAmenity="selectedAmenity"
      @close="showDynamicHeatmapDialog = false"
    />
  </div>
</template>

<script>
import { Mapable } from "../../../mixins/Mapable";
import Utils from "../../../utils/Layer";
import { mapGetters, mapActions } from "vuex";
import DynamicHeatmap from "./DynamicHeatmap";

export default {
  mixins: [Mapable],
  components: {
    "dynamic-heatmap": DynamicHeatmap
  },
  data: () => ({
    open: [],
    tree: [],
    heatmapLayers: [],
    poisLayer: null,
    showDynamicHeatmapDialog: false,
    selectedAmenity: {}
  }),
  methods: {
    ...mapActions("pois", {
      updateSelectedPois: "updateSelectedPois"
    }),
    getPoisIconUrl(item) {
      const images = require.context(
        "../../../assets/img/pois/",
        false,
        /\.png$/
      );
      return images("./" + item.icon + ".png");
    },
    increaseWeight(item) {
      const me = this;
      if (item.weight < 10) {
        item.weight++;
        me.updateHeatmapLayerViewParams(me.tree);
      }
    },
    decreaseWeight(item) {
      const me = this;
      if (item.weight > 1) {
        item.weight--;
        me.updateHeatmapLayerViewParams(me.tree);
      }
    },
    onMapBound() {
      const me = this;
      const map = me.map;
      const heatmapLayerNames = [
        "walkability",
        "walkability-population",
        "heatmap-dynamic"
      ];
      const poisLayerName = "pois";

      const allLayers = Utils.getAllChildLayers(map);
      allLayers.forEach(layer => {
        const layerName = layer.get("name");
        if (heatmapLayerNames.includes(layerName)) {
          me.heatmapLayers.push(layer);
        }
        if (layerName === poisLayerName) {
          me.poisLayer = layer;
        }
      });
    },
    updateHeatmapLayerViewParams(selectedPois) {
      const me = this;

      const standardHeatmapViewParams = selectedPois.reduce(
        (filtered, item) => {
          const { value, weight } = item;
          if (value != "undefined" && weight != undefined) {
            filtered.push({
              [`'${value}'`]: weight
            });
          }
          return filtered;
        },
        []
      );

      const dynamicHeatmapViewParams = selectedPois.reduce((filtered, item) => {
        const { value, weight, sensitivity } = item;
        if (value != "undefined" && weight != undefined) {
          filtered.push({
            [`${value}`]: { sensitivity: sensitivity, weight: weight }
          });
        }
        return filtered;
      }, []);

      me.heatmapLayers.forEach(layer => {
        const layerName = layer.get("name");
        const viewparams = JSON.stringify(
          layerName === "heatmap-dynamic"
            ? dynamicHeatmapViewParams
            : standardHeatmapViewParams
        );
        console.log(viewparams);
        layer.getSource().updateParams({
          viewparams: `amenities:'${btoa(viewparams)}'`
        });
        if (standardHeatmapViewParams.length === 0) {
          layer.setVisible(false);
        }

        layer.getSource().refresh();
      });
    },
    updatePoisLayerViewParams(selectedPois) {
      const me = this;
      if (me.poisLayer) {
        const viewParams = selectedPois.reduce((filtered, item) => {
          const { value } = item;
          if (value != "undefined") {
            filtered.push(value);
          }
          return filtered;
        }, []);

        me.poisLayer.getSource().updateParams({
          viewparams: `amenities:'${btoa(viewParams.toString())}'`
        });
      }
    },
    toggleDynamicHeatmapDialog(amenity) {
      console.log(this.showDynamicHeatmapDialog);
      console.log(amenity);
      this.selectedAmenity = amenity;
      this.showDynamicHeatmapDialog = true;
    }
  },
  watch: {
    tree: function() {
      const me = this;
      me.updateSelectedPois(me.tree);
      me.updateHeatmapLayerViewParams(me.tree);
      me.updatePoisLayerViewParams(me.tree);
    }
  },
  computed: {
    ...mapGetters("pois", {
      allPois: "allPois"
    })
  }
};
</script>
<style>
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
  width: 113px;
  word-wrap: break-word;
  overflow-wrap: break-word;
  overflow: hidden;
  text-overflow: ellipsis;
}
.v-treeview-node--leaf > .v-treeview-node__root {
  padding-left: 5px;
  padding-right: 4px;
}
</style>
