<template>
  <v-dialog
    v-model="show"
    v-if="selectedIcon"
    persistent
    scrollable
    max-width="830px"
  >
    <v-card v-if="visible">
      <v-app-bar :color="color" dark>
        <v-app-bar-nav-icon
          ><v-icon>fa-solid fa-icons</v-icon></v-app-bar-nav-icon
        >
        <v-toolbar-title>Change Icon</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-app-bar-nav-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-app-bar-nav-icon
        >
      </v-app-bar>
      <v-row no-gutters class="mt-5 ml-2 mx-0 px-0">
        <v-col cols="12" sm="4"></v-col>
        <v-col cols="12" sm="4" align="center">
          <v-row no-gutters align="center" justify="center">
            <i
              :class="
                `${
                  newIcon.icon ? newIcon.icon : selectedIcon.icon
                } fa-2x notranslate mx-2 theme--light grey--text`
              "
              :style="
                Array.isArray(selectedIcon.color) &&
                selectedIcon.color.length > 1
                  ? `--fa-primary-color: ${selectedIcon.color[0]};--fa-secondary-color: ${selectedIcon.color[1]};width:40px;`
                  : `color: ${
                      iconColor ? iconColor : selectedIcon.color
                    } !important;width:40px;`
              "
            >
            </i>
            <h3 class="mt-1">
              {{
                $te(`pois.${selectedIcon.value}`)
                  ? $t(`pois.${selectedIcon.value}`)
                  : selectedIcon.value
              }}
            </h3>
          </v-row>
        </v-col>
        <v-col cols="12" sm="4" align="end" class="pr-4">
          <v-tooltip top>
            <template v-slot:activator="{ on }">
              <v-btn
                v-on="on"
                @click="restoreDefault()"
                color="white"
                class="mr-2 mb-2 "
                fab
                small
                :loading="isRestoring"
                depressed
              >
                <i
                  :class="
                    `fas fa-undo fa-2x notranslate mx-2 theme--light grey--text`
                  "
                ></i>
              </v-btn>
            </template>
            Restore Default
          </v-tooltip>
        </v-col>
      </v-row>
      <v-divider class="my-2 mt-4 mx-4"></v-divider>
      <v-row justify="center" class="mt-1 mx-0 px-0">
        <v-text-field
          style="max-width:150px;"
          v-model="iconColor"
          v-mask="mask"
          hide-details
          class="mx-5 mb-2 pa-0"
          solo
        >
          <template v-slot:append>
            <v-menu
              v-model="iconColorMenu"
              top
              nudge-bottom="105"
              nudge-left="16"
              :close-on-content-click="false"
            >
              <template v-slot:activator="{ on }">
                <div :style="swatchStyle" v-on="on" />
              </template>
              <v-card>
                <v-card-text class="pa-0">
                  <v-color-picker
                    @input="changeIconColor"
                    :value="iconColor"
                    flat
                  />
                </v-card-text>
              </v-card>
            </v-menu>
          </template>
        </v-text-field>
      </v-row>
      <v-divider class="mx-4 mt-1"></v-divider>
      <v-row class="mx-4 px-0">
        <v-col cols="4">
          <v-select
            :items="iconCategories"
            v-model="filters.category"
            label="Categories"
            @change="filterIcons"
          >
            <template slot="selection" slot-scope="{ item }">
              {{
                $te(`fa6Categories.${item}`)
                  ? $t(`fa6Categories.${item}`)
                  : item
              }}
            </template>
            <template slot="item" slot-scope="{ item }">
              {{
                $te(`fa6Categories.${item}`)
                  ? $t(`fa6Categories.${item}`)
                  : item
              }}
            </template>
          </v-select>
        </v-col>
        <v-col cols="8">
          <v-text-field
            class="mt-4 mx-6"
            v-model="filters.name"
            placeholder="Search icon"
            prepend-icon="search"
            type="text"
            onautocomplete="off"
            @input="filterIcons"
            dense
            clearable
          />
        </v-col>
      </v-row>
      <vue-scroll>
        <v-container class="pb-0">
          <vue-scroll>
            <v-col cols="12">
              <span :key="i" v-for="(icon, i) in historyList">
                <v-tooltip :disabled="!icon.name" top>
                  <template v-slot:activator="{ on }">
                    <v-btn
                      v-on="on"
                      @click="selectIcon(icon)"
                      color="white"
                      class="mr-2 mb-2 "
                      fab
                      small
                      depressed
                    >
                      <i
                        :class="
                          `${icon.icon} fa-2x notranslate mx-2 theme--light grey--text`
                        "
                      ></i>
                    </v-btn>
                  </template>
                  {{ icon.name }}
                </v-tooltip>
              </span>
            </v-col>
          </vue-scroll>
        </v-container>
      </vue-scroll>
      <v-card-actions class="pt-0 elevation-3">
        <v-pagination
          v-if="filteredIcons.length > 100"
          circle
          :total-visible="7"
          :color="color"
          class="pagination pl-10 ml-10 mt-1"
          v-model="page"
          :length="pages"
          @input="updatePage"
        ></v-pagination>
        <v-spacer></v-spacer>
        <v-btn color="grey" text @click.native="cancel">{{
          $t("buttonLabels.cancel")
        }}</v-btn>
        <v-btn
          color="primary darken-1"
          :loading="isBusy"
          text
          @click.native="updateIcon"
          >{{ $t("buttonLabels.save") }}</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mask } from "vue-the-mask";
