<template>
  <v-dialog
    v-model="dialog"
    :max-width="options.width"
    @keydown.esc="cancel"
    v-bind:style="{ zIndex: options.zIndex }"
  >
    <v-card>
      <v-app-bar dark :color="appColor.primary" dense flat>
        <v-app-bar-nav-icon
          ><v-icon>{{ options.icon }}</v-icon></v-app-bar-nav-icon
        >
        <v-toolbar-title class="white--text">{{ title }}</v-toolbar-title>
      </v-app-bar>
      <v-card-text
        class="body-1 font-weight-medium mt-3 mb-0 pb-0"
        v-show="!!message"
        >{{ message }}</v-card-text
      >
      <v-card-actions class="pt-0">
        <v-spacer></v-spacer>
        <v-btn
          v-show="options.showYes"
          color="primary darken-1"
          text
          @click.native="agree"
          >{{ options.yesText || $t("buttonLabels.yes") }}</v-btn
        >
        <v-btn
          v-show="options.showNo"
          color="grey"
          text
          @click.native="cancel"
          >{{ options.noText || $t("buttonLabels.cancel") }}</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  data: () => ({
    dialog: false,
    resolve: null,
    reject: null,
    message: null,
    title: null,
    options: {
      color: "primary",
      width: 290,
      zIndex: 200,
      icon: "delete",
      showYes: true,
      showNo: true,
      yesText: "", // The value will be overwritted
      noText: "" // The value will be overwritted
    }
  }),
  methods: {
    open(title, message, options) {
      this.dialog = true;
      this.title = title;
      this.message = message;
      this.options = Object.assign(this.options, options);
      return new Promise((resolve, reject) => {
        this.resolve = resolve;
        this.reject = reject;
      });
    },
    agree() {
      this.resolve(true);
      this.dialog = false;
    },
    cancel() {
      this.resolve(false);
      this.dialog = false;
    }
  },
  computed: {
    ...mapGetters("app", {
      appColor: "appColor"
    })
  }
};
/**
 * Vuetify Confirm Dialog component
 *
 * Insert component where you want to use it:
 * <confirm ref="confirm"></confirm>
 *
 * Call it:
 * this.$refs.confirm.open('Delete', 'Are you sure?', { color: 'red' }).then((confirm) => {})
 * Or use await:
 * if (await this.$refs.confirm.open('Delete', 'Are you sure?', { color: 'red' })) {
 *   // yes
 * }
 * else {
 *   // cancel
 * }
 *
 * Alternatively you can place it in main App component and access it globally via this.$root.$confirm
 * <template>
 *   <v-app>
 *     ...
 *     <confirm ref="confirm"></confirm>
 *   </v-app>
 * </template>
 *
 * mounted() {
 *   this.$root.$confirm = this.$refs.confirm.open
 * }
 */
</script>
