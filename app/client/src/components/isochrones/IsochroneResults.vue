<template>
  <v-layout>
    <v-flex xs12 class="mx-2">
      <template v-for="calculation in calculations">
        <v-card class="mb-3 " :key="calculation.id">
          <!-- Isochrone Nr -->
          <div class="isochrone-nr">{{ calculation.id }}</div>
          <v-card-title class="pb-0 mb-0">
            <span>
              <v-icon small class="mr-1">fas fa-clock</v-icon>
              <span>{{ calculation.time }}</span>
              <v-icon small class="ml-2 mr-1">fas fa-tachometer-alt</v-icon>
              <span>{{ calculation.speed }}</span>
              <v-icon
                @click="showPoisTable(calculation)"
                small
                class="result-icons ml-4 mr-2"
                >fas fa-table</v-icon
              >
              <v-icon small class="result-icons mr-2">fas fa-pencil-alt</v-icon>
              <v-icon
                @click="showHideCalculation(calculation)"
                small
                class="result-icons mr-2"
                v-html="
                  calculation.isVisible ? 'fas fa-eye-slash' : 'fas fa-eye'
                "
              ></v-icon>
              <v-icon
                @click="toggleDownloadDialog(calculation)"
                small
                class="result-icons mr-2"
                >fas fa-download</v-icon
              >
              <v-icon
                @click="deleteCalculation(calculation)"
                small
                class="result-icons mr-1"
              >
                fas fa-trash-alt</v-icon
              >
              <br />
            </span>
            <v-card-text class="pr-0 pl-0 pt-0 pb-0">
              <v-divider></v-divider>
            </v-card-text>
          </v-card-title>
          <v-subheader
            class="clickable"
            @click="calculation.isExpanded = !calculation.isExpanded"
          >
            <v-icon
              small
              class="mr-2"
              v-html="
                calculation.isExpanded
                  ? 'fas fa-chevron-down'
                  : 'fas fa-chevron-right'
              "
            ></v-icon>
            <h3>{{ calculation.position }}</h3>
          </v-subheader>
          <v-card-text class="pt-0" v-show="calculation.isExpanded">
            <v-data-table
              :headers="headers"
              :items="calculation.data"
              class="elevation-1"
              hide-actions
            >
              <template v-slot:items="props">
                <td>{{ props.item.type }}</td>
                <td>{{ props.item.range }}</td>
                <td>{{ props.item.area }}</td>
                <td>
                  <v-switch
                    :input-value="props.item.isVisible"
                    primary
                    hide-details
                    @change="toggleIsochroneFeatureVisibility(props.item)"
                  ></v-switch>
                </td>
                <td>
                  <div
                    class="legend"
                    :style="{ backgroundColor: props.item.color }"
                  ></div>
                </td>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </template>
    </v-flex>
    <confirm ref="confirm"></confirm>
    <download
      :visible="showDialog"
      :calculation="selectedCalculation"
      @close="showDialog = false"
    ></download>
  </v-layout>
</template>
<script>
import { mapGetters, mapActions, mapMutations } from "vuex";
import Confirm from "../core/Confirm";
import Download from "./IsochronesDownload";
import IsochroneUtils from "../../utils/IsochroneUtils";

export default {
  components: {
    confirm: Confirm,
    download: Download
  },
  data() {
    return {
      headers: [
        { text: "Type", value: "type", sortable: false },
        { text: "Range", value: "range", sortable: false },
        { text: "Area", value: "area", sortable: false },
        { text: "Visible", value: "visible", sortable: false },
        { text: "Legend", value: "legend", sortable: false }
      ],
      showDialog: false,
      selectedCalculation: null
    };
  },

  methods: {
    ...mapActions("isochrones", {
      removeCalculation: "removeCalculation",
      setSelectedThematicData: "setSelectedThematicData"
    }),
    ...mapMutations("isochrones", {
      toggleIsochroneFeatureVisibility: "TOGGLE_ISOCHRONE_FEATURE_VISIBILITY",
      toggleIsochroneCalculationVisibility:
        "TOGGLE_ISOCHRONE_CALCULATION_VISIBILITY",
      toggleThematicDataVisibility: "TOGGLE_THEMATIC_DATA_VISIBILITY"
    }),
    deleteCalculation(calculation) {
      this.$refs.confirm
        .open(
          "Delete",
          "Are you sure you want to delete Calculation " +
            calculation.id +
            " ?",
          { color: "green" }
        )
        .then(confirm => {
          if (confirm) {
            this.removeCalculation(calculation);
          }
        });
    },
    toggleDownloadDialog(calculation) {
      this.showDialog = true;
      this.selectedCalculation = calculation;
    },
    showHideCalculation(calculation) {
      let me = this;
      me.toggleIsochroneCalculationVisibility(calculation);
    },
    showPoisTable(calculation) {
      let me = this;
      let features = IsochroneUtils.getCalculationFeatures(
        calculation,
        me.isochroneLayer
      );

      let calculationId = calculation.id;
      let calculationName = calculation.name;
      let pois = IsochroneUtils.getCalculationPoisObject(features);

      let payload = {
        calculationId: calculationId,
        calculationName: calculationName,
        pois: pois
      };

      me.setSelectedThematicData(payload);
      me.toggleThematicDataVisibility(true);
    }
  },
  computed: {
    ...mapGetters("isochrones", {
      calculations: "calculations",
      isochroneLayer: "isochroneLayer"
    })
  }
};
</script>
<style>
.result-icons {
  color: "#4A4A4A";
}
.result-icons:hover {
  cursor: pointer;
  color: #30c2ff;
}
.isochrone-nr {
  position: absolute;
  left: 6px;
}
table.v-table tbody td:first-child,
table.v-table tbody td:not(:first-child),
table.v-table tbody th:first-child,
table.v-table tbody th:not(:first-child),
table.v-table thead td:first-child,
table.v-table thead td:not(:first-child),
table.v-table thead th:first-child,
table.v-table thead th:not(:first-child) {
  padding: 0 10px;
}

table.v-table tbody td,
table.v-table tbody th {
  height: 32px;
}
table.v-table thead tr {
  height: 32px;
}

.legend {
  height: 24px;
  width: 24px;
  border-radius: 7px;
}

.activeIcon {
  color: #30c2ff;
}
</style>
