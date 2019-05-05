<template>
  <v-dialog v-model="show" max-width="450px">
    <v-card flat>
      <v-toolbar color="green" dark>
        <v-toolbar-side-icon><v-icon>fas fa-cog</v-icon></v-toolbar-side-icon>
        <v-toolbar-title>Settings</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-toolbar-side-icon @click.stop="show = false"
          ><v-icon>close</v-icon></v-toolbar-side-icon
        >
      </v-toolbar>

      <!-- App Language Settings -->
      <v-subheader><h3>Language</h3></v-subheader>
      <v-card-text class="pr-16 pl-16 pt-0 pb-0 mb-2">
        <v-divider></v-divider>
      </v-card-text>

      <v-card-text>
        <div class="">
          <span>
            <v-btn-toggle v-model="defaultLanguage" mandatory>
              <v-btn
                flat
                v-for="entry in languages"
                :key="entry.title"
                @click="changeLocale(entry.language)"
              >
                <flag :iso="entry.flag" v-bind:squared="false" />
                <span class="pl-2">{{ entry.title }}</span>
              </v-btn>
            </v-btn-toggle>
          </span>
        </div>
      </v-card-text>

      <!-- Map Units Settings  -->
      <v-subheader><h3>Units</h3></v-subheader>
      <v-card-text class="pr-16 pl-16 pt-0 pb-0">
        <v-divider></v-divider>
      </v-card-text>
      <v-card-text>
        <v-radio-group v-model="units" row style="justify-content: center;">
          <v-radio label="Kilometers" value="kilometers"></v-radio>
          <v-radio label="Miles" value="miles"></v-radio>
        </v-radio-group>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import i18n from "@/plugins/i18n";
export default {
  props: ["visible"],
  data() {
    return {
      defaultLanguage: 0,
      units: "kilometers",
      languages: [
        { flag: "us", language: "en", title: "English" },
        { flag: "de", language: "de", title: "German" },
        { flag: "es", language: "es", title: "Español" },
        { flag: "al", language: "al", title: "Shqip" }
      ]
    };
  },
  methods: {
    changeLocale(locale) {
      i18n.locale = locale;
    }
  },
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
    }
  }
};
</script>
