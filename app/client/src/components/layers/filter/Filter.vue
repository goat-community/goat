<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-subheader>
        <span class="title">{{ $t("appBar.filter.title") }}</span>
      </v-subheader>
      <v-card-text class="pr-16 pl-16 pt-0 pb-0">
        <v-divider></v-divider>
      </v-card-text>
      <v-card-text class="pa-2"><pois-aois-tree /></v-card-text>
      <v-card-actions> </v-card-actions>
    </v-card>
  </v-flex>
</template>

<script>
import PoisAoisTree from "./PoisAoisTree";
export default {
  components: {
    "pois-aois-tree": PoisAoisTree
  }
};
</script>
