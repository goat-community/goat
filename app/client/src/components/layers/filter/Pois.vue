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
          <v-icon
            @click="toggleHeatmapDialog(item)"
            small
            class="arrow-icons mr-1"
          >
            fas fa-cog
          </v-icon>
        </template>
      </template>
    </v-treeview>
    <heatmap-options
      :visible="showHeatmapOptionsDialog"
      :selectedAmenity="selectedAmenity"
      @updated="updateHeatmapLayerViewParams"
      @close="showHeatmapOptionsDialog = false"
    />
  </div>
</template>

<script>
import { Mapable } from "../../../mixins/Mapable";
import Utils from "../../../utils/Layer";
import { mapGetters, mapActions } from "vuex";
import HeatmapOptions from "./HeatmapOptions";

export default {
  mixins: [Mapable],
  components: {
    "heatmap-options": HeatmapOptions
  },
  data: () => ({
    open: [],
    tree: [],
    heatmapLayers: [],
    poisLayer: null,
    showHeatmapOptionsDialog: false,
    selectedAmenity: {}
  }),
  methods: {
    ...mapActions("pois", {
      updateSelectedPois: "updateSelectedPois"
    }),
    ...mapActions("isochrones", {
      countStudyAreaPois: "countStudyAreaPois"
    }),
    getPoisIconUrl(item) {
      const images = require.context(
        "../../../assets/img/pois/",
        false,
        /\.png$/
      );
      return images("./" + item.icon + ".png");
    },
    onMapBound() {
      const me = this;
      const map = me.map;
      const heatmapLayerNames = ["walkability", "walkability-population"];
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
    updateHeatmapLayerViewParams() {
      const me = this;
      const selectedPois = me.tree;
      const heatmapViewParams = selectedPois.reduce((filtered, item) => {
        const { value, weight, sensitivity } = item;
        if (value != "undefined" && weight != undefined) {
          filtered.push({
            [`'${value}'`]: { sensitivity: sensitivity, weight: weight }
          });
        }
        return filtered;
      }, []);

      me.heatmapLayers.forEach(layer => {
        const viewparams = JSON.stringify(heatmapViewParams);
        layer.getSource().updateParams({
          viewparams: `amenities:'${btoa(viewparams)}'`
        });

        if (heatmapViewParams.length === 0) {
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
    toggleHeatmapDialog(amenity) {
      this.selectedAmenity = amenity;
      this.showHeatmapOptionsDialog = true;
    }
  },
  watch: {
    tree: function() {
      const me = this;
      me.updateSelectedPois(me.tree);
      me.updateHeatmapLayerViewParams();
      me.updatePoisLayerViewParams(me.tree);
      me.countStudyAreaPois();
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
</style>
