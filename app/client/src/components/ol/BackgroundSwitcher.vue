<template>
  <v-speed-dial
    direction="top"
    style="position:absolute;bottom:30px;left:30px;z-index:2;"
    transition="slide-y-reverse-transition"
    v-if="backgroundLayers.length > 0"
  >
    <template v-slot:activator>
      <v-card
        v-for="(item, index) in backgroundLayers"
        max-width="80"
        class="mx-auto pa-1 elevation-5"
        :key="index"
        v-show="item.getVisible() === true"
        @click="selectBaselayer(item)"
      >
        <v-img
          :src="
            require(`../../assets/img/background-layers/${item.get(
              'name'
            )}.png`)
          "
          class="white--text"
          height="75"
          gradient="to bottom, rgba(0,0,0,.2), rgba(0,0,0,.5)"
        >
          <v-card-title
            class="fill-height align-end pl-1 pr-0 mb-0 pb-0 caption"
            style="font-size: 10px;"
            >{{ item.get("title") }}</v-card-title
          >
        </v-img>
      </v-card>
    </template>
    <template v-for="(item, index) in backgroundLayers">
      <v-card
        :key="index"
        max-width="80"
        v-show="item.getVisible() === false"
        @click="selectBaselayer(item)"
        class="mx-auto  mt-2 pa-1"
      >
        <v-img
          :src="
            require(`../../assets/img/background-layers/${item.get(
              'name'
            )}.png`)
          "
          class="white--text"
          height="75"
          gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
        >
          <v-card-title
            class="fill-height align-end pl-1 pr-0 mb-0 pb-0 caption"
            style="font-size: 10px;"
            >{{ item.get("title") }}</v-card-title
          >
        </v-img>
      </v-card>
    </template>
  </v-speed-dial>
</template>

<script>
import { Mapable } from "../../mixins/Mapable";
import { Group } from "ol/layer.js";
export default {
  mixins: [Mapable],
  data: () => ({
    backgroundLayers: [],
    activeBaseLayer: null
  }),
  methods: {
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      const me = this;

      me.map
        .getLayers()
        .getArray()
        .forEach(layer => {
          if (
            layer instanceof Group &&
            layer.get("name") === "Background Layers"
          ) {
            me.backgroundLayers = layer.getLayers().getArray();
          }
        });
    },
    selectBaselayer(item) {
      const me = this;
      me.backgroundLayers.forEach(layer => {
        layer.setVisible(false);
      });
      item.setVisible(true);
    }
  }
};
</script>
