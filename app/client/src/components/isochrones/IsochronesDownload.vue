<template>
  <v-dialog v-model="show" scrollable max-width="350px">
    <v-card>
      <v-app-bar :color="appColor.primary" dark>
        <v-app-bar-nav-icon
          ><v-icon>fa-solid fa-download</v-icon></v-app-bar-nav-icon
        >
        <v-toolbar-title>{{ $t("isochrones.download.title") }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
      <vue-scroll>
        <v-card-title primary-title>
          <v-flex xs12>
            <v-text-field
              :label="$t(`isochrones.download.fileName`)"
              v-model="name"
              type="text"
            ></v-text-field>
            <v-select
              :items="items"
              v-model="selected"
              :label="$t(`isochrones.download.outputFormat`)"
            ></v-select>
          </v-flex>
        </v-card-title>
      </vue-scroll>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          class="white--text"
          @click="download()"
          :loading="isDownloading"
          :color="appColor.primary"
          ><v-icon left>fas fa-download</v-icon
          >{{ $t("isochrones.download.download") }}</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";
import { saveAs } from "file-saver";
import ApiService from "../../services/api.service";

export default {
  props: {
    calculation: { type: Object, required: false },
    visible: { type: Boolean, required: true }
  },
  data: () => ({
    name: "isochrones-export",
    selected: "GeoJson",
    items: ["GeoJson", "Shapefile", "XLSX"],
    isDownloading: false
  }),
  methods: {
    download() {
      let me = this;
      let exportName = me.name;
      if (me.name.length === 0) {
        exportName = "export";
      }
      this.isDownloading = true;
      const isochrone_calculation_id =
        me.calculation.data[0].isochrone_calculation_id;
      ApiService.get_(
        `/isochrones/export/${isochrone_calculation_id}?return_type=${me.selected}`,
        { responseType: "blob" }
      )
        .then(response => {
          saveAs(response.data, `${exportName}.zip`);
        })
        .finally(() => {
          this.isDownloading = false;
          me.show = false;
        });
    }
  },
  computed: {
    ...mapGetters("isochrones", { isochroneLayer: "isochroneLayer" }),
    ...mapGetters("app", {
      appColor: "appColor",
      openapiConfig: "openapiConfig"
    }),
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
  },
  created() {
    this.items = this.openapiConfig.components.schemas.IsochroneExportType.enum;
    this.selected = this.items[0];
  }
};
</script>
