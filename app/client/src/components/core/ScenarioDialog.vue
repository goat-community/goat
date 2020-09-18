<template>
  <!-- CREATE SCENARIO DIALOG -->
  <v-dialog
    v-model="show"
    max-width="400"
    @keydown.esc="scenarioDialog = false"
  >
    <v-card>
      <v-app-bar flat color="green" dark height="50">
        <v-icon class="mr-3">fas fa-bullseye</v-icon>
        <v-toolbar-title>Create scenario</v-toolbar-title>
      </v-app-bar>
      <v-card-text class="mt-5">
        <v-form v-model="valid" lazy-validation>
          <v-text-field
            :rules="[rules.required, rules.counter]"
            v-model="scenarioName"
            label="Scenario Name"
            maxlength="30"
            lazy-validation
          ></v-text-field>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="primary darken-1"
          text
          :disabled="!valid"
          @click.native="
            createScenario();
            show = false;
          "
          >Ok</v-btn
        >
        <v-btn color="#dc143c" text @click.native="show = false">Cancel</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapFields } from "vuex-map-fields";

export default {
  props: ["visible"],
  data: () => ({
    valid: false,
    scenarioName: "",
    rules: {
      required: value => !!value || "Required.",
      counter: value => value.length <= 20 || "Max 20 characters"
    }
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
    },
    ...mapFields("isochrones", {
      scenarios: "scenarios",
      activeScenario: "activeScenario"
    })
  },
  methods: {
    createScenario() {
      console.log(this.scenarioName);
      let currentScenarioId = null;
      let previousScenarioId = parseInt(Object.keys(this.scenarios).pop());
      if (previousScenarioId) {
        currentScenarioId = previousScenarioId + 1;
      } else {
        currentScenarioId = 1;
      }
      this.$set(this.scenarios, currentScenarioId, {
        title: this.scenarioName
      });
      this.activeScenario = currentScenarioId;
      console.log(this.activeScenario);
      console.log(this.scenarios);
    }
  },
  watch: {
    show() {
      if (this.show === true) {
        let id = parseInt(Object.keys(this.scenarios).pop());
        console.log(id);
        if (id) {
          id += 1;
          this.scenarioName = "Scenario " + id;
        } else {
          this.scenarioName = "Scenario 1";
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
