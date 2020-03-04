<template>
  <v-flex xs12 sm8 md4>
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
              <div>{{ translate("layerGroup", layerGroup.name) }}</div>
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
              v-for="(item, i) in layerGroup.children"
              :key="i"
              :class="{
                'expansion-panel__container--active': item.showOptions === true
              }"
            >
              <v-expansion-panel-header
                expand-icon=""
                @click="toggleLayerVisibility(item, layerGroup)"
                v-slot="{}"
              >
                <v-layout row class="pl-2" wrap align-center>
                  <v-flex xs2>
                    <v-icon
                      :class="{
                        'active-icon': item.mapLayer.getVisible() === true,
                        'expansion-panel__container--active':
                          item.showOptions === true
                      }"
                      >done</v-icon
                    >
                  </v-flex>
                  <v-flex xs98>
                    <span>{{ translate("layerName", item.name) }}</span>
                  </v-flex>
                  <v-flex xs1>
                    <v-icon
                      v-show="item.mapLayer.getVisible()"
                      small
                      style="width: 30px; height: 30px;"
                      v-html="
                        item.showOptions === false
                          ? 'fas fa-chevron-down'
                          : 'fas fa-chevron-up'
                      "
                      :class="{
                        'expansion-panel__container--active':
                          item.showOptions === true
                      }"
                      @click.stop="toggleLayerOptions(item)"
                    ></v-icon>
                  </v-flex>
                </v-layout>
              </v-expansion-panel-header>
              <v-card
                class="pt-2"
                v-show="item.showOptions === true"
                style="background-color: white;"
                transition="slide-y-reverse-transition"
              >
                <v-slider
                  :value="item.mapLayer.getOpacity()"
                  class="mx-5"
                  step="0.05"
                  min="0"
                  max="1"
                  @input="changeLayerOpacity($event, item.mapLayer)"
                  :label="$t('layerTree.settings.transparency')"
                  color="#30C2FF"
                ></v-slider>
              </v-card>
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
import { mapGetters, mapMutations } from "vuex";

export default {
  mixins: [Mapable],
  data: () => ({
    layers: []
  }),
  components: {},
  computed: {
    ...mapGetters("pois", {
      selectedPois: "selectedPois"
    })
  },
  methods: {
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     * and registers the current map layers.
     */
    onMapBound() {
      const me = this;
      const localVectorLayers = {
        name: "Vector Layers",
        id: 100,
        isExpanded: [false],
        children: []
      };
      me.map
        .getLayers()
        .getArray()
        .forEach((layer, index) => {
          let obj = me.getMapLayerObj(layer, index);
          if (layer instanceof Group && layer.get("name") != "undefined") {
            me.layers.push(obj);
          } else if (
            layer instanceof Vector &&
            layer.get("name") != "undefined" &&
            layer.get("displayInLayerList") === true
          ) {
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
                name: layer.get("name") || "Unnamed layer",
                showOptions: false,
                mapLayer: layer
              };
              obj.children.push(layerOpt);
            }
          }
        });
      } else if (layer instanceof Vector) {
        obj.id = index;
        obj.name = layer.get("name");
        obj.showOptions = false;
        obj.mapLayer = layer;
      }
      return obj;
    },
    doNothing() {},
    toggleLayerVisibility(clickedLayer, layerGroup) {
      //Turn off other layers if layer group is background layers.
      if (
        layerGroup.name === "backgroundLayers" ||
        layerGroup.name === "accessbilityBasemaps"
      ) {
        layerGroup.children.forEach(layer => {
          if (layer.id === clickedLayer.id) return;
          layer.showOptions = false;
          layer.mapLayer.setVisible(false);
        });
      }
      if (layerGroup.name === "accessbilityBasemaps") {
        this.toggleSnackbar({
          type: "error",
          message: "selectAmenities",
          state: false,
          timeout: 0
        });
      }
      if (
        clickedLayer.mapLayer.get("requiresPois") === true &&
        this.selectedPois.length === 0
      ) {
        if (clickedLayer.mapLayer.getVisible() === false) {
          this.toggleSnackbar({
            type: "error",
            message: "selectAmenities",
            state: true,
            timeout: 60000
          });
        }
      }
      clickedLayer.mapLayer.setVisible(!clickedLayer.mapLayer.getVisible());
      if (clickedLayer.mapLayer.getVisible() === false) {
        clickedLayer.showOptions = false;
      }
    },
    toggleLayerOptions(item) {
      item.showOptions = !item.showOptions;
    },
    changeLayerOpacity(value, layer) {
      layer.setOpacity(value);
    },
    translate(type, key) {
      //type = {layerGroup || layerName}
      //Checks if key exists and translates it othewise return the input value
      const canTranslate = this.$te(`map.${type}.${key}`);
      if (canTranslate) {
        return this.$t(`map.${type}.${key}`);
      } else {
        return key;
      }
    },
    ...mapMutations("map", {
      toggleSnackbar: "TOGGLE_SNACKBAR"
    })
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
  background-color: #4caf50 !important;
  color: white !important;
}

.v-expansion-panel-content >>> .v-expansion-panel-content__wrap {
  padding: 0px;
}

.v-expansion-panel-content >>> .v-input__slot {
  margin-bottom: 0px;
}
</style>
