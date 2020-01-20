<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-subheader>
        <span class="title">{{ $t("appBar.filter.title") }}</span>
      </v-subheader>
      <v-card-text class="pr-16 pl-16 pt-0 pb-0">
        <v-divider></v-divider>
      </v-card-text>
      <v-card-text class="pa-2"><pois /></v-card-text>
      <v-card-actions> </v-card-actions>
    </v-card>
  </v-flex>
</template>

<script>
import pois from "./Pois";
export default {
  components: {
    pois
  }
};
</script>
