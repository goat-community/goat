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
                v-if="uploadedStorageSize < currentUser.storage"
                v-on="on"
                class="mt-n11 ml-2"
                :color="appColor.primary"
                @click="openUserDataUploadDialog"
                fab
                dark
                small
              >
                <v-icon dark>add</v-icon>
              </v-btn>
            </template>
            <span>Upload Dataset</span></v-tooltip
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
          {{ (uploadedStorageSize / 1024).toFixed(1) }}MB of
          {{ parseInt(currentUser.storage / 1024) }}MB used
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
          light
        >
          <template v-slot:item.category="{ item }">
            <p class="mb-0 pb-0">{{ item.category }}</p>
            <p class="mb-0 sub-header" style="font-size:12px;">
              {{ item.group }}
            </p>
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
              @change="toggleState(item)"
            ></v-switch>
          </template>
        </v-data-table>
        <v-divider></v-divider>
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
import { GET_APP_CONFIG, GET_USER_CUSTOM_DATA } from "../../store/actions.type";
import UserDataUploadDialog from "./UserDataUploadDialog";

export default {
  components: {
    "user-data-upload": UserDataUploadDialog
  },
  data: () => ({
    showDataUploadDialog: false
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
        console.log(this.poisConfig[item.category]);
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
          size: (item.upload_size / 1024).toFixed(1) + "MB",
          status: this.currentUser.active_data_upload_ids.includes(item.id)
            ? true
            : false
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
            });
          }
        });
    },
    deleteAllFiles() {
      this.$refs.confirm
        .open(
          this.$t("appBar.dataUpload.deleteFile"),
          this.$t("appBar.dataUpload.deleteFileMessage"),
          { color: this.appColor.primary }
        )
        .then(confirm => {
          if (confirm) {
            ApiService.delete(`/custom-data/poi/all`).then(() => {
              this.$store.dispatch(`app/${GET_USER_CUSTOM_DATA}`);
              this.$store.dispatch(`app/${GET_APP_CONFIG}`);
            });
          }
        });
    },
    openUserDataUploadDialog() {
      this.showDataUploadDialog = true;
    },
    toggleState(item) {
      ApiService.patch(`/custom-data/poi`, {
        data_upload_id: item.id,
        state: item.status
      }).then(() => {
        this.$store.dispatch(`app/${GET_USER_CUSTOM_DATA}`);
        this.$store.dispatch(`app/${GET_APP_CONFIG}`);
      });
    }
  }
};
</script>
