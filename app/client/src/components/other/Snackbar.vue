<template>
  <v-snackbar
    :color="snackbar.type"
    top
    :timeout="snackbar.timeout"
    v-model="snackbar.state"
  >
    <v-icon color="white" class="mr-3">
      info
    </v-icon>
    <span v-html="snackbar.message"></span>
    <v-btn text @click="hideSnackbar({ state: false })">
      <v-icon>close</v-icon>
    </v-btn>
  </v-snackbar>
</template>

<script>
//Store imports
import { mapGetters, mapMutations } from "vuex";

export default {
  computed: {
    ...mapGetters("map", {
      snackbar: "snackbar"
    })
  },
  methods: {
    ...mapMutations("map", {
      hideSnackbar: "TOGGLE_SNACKBAR"
    })
  }
};
</script>
