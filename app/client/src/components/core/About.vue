<template>
  <v-dialog v-model="show" max-width="355px">
    <v-card>
      <v-app-bar color="green" dark>
        <v-app-bar-nav-icon><v-icon>info</v-icon></v-app-bar-nav-icon>
        <v-toolbar-title>{{ $t("appBar.about.title") }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>

      <v-card-title primary-title>
        <div>
          <div class="body-1">
            <span
              ><b>{{ $t("appTitle") }}</b> {{ $t("appBar.about.content") }}
            </span>
          </div>
        </div>
      </v-card-title>
      <v-card-actions>
        <a
          class="info-link green--text"
          href="https://www.open-accessibility.org/"
          target="_blank"
          >{{ $t("appBar.about.moreInfo") }}</a
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: ["visible"],
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
