<template>
  <v-flex xs12 sm8 md4>
    <v-card flat>
      <v-subheader class="mb-4">
        <span class="title">{{ $t("appBar.dataUpload.title") }}</span>
      </v-subheader>
      <v-card-text class="pt-0 pb-0 px-0 mx-0">
        <v-divider></v-divider>
      </v-card-text>
      <v-card-text class="pa-2">
        <div>
          <v-tooltip top>
            <template v-slot:activator="{ on }">
              <v-btn
                :disabled="uploadedStorageSize > currentUser.storage"
                v-on="on"
                class="mt-n11 ml-2"
                :color="appColor.primary"
                @click="openUserDataUploadDialog"
                fab
                small
              >
                <v-icon color="white">add</v-icon>
              </v-btn>
            </template>
            <span>{{ $t("appBar.dataUpload.uploadSet") }}</span></v-tooltip
          >
        </div>
        <v-alert
          v-if="uploadedStorageSize > currentUser.storage"
          dense
          outlined
          type="error"
        >
          {{ $t("appBar.dataUpload.availableStorageExceeded") }}
        </v-alert>
      </v-card-text>
      <v-card class="px-16 mx-4 py-0 mb-2 fill-height" flat>
        <p class="mt-2 mb-1 sub-header">
          {{ (uploadedStorageSize / 1024).toFixed(2)
          }}{{ $t("userSettings.mbOf") }}
          {{ parseInt(currentUser.storage / 1024)
          }}{{ $t("userSettings.mbUsed") }}
        </p>
        <v-progress-linear
          height="2"
          :color="appColor.secondary"
          :value="occupiedStoragePercentage"
          class="mb-6 mt-0 pt-0"
        ></v-progress-linear>
        <v-hover v-slot="{ hover }">
          <v-btn
            small
            class="white--text"
            :color="hover ? 'error' : 'grey'"
            outlined
            @click="deleteAllFiles"
          >
            <v-icon left>delete</v-icon
            >{{ $t("appBar.dataUpload.deleteAllFiles") }}
          </v-btn>
        </v-hover>
        <v-data-table
          :headers="headers"
          :items="tableData"
          class="elevation-0 subtitle-1 mt-6"
          hide-default-footer
          hide-default-header
          light
        >
          <template v-slot:header="{ props: { headers } }">
            <thead>
              <tr>
                <th style="font-size:13px;" :key="h.value" v-for="h in headers">
                  <span>{{ h.text }}</span>
                </th>
              </tr>
            </thead>
          </template>
          <template v-slot:item.category="{ item }">
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <p v-on="on" class="mb-0 pb-0 truncate">{{ item.category }}</p>
              </template>
              <span>{{ item.category }}</span>
            </v-tooltip>
            <v-tooltip top>
              <template v-slot:activator="{ on }">
                <p
                  v-on="on"
                  class="mb-0 sub-header truncate"
                  style="font-size:12px;"
                >
                  {{ item.group }}
                </p>
              </template>
              <span>{{ item.group }}</span>
            </v-tooltip>
          </template>
          <template v-slot:items="props">
            <td>{{ props.item.date }}</td>
            <td>{{ props.item.size }}</td>
          </template>
          <template v-slot:item.delete="{ item }">
            <v-hover v-slot="{ hover }">
              <v-icon
                :color="hover ? 'error' : ''"
                dense
                @click="deleteItem(item)"
              >
                delete
              </v-icon>
            </v-hover>
          </template>
          <template v-slot:item.status="{ item }">
            <v-switch
              dense
              :color="appColor.secondary"
              :input-value="item.status"
              hide-details
              :disabled="isBusy"
              @change="toggleState(item)"
            ></v-switch>
          </template>
        </v-data-table>
        <v-divider></v-divider>
        <v-row style="width: 100%;" class="mt-2">
          <!-- add link to file -->
          <v-spacer></v-spacer>
          <a
            class="caption"
            style="text-decoration: none !important;"
            href="./static/template.geojson"
            download="template.geojson"
            >{{ $t("appBar.dataUpload.geojsonTemplate") }}</a
          >
        </v-row>
        <v-row style="width: 100%;" class="mt-1">
          <!-- add link to file -->
          <v-spacer></v-spacer>
          <a
            class="caption"
            style="text-decoration: none !important;"
            href="./static/template_shapefile.zip"
            download="template_shapefile.zip"
            >{{ $t("appBar.dataUpload.shapefileTemplate") }}</a
          >
        </v-row>
      </v-card>
    </v-card>
    <user-data-upload
      :visible="showDataUploadDialog"
      @close="showDataUploadDialog = false"
    />
    <confirm ref="confirm"></confirm>
  </v-flex>
