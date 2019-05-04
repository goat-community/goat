<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-card-title primary-title>
        <span class="title font-weight-regular">Print Map</span>
      </v-card-title>
      <v-card-text class="pr-16 pl-16 pt-0 pb-0">
        <v-divider></v-divider>
      </v-card-text>
      <v-card-text>
        <v-form>
          <v-text-field name="tittle" label="Tittle" type="text"></v-text-field>
          <v-select
            :items="layouts"
            prepend-icon="map"
            label="Layout"
          ></v-select>
          <v-select
            :items="scales"
            prepend-icon="fas fa-ruler-horizontal"
            item-text="display"
            item-value="value"
            label="Scale"
          ></v-select>
          <v-select
            :items="resolutions"
            prepend-icon="aspect_ratio"
            label="Resolution"
          ></v-select>
          <v-select
            :items="crs"
            prepend-icon="language"
            item-text="display"
            item-value="value"
            label="Reference System"
          ></v-select>

          <v-layout row>
            <v-flex xs9 class="pr-3">
              <v-slider
                prepend-icon="rotate_right"
                v-model="rotation"
                :max="360"
              ></v-slider>
            </v-flex>

            <v-flex xs3>
              <v-text-field
                v-model="rotation"
                suffix="°"
                class="mt-0"
                type="number"
              ></v-text-field>
            </v-flex>
          </v-layout>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn class="white--text" color="green">Print</v-btn>
      </v-card-actions>
    </v-card>
  </v-flex>
</template>

<script>
export default {
  data: () => ({
    defaultLayout: "A4 Portrait",
    layouts: ["A4 Portrait", "A4 Landscape", "A3 Portrait", "A3 Landscape"],
    scales: [
      { display: "1:100000", value: "100000" },
      { display: "1:50000", value: "50000" },
      { display: "1:25000", value: "25000" },
      { display: "1:10000", value: "10000" },
      { display: "1:5000", value: "5000" },
      { display: "1:2500", value: "2500" },
      { display: "1:500", value: "500" }
    ],
    resolutions: [72, 120, 200, 254, 300],
    crs: [{ display: "Web Mercator", value: "3857" }],
    rotation: 0
  }),
  components: {},
  computed: {},
  methods: {},
  mounted() {}
};
</script>
