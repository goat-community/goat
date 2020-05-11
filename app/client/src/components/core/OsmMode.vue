<template>
  <v-layout justify-space-between column fill-height style="overflow-y: auto;">
    <div v-if="!activeTask">
      <div v-for="(task, index) in this.osmMapMode.tasks" :key="index">
        <v-list two-line>
          <v-divider></v-divider>
          <v-list-item class="elevation-2" @click="setActiveTask(task)">
            <v-list-item-icon>
              <v-icon>fas fa-clock</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title class="subtitle-1 font-weight-medium">{{
                $te(`layerTree.osmMode.${task}.title`)
                  ? $t(`layerTree.osmMode.${task}.title`)
                  : task
              }}</v-list-item-title>
              <v-list-item-subtitle>{{
                $te(`layerTree.osmMode.${task}.shortDesc`)
                  ? $t(`layerTree.osmMode.${task}.shortDesc`)
                  : task
              }}</v-list-item-subtitle>
            </v-list-item-content>
            <v-list-item-action>
              <v-icon>fas fa-chevron-right</v-icon>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </div>
    </div>
    <div v-if="activeTask">
      <v-layout>
        <v-btn text icon class="mt-1 ml-1" light @click="setActiveTask(null)">
          <v-icon color="rgba(0,0,0,0.54)">fas fa-arrow-left</v-icon>
        </v-btn>
        <v-subheader class="ml-1 pb-1 pl-0">
          <span class="title">{{
            $te(`layerTree.osmMode.${activeTask}.title`)
              ? $t(`layerTree.osmMode.${activeTask}.title`)
              : task
          }}</span>
        </v-subheader>
      </v-layout>
      <v-divider></v-divider>

      <v-alert
        border="left"
        colored-border
        class="mb-0 mt-2 mx-1 elevation-2"
        icon="info"
        color="green"
        dense
      >
        <span
          v-html="
            $te(`layerTree.osmMode.${activeTask}.longDesc`)
              ? $t(`layerTree.osmMode.${activeTask}.longDesc`)
              : task
          "
        ></span>
      </v-alert>

      <v-subheader>
        <v-icon small class="mr-2">fas fa-tasks</v-icon>
        <h3>{{ $t(`layerTree.osmMode.steps`) }}</h3>
      </v-subheader>
      <v-divider class="mx-4 mt-0 pt-0"></v-divider>
      <ol class="ml-3 mt-2" id="steps">
        <li
          v-for="(value, key, index) in $t(
            `layerTree.osmMode.${activeTask}.stepsDesc`
          )"
          :key="index"
          v-html="value"
        ></li>
      </ol>
      <v-divider class="mx-4 mt-2 pt-0"></v-divider>
      <div class="red--text mx-3 pt-3">
        <i>{{ $t(`layerTree.osmMode.${activeTask}.note`) }}</i>
      </div>
    </div>
    <v-layout align-end>
      <v-bottom-navigation
        background-color="green"
        flat
        horizontal
        dark
        grow
        value="true"
        height="50"
      >
        <div class="pt-3">
          <v-icon>fas fa-tasks</v-icon>
          <span class="ml-2 subtitle-1" style="font-size: 0.85rem;">
            {{ $t("layerTree.osmMode.tasks") }}
          </span>
        </div>
      </v-bottom-navigation>
    </v-layout>
  </v-layout>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  data: () => ({
    activeTask: null
  }),
  created() {
    this.osmMapMode = this.$appConfig.componentData.osmMapMode;
  },
  beforeDestroy() {
    this.setActiveTask(null);
  },
  computed: {
    ...mapGetters("map", {
      layers: "layers"
    })
  },
  methods: {
    setActiveTask(task) {
      this.activeTask = task;
      // (Workaround) Watch is not accessible on component destory so are forced to add this here
      if (task === null) {
        // Remove cql filter from pois layer
        if (this.poisLayer) {
          const poisLayerSource = this.poisLayer.getSource();
          poisLayerSource.updateParams({
            cql_filter: null
          });
        }
      }
    }
  },
  watch: {
    activeTask(value) {
      switch (value) {
        case "missingHours": {
          // Show only pois with missing opening hours.
          if (!this.pois && this.layers.pois) {
            this.poisLayer = this.layers.pois;
          }
          this.poisLayer.getSource().updateParams({
            cql_filter: `opening_hours IS NULL`
          });
          break;
        }
        default: {
          break;
        }
      }
    }
  }
};
</script>

<style></style>
