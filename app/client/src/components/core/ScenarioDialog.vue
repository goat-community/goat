<template>
  <v-dialog
    v-model="show"
    max-width="400"
    @keydown.esc="scenarioDialog = false"
  >
    <v-card>
      <v-app-bar flat :color="appColor.primary" dark height="50">
        <v-icon class="mr-3">fas fa-bullseye</v-icon>
        <v-toolbar-title>{{
          scenarioId
            ? $t("appBar.edit.editScenarioName")
            : $t("appBar.edit.createScenario")
        }}</v-toolbar-title>
      </v-app-bar>
      <v-card-text class="mt-5">
        <v-form
          v-model="valid"
          @keyup.native.enter="
            updateInsertScenario();
            show = false;
          "
          @submit.prevent="show = false"
          lazy-validation
        >
          <v-text-field
            :rules="[rules.required, rules.counter]"
            v-model="scenarioName"
            :label="$t('appBar.edit.ScenarioName')"
            maxlength="50"
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
            updateInsertScenario();
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
import { mapGetters } from "vuex";
import ApiService from "../../services/api.service";
import { GET_SCENARIOS } from "../../store/actions.type";

export default {
  props: ["visible", "scenarioId"],
  data: () => ({
    valid: false,
    scenarioName: "",
    rules: {
      required: value => !!value || "Required.",
      counter: value => value.length < 50 || "Max 50 characters"
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
    ...mapFields("scenarios", {
      scenarios: "scenarios",
      activeScenario: "activeScenario"
    }),
    ...mapGetters("app", {
      appColor: "appColor"
    })
  },
  methods: {
    updateInsertScenario() {
      const scenarioName = this.scenarioName;
      const activeScenarioId = this.scenarioId;
      const payload = {
        scenario_name: scenarioName
      };
      let promise;
      if (activeScenarioId) {
        promise = ApiService.put(`/scenarios/${activeScenarioId}`, payload);
      } else {
        promise = ApiService.post("/scenarios", payload);
      }

      promise
        .then(response => {
          if (response.status === 200) {
            this.$store.dispatch(`scenarios/${GET_SCENARIOS}`);
            let scenarioId = activeScenarioId || response.data.id;
            scenarioId = parseInt(scenarioId);
            this.activeScenario = scenarioId;
          }
        })
        .catch(function(error) {
          throw new Error(error);
        });
    }
  },
  watch: {
    show() {
      if (this.show === true) {
        if (this.scenarioId) {
          this.scenarios.forEach(scenario => {
            if (scenario.id === this.scenarioId) {
              this.scenarioName = scenario.scenario_name;
            }
          });
        } else {
          let id = this.scenarios.length;
          if (id > 0) {
            id += 1;
            this.scenarioName = this.$t("appBar.edit.scenario") + " " + id;
          } else {
            this.scenarioName = this.$t("appBar.edit.scenario") + " 1";
          }
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
