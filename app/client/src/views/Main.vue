<template>
  <div class="pa-0 ma-0">
    <v-app
      v-if="appConfig && studyArea"
      id="wg-app"
      v-cloak
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
    <div class="loading">
      <v-progress-circular
        :width="7"
        :size="100"
        color="#2BB381"
        indeterminate
      ></v-progress-circular>
    </div>
  </div>
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
  GET_USER_CUSTOM_DATA,
  GET_APP_CONFIG,
  GET_STUDY_AREA,
  GET_STUDY_AREAS_LIST,
  GET_OPENAPI_CONFIG,
  GET_SCENARIOS,
  TEST_TOKEN
} from "../store/actions.type";
import { mapGetters, mapMutations } from "vuex";

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
    this.$store.dispatch(`auth/${TEST_TOKEN}`);
    this.$store.dispatch(`auth/${GET_USER}`).then(response => {
      if (response && response.language_preference) {
        this.$i18n.locale = response.language_preference;
      }
    });
    this.$store.dispatch(`app/${GET_APP_CONFIG}`).then(response => {
      this.setCloneVectorStyles(response);
    });
    this.$store.dispatch(`app/${GET_USER_CUSTOM_DATA}`);
    this.$store.dispatch(`map/${GET_STUDY_AREA}`);
    this.$store.dispatch(`map/${GET_STUDY_AREAS_LIST}`);
    this.$store.dispatch(`scenarios/${GET_SCENARIOS}`);
    this.$store.dispatch(`app/${GET_OPENAPI_CONFIG}`);
  },
  computed: {
    ...mapGetters("app", {
      appConfig: "appConfig",
      appColor: "appColor"
    }),
    ...mapGetters("map", {
      studyArea: "studyArea"
    })
  },
  methods: {
    ...mapMutations("map", {
      setCloneVectorStyles: "SET_CLONE_VECTOR_STYLES"
    })
  },
  mounted() {
    EventBus.$emit("app-mounted");
  }
};
</script>
