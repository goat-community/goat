<template>
  <v-dialog v-model="show" max-width="355px">
    <v-card>
      <v-app-bar color="green" dark>
        <v-app-bar-nav-icon><v-icon>query_builder</v-icon></v-app-bar-nav-icon>
        <v-toolbar-title>Opening Hours</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    visible: { type: Boolean, required: true }
  },
  computed: {
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

<style scoped>
.v-card__text,
.v-card__title {
  word-break: normal !important;
}
</style>