import ApiService from "../../services/api.service";
import { mapFields } from "vuex-map-fields";
import { mapMutations, mapGetters } from "vuex";
import {
  solidFontAwesomeProDefs,
  fontAwesome6Categories
} from "../../utils/FontAwesomev6ProOnlySolid";
import { SET_POI_ICONS } from "../../store/mutations.type";
import { debounce } from "../../utils/Helpers";
export default {
  directives: { mask },
  props: {
    visible: { type: Boolean, required: true },
    selectedIcon: { type: Object },
    color: { type: String, default: "#2BB381" }
  },
  data: () => ({
    isBusy: false,
    isRestoring: false,
    // Pagination
    page: 1,
    pageSize: 100,
    listCount: 0,
    historyList: [],
    //--
    newIcon: {},
    iconColor: "",
    mask: "!#XXXXXXXX",
    iconColorMenu: false,
    filters: { name: "", category: "all" },
    filteredIcons: [],
    iconCategories: ["all", "custom(p4b)"],
    allIcons: []
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

    swatchStyle() {
      const { iconColor, iconColorMenu } = this;
      return {
        backgroundColor: iconColor,
        cursor: "pointer",
        height: "30px",
        width: "30px",
        borderRadius: iconColorMenu ? "50%" : "4px",
        transition: "border-radius 200ms ease-in-out"
      };
    },
    pages() {
      let _this = this;
      if (_this.pageSize == null || _this.listCount == null) return 0;
      return Math.ceil(_this.listCount / _this.pageSize);
    },
    ...mapFields("app", {
      appConfig: "appConfig"
    }),
    ...mapGetters("poisaois", {
      poisAoisLayer: "poisAoisLayer"
    })
  },
  methods: {
    ...mapMutations("app", {
      setPoiIcons: SET_POI_ICONS
    }),
    updateIcon() {
      const iconCategory = this.selectedIcon.value;
      const payload = {};
      payload[iconCategory] = {
        icon: this.newIcon.icon ? this.newIcon.icon : this.selectedIcon.icon,
        color: [this.iconColor]
      };
      this.isBusy = true;
      ApiService.post(`customizations/user/insert/poi`, payload)
        .then(res => {
          if (res.data) {
            this.appConfig = res.data;
            this.setPoiIcons(res.data);
            this.poisAoisLayer.changed();
          }
        })
        .finally(() => {
          this.isBusy = false;
          this.show = false;
        });
    },
    changeIconColor: debounce(function(color) {
      this.iconColor = color;
    }, 60),
    restoreDefault() {
      this.isRestoring = true;
      ApiService.delete(
        `customizations/user/reset-style/poi/${this.selectedIcon.value}`
      )
        .then(res => {
          if (res.data) {
            this.appConfig = res.data;
            this.setPoiIcons(res.data);
            this.poisAoisLayer.changed();
          }
        })
        .finally(() => {
          this.isRestoring = false;
          this.show = false;
        });
    },
    selectIcon(icon) {
      this.newIcon = {
        icon: icon.icon,
        color: this.iconColor
      };
    },
    selectColor(color) {
      this.newIcon = {
        icon: this.newIcon.icon ? this.newIcon.icon : this.selectedIcon.icon,
        color: color
      };
      this.iconColor = color;
    },
    filterIcons() {
      const filterKeys = Object.keys(this.filters);
      if (!this.filters.name && this.filters.category == "all") {
        this.filteredIcons = this.allIcons;
      }
      filterKeys.forEach(key => {
        if (this.filters[key] === null) {
          this.filters[key] = "";
        }
      });
      this.filteredIcons = this.allIcons.filter(icon =>
        icon.name.toLowerCase().includes(this.filters.name.toLowerCase())
      );
      if (this.filters.category != "all") {
        this.filteredIcons = this.filteredIcons.filter(
          icon => icon.category === this.filters.category
        );
      }
      this.page = 1;
      this.initPage();
      this.updatePage(this.page);
    },
    initPage: function() {
      let _this = this;
      _this.listCount = _this.filteredIcons.length;
      if (_this.listCount < _this.pageSize) {
        _this.historyList = _this.filteredIcons;
      } else {
        _this.historyList = _this.filteredIcons.slice(0, _this.pageSize);
      }
    },
    updatePage: function(pageIndex) {
      let _this = this;
      let _start = (pageIndex - 1) * _this.pageSize;
      let _end = pageIndex * _this.pageSize;
      _this.historyList = _this.filteredIcons.slice(_start, _end);
      _this.page = pageIndex;
    },
    clear() {
      this.filters.name = "";
      this.filters.category = "all";
      this.newIcon = {};
      this.iconColor = "";
      this.iconColorMenu = false;
      this.page = 1;
      this.pageSize = 100;
      this.listCount = 0;
      this.historyList = [];
    },
    cancel() {
      this.clear();
      this.show = false;
    }
  },
  watch: {
    visible() {
      if (this.visible === true) {
        this.clear();
        this.iconColor = this.selectedIcon.color[0] || this.color;
        this.filterIcons();
      }
    }
  },
  created() {
    if (
      window.FontAwesomeKitConfig &&
      window.FontAwesomeKitConfig.iconUploads
    ) {
      const iconDefs = Object.keys(window.FontAwesomeKitConfig.iconUploads);
      iconDefs.forEach(iconDef => {
        this.allIcons.push({
          icon: `fak fa-${iconDef}`,
          category: "custom(p4b)",
          name: ""
        });
      });

      const solidIcons = Object.keys(solidFontAwesomeProDefs);
      solidIcons.forEach(iconDef => {
        this.allIcons.push({
          icon: iconDef,
          category: solidFontAwesomeProDefs[iconDef].category_id,
          name: solidFontAwesomeProDefs[iconDef].label
            ? solidFontAwesomeProDefs[iconDef].label
            : ""
        });
      });

      this.iconCategories = [...this.iconCategories, ...fontAwesome6Categories];
    }
  }
};
</script>

<style scoped></style>
