<template>
  <v-flex xs12 sm8 md4>
    <v-subheader>
      <span class="title">Layers</span>
    </v-subheader>
    <v-divider></v-divider>

    <v-expansion-panels accordion multiple>
      <v-expansion-panel v-for="(layerGroup, i) in layers" :key="i" expand>
        <v-expansion-panel-header
          class="elevation-2"
          expand-icon=""
          v-slot="{ open }"
        >
          <v-layout row wrap align-center>
            <v-flex xs1>
              <v-icon small>fas fa-layer-group</v-icon>
            </v-flex>
            <v-flex xs10>
              <div>{{ layerGroup.name }}</div>
            </v-flex>
            <v-flex xs1>
              <v-icon v-html="open ? 'remove' : 'add'"></v-icon>
            </v-flex>
          </v-layout>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <!-- LAYERS -->
          <v-expansion-panels>
            <v-expansion-panel
              v-for="(item, i) in layerGroup.children"
              :key="i"
              :class="{
                'expansion-panel__container--active': item.showOptions === true
              }"
            >
              <v-expansion-panel-header
                expand-icon=""
                @click="toggleLayerVisibility(item, layerGroup)"
                v-slot="{ open }"
              >
                <v-layout row class="pl-2" wrap align-center>
                  <v-flex xs2>
                    <v-icon
                      :class="{
                        'active-icon': item.isVisible === true,
                        'expansion-panel__container--active':
                          item.showOptions === true
                      }"
                      >done</v-icon
                    >
                  </v-flex>
                  <v-flex xs9>
                    <span>{{ item.name }}</span>
                  </v-flex>
                  <v-flex xs1>
                    <v-icon
                      v-show="item.isVisible"
                      @click.stop="toggleLayerOptions(item)"
                    ></v-icon>
                  </v-flex>
                </v-layout>
              </v-expansion-panel-header>
            </v-expansion-panel>
          </v-expansion-panels>

          <!-- ---- -->
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-flex>
</template>

<script>
import { Mapable } from "../../../mixins/Mapable";
import { Group, Vector } from "ol/layer.js";
export default {
  mixins: [Mapable],
  data: () => ({
    layers: []
  }),
  components: {},
  computed: {},
  methods: {
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     * and registers the current map layers.
     */
    onMapBound() {
      const me = this;
      const localVectorLayers = {
        name: "Local Vector Layers",
        id: 100,
        isExpanded: [false],
        children: []
      };
      me.map
        .getLayers()
        .getArray()
        .forEach((layer, index) => {
          let obj = me.getMapLayerObj(layer, index);
          if (layer instanceof Group) {
            me.layers.push(obj);
          } else if (layer instanceof Vector) {
            localVectorLayers.children.push(obj);
          }
        });
      //Check if there are any vector layers currently in the map
      if (localVectorLayers.children.length > 0) {
        me.layers.push(localVectorLayers);
      }
    },
    getMapLayerObj(layer, index) {
      const me = this;
      const obj = {};
      if (layer instanceof Group) {
        obj.name = layer.get("name") ? layer.get("name") : "Layer Group";
        obj.id = index;
        obj.isExpanded = [true];
        obj.children = [];
        const layers = layer.getLayers().getArray();
        layers.forEach((layer, index) => {
          if (layer instanceof Group) {
            me.getMapLayerObj(layer);
          } else {
            if (layer.get("displayInLayerList")) {
              let layerOpt = {
                id: index,
                name:
                  layer.get("title") || layer.get("name") || "Unnamed layer",
                isVisible: layer.getVisible() || false,
                showOptions: false,
                mapLayer: layer
              };
              obj.children.push(layerOpt);
            }
          }
        });
      } else if (layer instanceof Vector) {
        obj.id = index;
        obj.name = layer.get("title") || layer.get("name");
        obj.isVisible = layer.getVisible() || false;
        obj.showOptions = false;
        obj.mapLayer = layer;
      }
      return obj;
    },
    doNothing() {},
    toggleLayerVisibility(clickedLayer, layerGroup) {
      //Turn off other layers if layer group is background layers.
      if (
        layerGroup.name === "Background Layers" ||
        layerGroup.name === "Accessibility Basemap"
      ) {
        layerGroup.children.forEach(layer => {
          if (layer.id === clickedLayer.id) return;
          layer.isVisible = false;
          layer.showOptions = false;
          layer.mapLayer.setVisible(false);
        });
      }
      clickedLayer.isVisible = !clickedLayer.isVisible;
      clickedLayer.mapLayer.setVisible(clickedLayer.isVisible);
      if (clickedLayer.isVisible === false) {
        clickedLayer.showOptions = false;
      }
    },
    toggleLayerOptions(item) {
      item.showOptions = !item.showOptions;
    }
  },
  mounted() {}
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
  background-color: #4caf50 !important;
  color: white !important;
}

.v-expansion-panel-content >>> .v-expansion-panel-content__wrap {
  padding: 0px;
}
</style>
