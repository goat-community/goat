import ApiService from "../../services/api.service";
import { getField, updateField } from "vuex-map-fields";
import { GET_STUDY_AREA, GET_STUDY_AREAS_LIST } from "../actions.type";
import { SET_STUDY_AREA, SET_STUDY_AREAS_LIST } from "../mutations.type";
import { SET_ERROR } from "../mutations.type";
import { errorMessage } from "../../utils/Helpers";
import { transformExtent } from "ol/proj";
import { geojsonToFeature } from "../../utils/MapUtils";

const state = {
  studyArea: null,
  studyAreaList: [],
  subStudyAreaLayer: null,
  map: null,
  errors: null,
  helpTooltip: {
    isActive: false,
    currentMessage: ""
  },
  messages: {
    snackbar: {
      type: "info",
      message: "",
      state: false,
      timeout: 2000
    }
  },
  contextmenu: null,
  isMapBusy: false,
  ///

  layers: {}, // Only for operational layers
  osmMode: false,
  reqFields: null,
  bldEntranceLayer: null,
  editLayer: null,
  selectedEditLayer: null,
  heatmapCancelToken: null,
  isMapillaryBtnDisabled: false,
  miniViewerVisible: false,
  vectorTileStyles: {},
  vectorTileStylesCopy: {},
  print: {
    active: false,
    title: "",
    crs: [{ display: "Web Mercator", value: "EPSG:3857" }],
    selectedCrs: "EPSG:3857",
    outputFormats: [
      { display: "PDF", value: "pdf" },
      { display: "PNG", value: "png" }
    ],
    selectedFormat: "pdf",
    rotation: 0,
    dpi: 150,
    dpis: [300, 150, 75],
    layout: {
      name: "A4 landscape",
      format: "a4",
      orientation: "landscape",
      size: [297, 210],
      padding: 5 // in mm.
    },
    layouts: [
      {
        name: "A4 portrait",
        format: "a4",
        orientation: "portrait",
        size: [210, 297],
        padding: 5 // in mm.
      },
      {
        name: "A4 landscape",
        format: "a4",
        orientation: "landscape",
        size: [297, 210],
        padding: 5 // in mm.
      },
      {
        name: "A3 portrait",
        format: "a3",
        orientation: "portrait",
        size: [297, 410],
        padding: 10 // in mm.
      },
      {
        name: "A3 landscape",
        format: "a3",
        orientation: "landscape",
        size: [410, 297],
        padding: 10 // in mm.
      }
    ],
    legend: true,
    grid: false,
    scale: null,
    scales: [500000, 100000, 50000, 25000, 10000, 5000, 2500, 500, 250, 100]
  }
};

const getters = {
  studyArea: state => state.studyArea,
  subStudyAreaLayer: state => state.subStudyAreaLayer,
  studyAreaProps: state => {
    if (Array.isArray(state.studyArea)) {
      const studyArea = state.studyArea[0];
      return {
        id: studyArea.get("id"),
        name: studyArea.get("name"),
        population: studyArea.get("population")
      };
    } else {
      return {};
    }
  },
  studyAreaList: state => state.studyAreaList,
  map: state => state.map,
  layers: state => state.layers,
  // eslint-disable-next-line no-unused-vars
  layerConfigList: (state, getters, rootState, rootGetters) => {
    const layerGroups = rootState.app.appConfig.layer_groups;
    const layers = [];
    layerGroups.forEach(layerGroup => {
      const groupName = Object.keys(layerGroup)[0];
      layerGroup[groupName].children.forEach(layerObj => {
        const layerName = Object.keys(layerObj)[0];
        const layer = layerObj[layerName];
        layers.push(layer);
      });
    });
    return layers;
  },
  osmMode: state => state.osmMode,
  helpTooltip: state => state.helpTooltip,
  messages: state => state.messages,
  contextmenu: state => state.contextmenu,
  snackbar: state => state.messages.snackbar,
  reqFields: state => state.reqFields,
  bldEntranceLayer: state => state.bldEntranceLayer,
  editLayer: state => state.editLayer,
  selectedEditLayer: state => state.selectedEditLayer,
  isMapillaryBtnDisabled: state => state.isMapillaryBtnDisabled,
  miniViewerVisible: state => state.miniViewerVisible,
  print: state => state.print,
  isMapBusy: state => state.isMapBusy,
  heatmapCancelToken: state => state.heatmapCancelToken,
  getField
};

const actions = {
  [GET_STUDY_AREA](context, credentials) {
    return new Promise((resolve, reject) => {
      ApiService.get("/users/me/study-area", credentials)
        .then(response => {
          context.commit(SET_STUDY_AREA, response.data);
          resolve(response.data);
        })
        .catch(({ response }) => {
          errorMessage(context, response, SET_ERROR);
          reject(response);
        });
    });
  },
  [GET_STUDY_AREAS_LIST](context, credentials) {
    return new Promise((resolve, reject) => {
      ApiService.get("/users/me/study-areas-list", credentials)
        .then(response => {
          context.commit(SET_STUDY_AREAS_LIST, response.data);
          resolve(response.data);
        })
        .catch(({ response }) => {
          errorMessage(context, response, SET_ERROR);
          reject(response);
        });
    });
  }
};

const mutations = {
  SET_MAP(state, map) {
    state.map = map;
  },
  [SET_ERROR](state, error) {
    state.errors = error;
  },
  START_HELP_TOOLTIP(state, message) {
    state.helpTooltip.isActive = true;
    state.helpTooltip.currentMessage = message;
  },
  STOP_HELP_TOOLTIP(state) {
    state.helpTooltip.isActive = false;
  },
  UPDATE_HELP_TOOLTIP(state, message) {
    state.currentMessage = message;
  },
  TOGGLE_SNACKBAR(state, payload) {
    Object.assign(state.messages.snackbar, payload);
  },
  [SET_STUDY_AREA](state, studyArea) {
    const olFeatures = geojsonToFeature(studyArea, {
      dataProjection: "EPSG:4326",
      featureProjection: "EPSG:3857"
    });
    const extent = transformExtent(
      olFeatures[0].get("bounds"),
      "EPSG:4326",
      "EPSG:3857"
    );
    if (Array.isArray(olFeatures) && olFeatures.length > 0) {
      olFeatures[0].set("bounds", extent);
      state.studyArea = olFeatures;
    }
  },
  [SET_STUDY_AREAS_LIST](state, studyAreas) {
    state.studyAreaList = studyAreas;
  },
  SET_CONTEXTMENU(state, contextmenu) {
    state.contextmenu = contextmenu;
  },
  SET_CLONE_VECTOR_STYLES(state, customerData) {
    const layerGroups = customerData.layer_groups;
    const styles = {};
    layerGroups.forEach(layerGroup => {
      const groupName = Object.keys(layerGroup)[0];
      layerGroup[groupName].children.forEach(layerObj => {
        const layerName = Object.keys(layerObj)[0];
        const layer = layerObj[layerName];
        styles[layerName] = {
          format: "geostyler",
          style: layer.style,
          translation: layer.translation || {}
        };
      });
    });
    state.vectorTileStyles = styles;
    //Making deep copy of styleobject for restoring the the original style of layers
    state.vectorTileStylesCopy = JSON.parse(JSON.stringify(styles));
  },
  /////////
  UPDATE_REQ_FIELDS(state, reqFields) {
    state.reqFields = reqFields;
  },
  SET_BLD_ENTRANCE_LAYER(state, entranceLayer) {
    state.bldEntranceLayer = entranceLayer;
  },
  SET_EDIT_LAYER(state, editLayer) {
    state.editLayer = editLayer;
  },
  updateField
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
