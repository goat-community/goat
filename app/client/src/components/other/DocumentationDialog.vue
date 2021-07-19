<template>
  <v-dialog v-model="show" v-if="item" scrollable max-width="830px">
    <v-card>
      <v-app-bar :color="color" dark>
        <v-tooltip top>
          <template v-slot:activator="{ on }">
            <v-app-bar-nav-icon v-on="on" @click="openDocInNetTab"
              ><v-icon>fas fa-external-link-alt</v-icon></v-app-bar-nav-icon
            >
          </template>
          <span>{{ $t(`appBar.documentation.openInNewTab`) }}</span>
        </v-tooltip>
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
        :color="color"
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
    item: { type: Object, required: false },
    color: { type: String, default: "#2BB381" }
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
  },
  methods: {
    openDocInNetTab() {
      if (!this.item) return;
      const url = this.item.mapLayer.get("docUrl");
      if (url) {
        window.open(url, "_blank");
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
  max-width: 800px;
}

iframe {
  border: 0px none;
  margin-left: -510px;
  height: 1500px;
  margin-bottom: -560px;
  margin-top: -120px;
  width: 1400px;
}
</style>
