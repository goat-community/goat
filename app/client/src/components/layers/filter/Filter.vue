<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-card-title primary-title>
        <span class="title font-weight-regular">Filter</span>
      </v-card-title>
      <v-card-text class="pr-16 pl-16 pt-0 pb-0">
        <v-divider></v-divider>
      </v-card-text>
      <v-card-text><pois /></v-card-text>
      <v-card-actions> </v-card-actions>
    </v-card>
  </v-flex>
</template>

<script>
import pois from "./Pois";
export default {
  data: () => ({}),
  components: {
    pois
  },
  computed: {},
  methods: {},
  mounted() {}
};
</script>
