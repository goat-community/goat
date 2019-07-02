<template>
  <v-dialog v-model="show" max-width="350px">
    <v-card>
      <v-toolbar color="green" dark>
        <v-toolbar-side-icon
          ><v-icon>fas fa-file-download</v-icon></v-toolbar-side-icon
        >
        <v-toolbar-title>Download Isochrones</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-side-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-toolbar-side-icon
        >
      </v-toolbar>
      <v-card-title primary-title>
        <v-flex xs12>
          <v-text-field
            name="username"
            label="Filename"
            v-model="name"
            type="text"
          ></v-text-field>
          <v-select
            :items="items"
            v-model="selected"
            label="Choose output format"
          ></v-select>
        </v-flex>
      </v-card-title>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="white--text" @click="download()" color="green"
          >Download</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  props: {
    calculation: { type: Object, required: false },
    visible: { type: Boolean, required: true }
  },
  data: () => ({
    name: "isochrones-export",
    selected: "GeoJson",
    items: ["GeoJson", "Shapefile"]
  }),
  methods: {
    download() {}
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
