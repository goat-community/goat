<template>
  <v-dialog v-model="show" scrollable max-width="550px">
    <v-card>
      <v-app-bar :color="appColor.primary" dark>
        <v-app-bar-nav-icon
          ><v-icon>fas fa-cloud-arrow-up</v-icon></v-app-bar-nav-icon
        >
        <v-toolbar-title>{{
          $t("appBar.dataUpload.dialog.uploadData")
        }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
      <vue-scroll>
        <v-card-text primary-title>
          <h3>Upload Points of Interest</h3>
          <v-select
            :label="$t('appBar.dataUpload.dialog.selectCategory')"
            v-if="!isCustom"
            solo
            class="mt-2 mb-0 pb-0"
            item-value="type"
            v-model="selectedPoi"
            :items="poiList"
          >
            <template slot="selection" slot-scope="{ item }">
              <v-row>
                <v-col cols="3">
                  <i
                    :class="
                      item.icon +
                        ' v-icon notranslate ml-1 v-icon--dense theme--light grey--text ml-1'
                    "
                    :style="
                      Array.isArray(item.color) && item.color.length > 1
                        ? `--fa-primary-color: ${item.color[0]};--fa-secondary-color: ${item.color[1]};width:20px;`
                        : `color: ${item.color} !important;width:20px;`
                    "
                  >
                  </i>
                </v-col>
                <v-col cols="9"
                  ><span class="cb-item">{{
                    $te(`pois.${item.type}`)
                      ? $t(`pois.${item.type}`)
                      : item.type
                  }}</span></v-col
                >
              </v-row>
            </template>
            <template slot="item" slot-scope="{ item }">
              <v-row>
                <v-col cols="2">
                  <i
                    :class="
                      item.icon +
                        ' v-icon notranslate ml-1 v-icon--dense theme--light grey--text ml-1'
                    "
                    :style="
                      Array.isArray(item.color) && item.color.length > 1
                        ? `--fa-primary-color: ${item.color[0]};--fa-secondary-color: ${item.color[1]};width:20px;`
                        : `color: ${item.color} !important;width:20px;`
                    "
                  >
                  </i>
                </v-col>
                <v-col cols="10"
                  ><span class="cb-item">{{
                    $te(`pois.${item.type}`)
                      ? $t(`pois.${item.type}`)
                      : item.type
                  }}</span></v-col
                >
              </v-row>
            </template>
          </v-select>
          <v-checkbox
            class="pb-0 mb-0 mt-3"
            v-model="isCustom"
            :label="$t(`appBar.dataUpload.dialog.customCategory`)"
            @change="isCustomClicked"
          ></v-checkbox>
          <v-alert v-if="!isValid" dense outlined type="error">
            {{ $t("appBar.dataUpload.dialog.invalidCategory") }}
          </v-alert>
          <v-text-field
            v-if="isCustom"
            label="Category Name"
            v-model="selectedPoi"
            outlined
            min="2"
            max="50"
            :rules="[minLength]"
            lazy-validation
            @input="categoryNameInput"
          ></v-text-field>

          <v-btn
            :color="appColor.primary"
            class="white--text"
            depressed
            :disabled="!selectedPoi || !isValid"
            :loading="isSelecting"
            @click="onUploadButtonClick"
          >
            <v-icon left>
              cloud_upload
            </v-icon>
            {{ $t(`appBar.dataUpload.dialog.browseYourFiles`) }}
          </v-btn>
          <input
            ref="uploader"
            class="d-none"
            type="file"
            accept="image/*"
            @change="onFileChanged"
          />
        </v-card-text>
      </vue-scroll>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";
export default {
  data: () => ({
    isBusy: false,
    isValid: true,
    selectedFile: null,
    isSelecting: false,
    isCustom: false,
    selectedPoi: null,
    minLength: val => {
      if (val < 2) return "Please enter a text with at least 1 characters";
      return true;
    }
  }),
  props: ["visible"],
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
    ...mapGetters("app", {
      appColor: "appColor",
      poiIcons: "poiIcons",
      poisConfig: "poisConfig"
    }),
    poiList() {
      const poiIcons = this.poiIcons;
      const poiNames = Object.keys(poiIcons);
      return poiNames.map(poiName => {
        if (this.poisConfig[poiName]) {
          return {
            type: poiName,
            icon: poiIcons[poiName].icon,
            color: poiIcons[poiName].color
          };
        }
      });
    }
  },
  methods: {
    isCustomClicked() {
      this.selectedPoi = null;
      this.isValid = true;
    },
    onUploadButtonClick() {
      this.isSelecting = true;
      window.addEventListener(
        "focus",
        () => {
          this.isSelecting = false;
        },
        { once: true }
      );

      this.$refs.uploader.click();
    },
    onFileChanged(e) {
      this.selectedFile = e.target.files[0];
    },
    categoryNameInput() {
      const existingPoi = this.poiList.filter(p => p.type === this.selectedPoi);
      if (existingPoi.length > 0) {
        this.isValid = false;
      } else {
        this.isValid = true;
      }
    },
    clean() {
      this.isValid = true;
      this.selectedFile = null;
      this.isSelecting = false;
      this.isCustom = false;
      this.selectedPoi = null;
    }
  },
  watch: {
    visible(visible) {
      if (!visible) {
        this.clean();
      }
    }
  }
};
</script>

<style scoped></style>
