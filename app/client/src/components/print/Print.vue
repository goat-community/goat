<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-subheader>
        <span class="title">{{ $t("appBar.printMap.title") }}</span>
      </v-subheader>

      <v-card-text class="pr-16 pl-16 pt-0 pb-0">
        <v-divider></v-divider>
      </v-card-text>
      <v-card-text>
        <v-form ref="form" lazy-validation>
          <v-text-field
            name="tittle"
            :label="$t('appBar.printMap.form.title.label')"
            type="text"
            :rules="rules.tittle"
            required
          ></v-text-field>
          <v-select
            :items="layouts"
            prepend-icon="map"
            :label="$t('appBar.printMap.form.layout.label')"
            :rules="rules.required"
            required
          ></v-select>
          <v-select
            :items="scales"
            prepend-icon="fas fa-ruler-horizontal"
            item-text="display"
            item-value="value"
            :label="$t('appBar.printMap.form.scale.label')"
            :rules="rules.required"
            required
          ></v-select>
          <v-select
            :items="resolutions"
            prepend-icon="aspect_ratio"
            :label="$t('appBar.printMap.form.resolution.label')"
            :rules="rules.required"
            required
          ></v-select>
          <v-select
            :items="crs"
            prepend-icon="language"
            item-text="display"
            item-value="value"
            :label="$t('appBar.printMap.form.crs.label')"
            :rules="rules.required"
            required
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
        <v-btn class="white--text" color="green" @click="print">{{
          $t("appBar.printMap.form.submit")
        }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-flex>
</template>

<script>
import { Mapable } from "../../mixins/Mapable";
import OlPrintController from "../../controllers/OlPrintController";

export default {
  mixins: [Mapable],
  data: () => ({
    rules: {
      tittle: [
        v => !!v || "Field is required",
        v => (v && v.length <= 20) || "Tittle must be less than 20 characters"
      ],
      required: [v => !!v || "Field is required"]
    },
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
  methods: {
    print() {
      if (this.$refs.form.validate()) {
        console.log("init print...");
      }
    },
    /**
     * This function is executed, after the map is bound (see mixins/Mapable)
     */
    onMapBound() {
      //Initialize ol print controller
      this.olPrintCtrl = new OlPrintController(this.map, this.rotation);
    }
  },
  mounted() {},
  activated: function() {
    this.olPrintCtrl.activate();
  },
  deactivated: function() {
    this.olPrintCtrl.deactivate();
  }
};
</script>
