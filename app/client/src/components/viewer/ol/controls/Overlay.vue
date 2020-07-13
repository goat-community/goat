<template>
  <v-card ref="popup" max-width="344" width="250" class="ol-popup mx-auto">
    <v-toolbar color="green" flat height="50" dark>
      <v-toolbar-title>{{
        title ? $t(`map.popup.${title}`) : ""
      }}</v-toolbar-title>
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
export default {
  name: "overlay-popup",
  props: {
    title: { type: String, required: false }
  }
};
</script>
