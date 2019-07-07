<template>
  <v-dialog v-model="show" max-width="350px">
    <v-card>
      <v-toolbar color="green" dark>
        <v-toolbar-side-icon
          ><v-icon>fas fa-file-download</v-icon></v-toolbar-side-icon
        >
        <v-toolbar-title>Download Isochrones</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-side-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-toolbar-side-icon
        >
      </v-toolbar>
      <v-card-title primary-title>
        <v-flex xs12>
          <v-text-field
            name="username"
            label="Filename"
            v-model="name"
            type="text"
          ></v-text-field>
          <v-select
            :items="items"
            v-model="selected"
            label="Choose output format"
          ></v-select>
        </v-flex>
      </v-card-title>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="white--text" @click="download()" color="green"
          >Download</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";
import maputils from "../../utils/MapUtils";
import { saveAs } from "file-saver";

export default {
  props: {
    calculation: { type: Object, required: false },
    visible: { type: Boolean, required: true }
  },
  data: () => ({
    name: "isochrones-export",
    selected: "GeoJson",
    items: ["GeoJson", "Shapefile"]
  }),
  methods: {
    download() {
      let me = this;
      if (me.selected === "GeoJson") {
        let featuresArray = [];
        let data = me.calculation.data;
        data.forEach(isochrone => {
          let id = isochrone.id;
          let feature = me.isochroneLayer.getSource().getFeatureById(id);
          if (feature) {
            let clonedFeature = feature.clone();
            clonedFeature.unset("isVisible");
            featuresArray.push(clonedFeature);
          }
        });
        let json = maputils.featuresToGeojson(featuresArray, "EPSG:3857");
        let blob = new Blob([json], { type: "application/json" });
        let exportName = me.name;
        if (me.name.length === 0) {
          exportName = "export";
        }
        saveAs(blob, `${exportName}.json`);
      }
    }
  },
  computed: {
    ...mapGetters("isochrones", { isochroneLayer: "isochroneLayer" }),
    show: {
      get() {
        return this.visible;
      },
      set(value) {
        if (!value) {
          this.$emit("close");
        }
      }
    }
  }
};
</script>
