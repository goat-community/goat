<template>
  <v-dialog v-model="show" max-width="350px">
    <v-card>
      <v-toolbar color="green" dark>
        <v-toolbar-side-icon><v-icon>info</v-icon></v-toolbar-side-icon>
        <v-toolbar-title>About GOAT</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-side-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-toolbar-side-icon
        >
      </v-toolbar>

      <v-card-title primary-title>
        <div>
          <div class="">
            <span
              ><b>GOAT</b> stands for Geo Open Accessibility Tool. This web-tool
              is meant to be open source, interactive, flexible and useful for
              accessibility planning. It is under development at the Chair for
              Urban Structure and Transport Planning at TUM.....
            </span>
          </div>
        </div>
      </v-card-title>

      <v-card-actions>
        <a
          class="info-link green--text"
          href="https://www.open-accessibility.org/"
          target="_blank"
          >More Info</a
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
