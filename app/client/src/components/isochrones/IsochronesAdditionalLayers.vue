<template>
  <v-dialog v-model="show" max-width="350px">
    <v-card>
      <v-app-bar color="green" dark>
        <v-app-bar-nav-icon
          ><v-icon>fas fa-layer-group</v-icon></v-app-bar-nav-icon
        >
        <v-toolbar-title>{{
          $t("isochrones.results.additionalLayers")
        }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>

      <v-card-title primary-title v-if="calculation">
        <v-flex xs12>
          <v-checkbox label="Default Road Network"></v-checkbox>
          <v-checkbox label="Modified Road Network"></v-checkbox>
        </v-flex>
      </v-card-title>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  props: {
    calculation: { type: Object, required: false },
    visible: { type: Boolean, required: true }
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
