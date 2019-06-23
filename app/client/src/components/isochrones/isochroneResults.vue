<template>
  <v-layout>
    <v-flex xs12 class="mx-2">
      <template v-for="isochrone in allIsochrones">
        <v-card class="mb-3 " :key="isochrone.id">
          <!-- Isochrone Nr -->
          <div class="isochrone-nr">{{ isochrone.id }}</div>
          <v-card-title class="pb-0 mb-0">
            <span>
              <v-icon small class="mr-1">fas fa-clock</v-icon>
              <span>{{ isochrone.time }}</span>
              <v-icon small class="ml-2 mr-1">fas fa-tachometer-alt</v-icon>
              <span>{{ isochrone.speed }}</span>
              <v-icon small class="result-icons ml-4 mr-2">fas fa-table</v-icon>
              <v-icon small class="result-icons mr-2">fas fa-pencil-alt</v-icon>
              <v-icon small class="result-icons mr-2">fas fa-eye-slash</v-icon>
              <v-icon small class="result-icons mr-2">fas fa-download</v-icon>
              <v-icon small class="result-icons mr-1"> fas fa-trash-alt</v-icon>
              <br />
            </span>
            <v-card-text class="pr-0 pl-0 pt-0 pb-0">
              <v-divider></v-divider>
            </v-card-text>
          </v-card-title>
          <v-subheader
            class="clickable"
            @click="isochrone.isExpanded = !isochrone.isExpanded"
          >
            <v-icon
              small
              class="mr-2"
              v-html="
                isochrone.isExpanded
                  ? 'fas fa-chevron-down'
                  : 'fas fa-chevron-right'
              "
            ></v-icon>
            <h3>{{ isochrone.title }}</h3>
          </v-subheader>
          <v-card-text class="pt-0" v-show="isochrone.isExpanded">
            <v-data-table
              :headers="headers"
              :items="isochrone.data"
              class="elevation-1"
              hide-actions
            >
              <template v-slot:items="props">
                <td>{{ props.item.type }}</td>
                <td>{{ props.item.range }}</td>
                <td>{{ props.item.area }}</td>
                <td>
                  <v-switch
                    v-model="props.item.visible"
                    primary
                    hide-details
                  ></v-switch>
                </td>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </template>
    </v-flex>
  </v-layout>
</template>

<script>
import { mapGetters } from "vuex";

export default {
  data() {
    return {
      headers: [
        { text: "Type", value: "type", sortable: false },
        { text: "Range", value: "range", sortable: false },
        { text: "Area", value: "area", sortable: false },
        { text: "Visible", value: "visible", sortable: false }
      ]
    };
  },
  methods: {},
  computed: mapGetters(["allIsochrones"])
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
</style>
