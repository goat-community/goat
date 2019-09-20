<template>
  <v-expansion-panels
    dark
    style="position:absolute;bottom:30px;right:10px;maxWidth: 200px;"
  >
    <v-expansion-panel style="background-color: white;">
      <v-expansion-panel-header
        >{{ $t("map.layerLegend.title") }}
        <template v-slot:actions>
          <v-icon small>$vuetify.icons.expand</v-icon>
        </template>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <vue-scroll>
          <template v-for="(item, index) in layers">
            <div
              :key="index"
              v-if="item.getVisible() === true"
              style="max-height: 150px;padding-right:10px;"
            >
              <p class="grey--text text--darken-2 pb-0 mb-1 mt-2 subtitle-2">
                {{
                  $te(`map.layerName.${item.get("name")}`)
                    ? $t(`map.layerName.${item.get("name")}`)
                    : item.get("name")
                }}
              </p>
              <v-divider></v-divider>
              <img
                style="max-width: 100%;"
                :src="getImageUrl(item)"
                class="white--text mt-0 pt-0"
              />
            </div>
          </template>
        </vue-scroll>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>
</template>
<script>
import { Mapable } from "../../mixins/Mapable";
import { getAllChildLayers } from "../../utils/Layer";

export default {
  mixins: [Mapable],
  data: () => ({
    layers: []
  }),
  methods: {
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      const me = this;
      const allLayers = getAllChildLayers(me.map);
      me.layers = allLayers.filter(
        layer => layer.getSource().serverType_ === "geoserver"
      );

      console.log(me.layers);
    },
    getImageUrl(item) {
      const baseUrl = window.location.origin;
      const url = `${baseUrl}/geoserver/ows?service=WMS&request=GetLegendGraphic&format=image/png&layer=${
        item.getSource().getParams().LAYERS
      }`;
      return url;
    }
  }
};
</script>
<style lang="css" scoped>
.v-expansion-panel-header {
  min-height: 30px;
  padding: 5px;
  background-color: #4caf50;
}

.v-expansion-panel-content >>> .v-expansion-panel-content__wrap {
  padding: 2px 0px 0px 5px;
}
</style>
