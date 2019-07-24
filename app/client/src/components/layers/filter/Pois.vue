<template>
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
        <v-icon @click="decreaseWeight(item)" small class="arrow-icons ml-1">
          fas fa-arrow-down
        </v-icon>
      </template>
    </template>
  </v-treeview>
</template>

<script>
import { Mapable } from "../../../mixins/Mapable";
import Utils from "../../../utils/Layer";
import { mapGetters, mapActions } from "vuex";

export default {
  mixins: [Mapable],
  data: () => ({
    open: [],
    tree: [],
    heatmapLayers: [],
    poisLayer: null
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
      if (item.weight < 10) {
        item.weight++;
      }
    },
    decreaseWeight(item) {
      if (item.weight > 1) {
        item.weight--;
      }
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
    updateHeatmapLayerViewParams(selectedPois) {
      const me = this;
      const viewParams = selectedPois.map(item => {
        const { value, weight } = item;
        return {
          [`'${value}'`]: weight
        };
      });
      console.log(viewParams);

      me.heatmapLayers.forEach(layer => {
        layer.getSource().updateParams({
          viewparams: `amenities:'${btoa(JSON.stringify(viewParams))}'`
        });
        if (viewParams.length === 0) {
          layer.setVisible(false);
        }

        layer.getSource().refresh();
      });
    },
    updatePoisLayerViewParams(selectedPois) {
      const me = this;
      if (me.poisLayer) {
        const viewparams = selectedPois.map(item => {
          const { value } = item;
          return value;
        });
        me.poisLayer.getSource().updateParams({
          viewparams: `amenities:'${btoa(viewparams.toString())}'`
        });
      }
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
  width: 130px;
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
