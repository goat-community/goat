<template>
  <v-container
    class="ol-popup mx-auto ma-0 pa-1"
    style="border-radius: 5px;min-width: 200px;"
    fluid
  >
    <v-card
      flat
      tile
      style="border-radius: 5px;"
      max-width="200"
      class="d-flex"
    >
      <v-img :aspect-ratio="1.5" :src="imageUrl" v-if="imageUrl" class="black">
        <template v-slot:placeholder>
          <v-row class="fill-height ma-0" align="center" justify="center">
            <v-progress-circular
              indeterminate
              color="#2BB381"
            ></v-progress-circular>
          </v-row>
        </template>
      </v-img>
    </v-card>
  </v-container>
</template>
<script>
export default {
  name: "mapillary-image-preview",
  props: {
    imageUrl: { type: String, required: false }
  }
};
</script>
