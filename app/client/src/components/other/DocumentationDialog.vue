<template>
  <v-dialog v-model="show" v-if="item" scrollable max-width="815px">
    <v-card>
      <v-app-bar color="green" dark>
        <v-app-bar-nav-icon
          ><v-icon>fas fa-question-circle</v-icon></v-app-bar-nav-icon
        >
        <v-toolbar-title>{{
          $t("appBar.documentation.title")
        }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
      <v-progress-linear
        v-show="isLoading === true"
        indeterminate
        height="5"
        color="green"
      ></v-progress-linear>

      <vue-scroll>
        <v-container class="pb-0">
          <vue-scroll>
            <div class="documentation-wrapper">
              <iframe
                @load="isLoading = false"
                scrolling="yes"
                :src="item.mapLayer.get('docUrl')"
              >
              </iframe></div
          ></vue-scroll>
        </v-container>
      </vue-scroll>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    visible: { type: Boolean, required: true },
    item: { type: Object, required: false }
  },
  data: () => ({
    isLoading: true
  }),
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
.documentation-wrapper {
  border: 1px solid gray;
  margin: 10px;
  overflow: hidden;
  margin: 15px auto;
  max-width: 780px;
}

iframe {
  border: 0px none;
  margin-left: -500px;
  height: 1200px;
  margin-bottom: -520px;
  margin-top: -120px;
  width: 1400px;
}
</style>
