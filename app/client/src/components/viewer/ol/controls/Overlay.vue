<template>
  <v-card ref="popup" max-width="800" class="ol-popup mx-auto">
    <v-toolbar :color="appColor.primary" flat height="50" dark>
      <v-toolbar-title>{{ title }}</v-toolbar-title>
      <v-spacer></v-spacer>
      <slot name="close"></slot>
    </v-toolbar>
    <v-card-text class="pb-0">
      <slot name="body"></slot>
    </v-card-text>
    <v-card-actions class="pt-0">
      <v-spacer></v-spacer>
      <slot name="actions"></slot>
    </v-card-actions>
  </v-card>
</template>
<script>
import { mapGetters } from "vuex";

export default {
  name: "overlay-popup",
  props: {
    title: { type: String, required: false },
    color: { type: String, default: "#2BB381" }
  },
  computed: {
    ...mapGetters("app", {
      appColor: "appColor"
    })
  }
};
</script>
