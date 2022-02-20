import ApiService from "../../services/api.service";
import { getField, updateField } from "vuex-map-fields";
import { GET_APP_CONFIG } from "../actions.type";
import { SET_APP_CONFIG, SET_ERROR } from "../mutations.type";
import { errorMessage } from "../../utils/Helpers";

const state = {
  errors: null,
  appConfig: null,
  layerTabIndex: 0,
  calculationMode: {
    values: ["default", "scenario", "comparision"],
    active: "default"
  },
  activeColor: {
    primary: "#2BB381",
    secondary: "#2BB381"
  }
};

const getters = {
  appConfig: state => state.appConfig,
  calculationMode: state => state.calculationMode,
  appColor: state => {
    return state.appConfig.app_ui.base_color;
  },
  vectorTileStyles: state => {
    const layerGroups = state.appConfig.layer_groups;
    const styles = {};
    layerGroups.forEach(layerGroup => {
      layerGroup.layers.forEach(layer => {
        if (layer.style) {
          styles[layer.name] = {};
          styles[layer.name]["style"] = layer.style;
        }
        if (layer.translation) {
          styles[layer.name]["translation"] = layer.style;
        }
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
  poiAoiTree: state => {
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
        children: restructuredChildren
      };
      treeStruct.push(groupTreeStruct);
    });
    return treeStruct;
  },
  activeColor: state => state.activeColor,
  getField
};

const actions = {
  [GET_APP_CONFIG](context) {
    return new Promise((resolve, reject) => {
      ApiService.get("/customizations/me")
        .then(response => {
          context.commit(SET_APP_CONFIG, response.data);
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
  updateField,
  [SET_ERROR](state, error) {
    state.errors = error;
  },
  [SET_APP_CONFIG](state, config) {
    state.appConfig = config;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
