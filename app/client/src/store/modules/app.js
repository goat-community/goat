import ApiService from "../../services/api.service";
import { getField, updateField } from "vuex-map-fields";
import {
  GET_APP_CONFIG,
  GET_OPENAPI_CONFIG,
  GET_USER_CUSTOM_DATA
} from "../actions.type";
import {
  SET_APP_CONFIG,
  SET_ERROR,
  SET_OPENAPI_CONFIG,
  SET_POI_ICONS,
  SET_USER_CUSTOM_DATA
} from "../mutations.type";
import { errorMessage } from "../../utils/Helpers";
import SwaggerParser from "@apidevtools/swagger-parser";

const state = {
  errors: null,
  appConfig: null,
  openapiConfig: null,
  uploadedData: [],
  poiIcons: {},
  layerTabIndex: 0,
  calculationMode: {
    values: ["default", "scenario", "comparison"],
    active: "default"
  },
  activeColor: {
    primary: "#2BB381",
    secondary: "#2BB381"
  }
};

const getters = {
  appConfig: state => state.appConfig,
  openapiConfig: state => state.openapiConfig,
  uploadedData: state => state.uploadedData,
  calculationMode: state => state.calculationMode,
  appColor: state => {
    return state.appConfig.app_ui.base_color;
  },
  vectorTileStyles: state => {
    const layerGroups = state.appConfig.layer_groups;
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
    return styles;
  },
  routingProfiles: state => {
    let routingProfiles = {};
    const routing = state.appConfig.routing;
    routing.forEach(r => {
      routingProfiles[r.type] = r;
    });
    return routingProfiles;
  },
  poisAoisTree: state => {
    let treeStruct = [];
    const poiAoiGroups = [
      ...state.appConfig.poi_groups,
      ...state.appConfig.aoi_groups
    ];
    poiAoiGroups.forEach((group, groupIndex) => {
      const groupName = Object.keys(group)[0];
      const restructuredChildren = [];
      const children = group[groupName].children;
      let hasUserData = false;
      children.forEach(child => {
        const childName = Object.keys(child)[0];

        const restructeredChild = {
          value: childName,
          hasUserData: false,
          sensitivity: 300000,
          ...child[childName]
        };
        if (child[childName].upload_size) {
          hasUserData = true;
          restructeredChild.hasUserData = true;
        }
        restructuredChildren.push(restructeredChild);
      });
      const groupTreeStruct = {
        id: groupIndex,
        value: groupName,
        hasUserData,
        icon: group[groupName].icon,
        color: group[groupName].color,
        children: restructuredChildren
      };
      treeStruct.push(groupTreeStruct);
    });
    return treeStruct;
  },
  poisTreeOnlyChildren: (state, getters) => {
    let treeStruct = {};
    getters.poisAoisTree.forEach(group => {
      group.children.forEach(child => {
        if (getters.poiIcons[child.value]) {
          treeStruct[child.value] = child;
        }
      });
    });
    return treeStruct;
  },
  // Only Pois
  poisConfig: state => {
    const poiGroups = state.appConfig.poi_groups;
    let poisConfig = {};
    poiGroups.forEach(group => {
      const groupName = Object.keys(group)[0];
      group[groupName].children.forEach(child => {
        const childName = Object.keys(child)[0];
        poisConfig[childName] = {
          icon: child[childName].icon,
          color: child[childName].color,
          group: groupName
        };
      });
    });
    return poisConfig;
  },
  // Only Aois
  aoisConfig: state => {
    const aoisGroups = state.appConfig.aoi_groups;
    let aoisConfig = {};
    aoisGroups.forEach(group => {
      const groupName = Object.keys(group)[0];
      group[groupName].children.forEach(child => {
        const childName = Object.keys(child)[0];
        aoisConfig[childName] = {
          icon: child[childName].icon,
          color: child[childName].color,
          group: groupName
        };
      });
    });
    return aoisConfig;
  },
  uploadedStorageSize: state => {
    return state.uploadedData.reduce((acc, item) => {
      return acc + item.upload_size;
    }, 0);
  },
  // eslint-disable-next-line no-unused-vars
  occupiedStoragePercentage: (state, getters, rootState, rootGetters) => {
    const totalStorage = rootState.auth.user.storage;
    return (getters.uploadedStorageSize * 100) / totalStorage;
  },
  poiIcons: state => state.poiIcons,
  activeColor: state => state.activeColor,
  getField
};

const actions = {
  [GET_APP_CONFIG](context) {
    return new Promise((resolve, reject) => {
      ApiService.get("/customizations/me")
        .then(response => {
          context.commit(SET_APP_CONFIG, response.data);
          context.commit(SET_POI_ICONS, response.data);
          resolve(response.data);
        })
        .catch(({ response }) => {
          errorMessage(context, response, SET_ERROR);
          reject(response);
        });
    });
  },
  [GET_USER_CUSTOM_DATA](context) {
    return new Promise((resolve, reject) => {
      ApiService.get("/custom-data/poi")
        .then(response => {
          context.commit(SET_USER_CUSTOM_DATA, response.data);
          resolve(response.data);
        })
        .catch(({ response }) => {
          errorMessage(context, response, SET_ERROR);
          reject(response);
        });
    });
  },
  [GET_OPENAPI_CONFIG](context) {
    return new Promise((resolve, reject) => {
      ApiService.get("/openapi.json")
        .then(response => {
          context.commit(SET_OPENAPI_CONFIG, response.data);
          SwaggerParser.validate(response.data, (err, api) => {
            //TODO: Check swagger for validation errors here.
            resolve(api);
          });
        })
        .catch(({ response }) => {
          errorMessage(context, response, SET_ERROR);
          reject(response);
        });
    });
  }
};

const mutations = {
  updateField,
  [SET_ERROR](state, error) {
    state.errors = error;
  },
  [SET_APP_CONFIG](state, config) {
    state.appConfig = config;
  },
  /**
   * Restructures the POI icons to be easier to use for openlayers layer styling
   */
  [SET_POI_ICONS](state, config) {
    const icons = {};
    const poiAoiGroups = [...config.poi_groups, ...config.aoi_groups];
    poiAoiGroups.forEach(group => {
      const groupName = Object.keys(group)[0];
      const children = group[groupName].children;
      children.forEach(child => {
        const childName = Object.keys(child)[0];
        icons[childName] = {
          icon: child[childName].icon,
          color: child[childName].color[0]
        };
      });
    });
    state.poiIcons = icons;
  },
  [SET_USER_CUSTOM_DATA](state, customData) {
    state.uploadedData = customData;
  },
  [SET_OPENAPI_CONFIG](state, config) {
    state.openapiConfig = config;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