</template>

<script>
import { mapGetters } from "vuex";
import ApiService from "../../services/api.service";
// import {saveAs} from 'file-saver';
import {
  GET_APP_CONFIG,
  GET_POIS_AOIS,
  GET_USER_CUSTOM_DATA
} from "../../store/actions.type";
import UserDataUploadDialog from "./UserDataUploadDialog";

export default {
  components: {
    "user-data-upload": UserDataUploadDialog
  },
  data: () => ({
    showDataUploadDialog: false,
    isBusy: false
  }),
  computed: {
    ...mapGetters("app", {
      appColor: "appColor",
      uploadedData: "uploadedData",
      poisConfig: "poisConfig",
      occupiedStoragePercentage: "occupiedStoragePercentage",
      uploadedStorageSize: "uploadedStorageSize"
    }),
    ...mapGetters("auth", {
      currentUser: "currentUser"
    }),
    tableData() {
      return this.uploadedData.map(item => {
        return {
          id: item.id,
          category: this.$te(`pois.${item.category}`)
            ? this.$t(`pois.${item.category}`)
            : item.category,
          group:
            this.poisConfig[item.category] &&
            this.poisConfig[item.category].group &&
            this.$te(`pois.${this.poisConfig[item.category].group}`)
              ? this.$t(`pois.${this.poisConfig[item.category].group}`)
              : "",
          date: new Date(Date.parse(item.creation_date)).toLocaleDateString(),
          size: (item.upload_size / 1024).toFixed(2) + "MB",
          status: item.state
        };
      });
    },
    headers() {
      return [
        {
          text: this.$t("appBar.dataUpload.table.category"),
          value: "category",
          sortable: false,
          width: "40%"
        },
        {
          text: this.$t("appBar.dataUpload.table.date"),
          value: "date",
          align: "center",
          sortable: false,
          width: "15%"
        },
        {
          text: this.$t("appBar.dataUpload.table.size"),
          value: "size",
          align: "center",
          sortable: false,
          width: "15%"
        },
        {
          text: this.$t("appBar.dataUpload.table.delete"),
          value: "delete",
          align: "center",
          sortable: false,
          width: "15%"
        },
        {
          text: this.$t("appBar.dataUpload.table.status"),
          value: "status",
          sortable: false,
          width: "15%"
        }
      ];
    }
  },
  methods: {
    deleteItem(item) {
      this.$refs.confirm
        .open(
          this.$t("appBar.dataUpload.deleteAllFiles"),
          this.$t("appBar.dataUpload.deleteAllFilesMessage"),
          { color: this.appColor.primary }
        )
        .then(confirm => {
          if (confirm) {
            ApiService.delete(`/custom-data/poi/${item.id}`).then(() => {
              this.$store.dispatch(`app/${GET_USER_CUSTOM_DATA}`);
              this.$store.dispatch(`app/${GET_APP_CONFIG}`);
              this.$store.dispatch(`poisaois/${GET_POIS_AOIS}`);
            });
          }
        });
    },
    deleteAllFiles() {
      this.$refs.confirm
        .open(
          this.$t("appBar.dataUpload.deleteAllFiles"),
          this.$t("appBar.dataUpload.deleteAllFilesMessage"),
          { color: this.appColor.primary }
        )
        .then(confirm => {
          if (confirm) {
            ApiService.delete(`/custom-data/poi/all`).then(() => {
              this.$store.dispatch(`app/${GET_USER_CUSTOM_DATA}`);
              this.$store.dispatch(`app/${GET_APP_CONFIG}`);
              this.$store.dispatch(`poisaois/${GET_POIS_AOIS}`);
            });
          }
        });
    },
    openUserDataUploadDialog() {
      this.showDataUploadDialog = true;
    },
    toggleState(item) {
      this.isBusy = true;
      ApiService.patch(`/custom-data/poi`, {
        data_upload_id: item.id,
        state: !item.status
      })
        .then(() => {
          this.$store.dispatch(`app/${GET_USER_CUSTOM_DATA}`);
          this.$store.dispatch(`app/${GET_APP_CONFIG}`);
          this.$store.dispatch(`poisaois/${GET_POIS_AOIS}`);
        })
        .finally(() => {
          this.isBusy = false;
        });
    }
  }
};
</script>
<style lang="css" scoped>
.truncate {
  max-width: 65px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
