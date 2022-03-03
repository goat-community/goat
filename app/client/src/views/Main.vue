<template>
  <v-app
    v-if="appConfig && studyArea"
    id="wg-app"
    data-app
    :class="{ 'wg-app': true }"
  >
    <left-panel />
    <v-content>
      <v-container
        style="height: 100vh; max-height: 100%;"
        fluid
        fill-height
        class="pa-0"
      >
        <vue-scroll>
          <v-row style="width:100%;" justify="center" align="center">
            <app-viewer />
            <snackbar />
          </v-row>
        </vue-scroll>
      </v-container>
    </v-content>
    <app-sidebar />
  </v-app>
</template>

<script>
import { EventBus } from "../EventBus.js";
import appSidebar from "../components/core/SideDrawer";
import leftPanel from "../components/core/LeftPanel";
import Snackbar from "../components/other/Snackbar";
import Viewer from "../components/viewer/viewer";
import "@/globalComponents";
import {
  GET_USER,
  GET_APP_CONFIG,
  GET_STUDY_AREA,
  GET_STUDY_AREAS_LIST
} from "../store/actions.type";
import { mapGetters } from "vuex";

export default {
  name: "wg-app",
  components: {
    Snackbar,
    appSidebar,
    "left-panel": leftPanel,
    "app-viewer": Viewer
  },
  data() {
    return {};
  },
  created() {
    this.$store.dispatch(`auth/${GET_USER}`);
    this.$store.dispatch(`app/${GET_APP_CONFIG}`);
    this.$store.dispatch(`map/${GET_STUDY_AREA}`);
    this.$store.dispatch(`map/${GET_STUDY_AREAS_LIST}`);
  },
  computed: {
    ...mapGetters("app", {
      appConfig: "appConfig"
    }),
    ...mapGetters("map", {
      studyArea: "studyArea"
    })
  },
  mounted() {
    EventBus.$emit("app-mounted");
  },
  methods: {}
};
</script>
