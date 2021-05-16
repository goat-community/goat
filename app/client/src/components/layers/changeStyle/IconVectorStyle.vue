<template>
  <v-dialog
    width="300"
    overlay-opacity="0"
    persistent
    no-click-animation
    hide-overlay
    v-model="dialogue"
    content-class="v-dialog"
  >
    <template v-slot:activator="{ on, attrs }">
      <v-icon
        v-ripple
        style="color:#B0B0B0;margin-bottom:15px;cursor:pointer"
        dark
        v-bind="attrs"
        v-on="on"
        @click="onSettingClick()"
      >
        fas fa-cog
      </v-icon>
    </template>
    <v-card
      :style="[isExpanded ? { height: 'auto' } : { height: '50px' }]"
      style="position:fixed;top:10px;left:360px;z-index:2;max-width:350px;min-width:450px;height:450px;overflow:hidden;"
    >
      <v-layout justify-space-between column fill-height>
        <v-app-bar
          :color="activeColor.primary"
          height="50"
          style="cursor:grab;"
          dark
        >
          <v-app-bar-nav-icon>
            <v-icon style="color:#B0B0B0;">
              fas fa-cog
            </v-icon>
          </v-app-bar-nav-icon>
          <v-toolbar-title>
            <b>{{ style.name }}</b>
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <v-icon @click="expand" class="toolbar-icons mr-2">
            {{ isExpanded ? "fas fa-chevron-up" : "fas fa-chevron-down" }}
          </v-icon>
          <v-icon @click="close" class="toolbar-icons ml-2">
            fas fa-times
          </v-icon>
        </v-app-bar>
        <vue-scroll>
          <v-tabs grow v-model="tab">
            <v-tab :key="1">
              <v-badge>
                <b>Change Icon Size</b>
              </v-badge>
            </v-tab>
            <v-tab :key="2">
              <v-badge>
                <b>Change Icon</b>
              </v-badge>
            </v-tab>
          </v-tabs>
          <v-tabs-items v-model="tab">
            <v-tab-item :key="1">
              <span
                class="d-flex mb-6"
                style="margin:10px 20px 0px 20px;width:200px"
              >
                <v-text-field
                  type="number"
                  :min="0"
                  :step="0.1"
                  outlined
                  tile
                  v-model="iconSize"
                  label="Icon Size"
                  style="height:50px;margin-right:50px;"
                  @input="onIconSizeChange()"
                ></v-text-field>
              </span>
            </v-tab-item>
            <v-tab-item :key="2" style="padding-top:10px;">
              <v-file-input
                append-outer-icon
                outlined
                tile
                label="Local Upload"
                @change="localUpload($event)"
                style="width:300px;margin-left:50px;"
              ></v-file-input>
              <span class="d-flex mb-6" style="width:350px;">
                <v-icon
                  style="padding-left:53px;padding-bottom:30px;font-size:20px;"
                >
                  fas fa-link
                </v-icon>
                <v-text-field
                  outlined
                  tile
                  v-model="urlIcon"
                  label="Url Upload"
                  style="padding-left: 12px;"
                  @input="urlUpload($event)"
                ></v-text-field>
              </span>
            </v-tab-item>
          </v-tabs-items>
        </vue-scroll>
      </v-layout>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapGetters } from "vuex";
import Legend from "../../viewer/ol/controls/Legend";

export default {
  props: ["item", "ruleIndex"],
  mixins: [Legend],
  data: () => ({
    isExpanded: true,
    tab: null,
    dialogue: false,
    iconSize: null,
    urlIcon: null
  }),
  computed: {
    ...mapGetters("app", {
      activeColor: "activeColor"
    }),
    style() {
      return this.filterStylesOnActiveModeByLayerName(
        this.item.mapLayer.get("name")
      ).rules[this.ruleIndex];
    }
  },
  methods: {
    expand() {
      this.isExpanded = !this.isExpanded;
    },
    close() {
      this.dialogue = false;
      //Refresh the legend
      this.item.layerTreeKey += 1;
    },
    onSettingClick() {
      if (this.dialogue == true) {
        //Refresh the legend
        this.item.layerTreeKey += 1;
      }
      this.dialogue = !this.dialogue;
      this.iconSize = this.style.symbolizers[0].size;
    },
    onIconSizeChange() {
      //Change icon size on input change event
      if (this.iconSize == 0) {
        this.style.symbolizers[0].size = 0.001;
      } else {
        this.style.symbolizers[0].size = Number(this.iconSize);
      }
      this.item.mapLayer.getSource().changed();
    },
    localUpload(value) {
      //Upload new icon from local
      this.urlIcon = null;
      if (value) {
        const reader = new FileReader();
        reader.readAsDataURL(value);
        reader.onload = e => {
          let icon = e.target.result;
          this.style.symbolizers[0].image = icon;
          this.item.mapLayer.getSource().changed();
        };
      }
    },
    urlUpload(value) {
      //Upload new icon from URL
      if (value) {
        this.style.symbolizers[0].image = value;
        this.item.mapLayer.getSource().changed();
      }
    }
  }
};
</script>
<style>
.v-dialog {
  box-shadow: none;
}
</style>
