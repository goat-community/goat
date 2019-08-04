<template>
  <v-card ref="popup" max-width="344" width="250" class="ol-popup mx-auto">
    <v-toolbar color="green" flat height="50" dark>
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
export default {
  props: {
    title: { type: String, required: false }
  }
};
</script>
<style>
/*Popup overlay Styling */
.ol-popup {
  position: absolute;
  background-color: white;
  -webkit-filter: drop-shadow(0 1px 4px rgba(0, 0, 0, 0.2));
  filter: drop-shadow(0 1px 4px rgba(0, 0, 0, 0.2));
  bottom: 12px;
  left: -50px;
  min-width: 280px;
}
.ol-popup:after,
.ol-popup:before {
  top: 100%;
  border: solid transparent;
  content: " ";
  height: 0;
  width: 0;
  position: absolute;
  pointer-events: none;
}
.ol-popup:after {
  border-top-color: white;
  border-width: 10px;
  left: 48px;
  margin-left: -10px;
}
.ol-popup:before {
  border-top-color: #cccccc;
  border-width: 11px;
  left: 48px;
  margin-left: -11px;
}
</style>
