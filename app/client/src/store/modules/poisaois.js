import { getField, updateField } from "vuex-map-fields";
import ApiService from "../../services/api.service";
import { GET_POIS_AOIS } from "../actions.type";
import { SET_POIS_AOIS } from "../mutations.type";
import { geobufToFeatures } from "../../utils/MapUtils";
//parts of the data will be loaded dynamically from app conf json

const state = {
  poisAoisLayer: null,
  poisAois: {},
  selectedPoisAois: [],
  treeViewKey: 0 // Used for re-rendering the tree view
};

const getters = {
  dynamicHeatmapTravelTimes: () => {
    const dynamicHeatmapTravelTimes = [];
    for (let i = 0; i <= 120; i++) {
      dynamicHeatmapTravelTimes.push(i * 10);
    }
    return dynamicHeatmapTravelTimes;
  },
  poisAois: state => state.poisAois,
  poisAoisLayer: state => state.poisAoisLayer,
  // eslint-disable-next-line no-unused-vars
  selectedPois: (state, getters, rootState, rootGetters) => {
    const poisConfig = rootGetters["app/poisConfig"];
    const pois = state.selectedPoisAois.filter(poi => {
      if (poisConfig[poi.value]) {
        return true;
      } else {
        return false;
      }
    });
    return pois;
  },
  selectedPoisOnlyKeys: (state, getters) => {
    const selectedPoiKeys = [];
    getters.selectedPois.forEach(poi => {
      selectedPoiKeys.push(poi.value);
    });
    return selectedPoiKeys;
  },
  // eslint-disable-next-line no-unused-vars
  selectedAois: (state, getters, rootState, rootGetters) => {
    const aoisConfig = rootGetters["app/aoisConfig"];
    const aois = state.selectedPoisAois.filter(aoi => {
      if (aoisConfig[aoi.value]) {
        return true;
      } else {
        return false;
      }
    });
    return aois;
  },
  selectedAoisOnlyKeys: (state, getters) => {
    const selectedAoiKeys = [];
    getters.selectedAois.forEach(aoi => {
      selectedAoiKeys.push(aoi.value);
    });
    return selectedAoiKeys;
  },

  getField
};

const actions = {
  [GET_POIS_AOIS](context) {
    return new Promise((resolve, reject) => {
      ApiService.get_(`/pois-aois/visualization?return_type=db_geobuf`, {
        responseType: "arraybuffer",
        headers: {
          Accept: "application/pdf"
        }
      })
        .then(response => {
          resolve(response);
          if (response.data) {
            resolve(response.data);
            const olFeatures = geobufToFeatures(response.data, {
              dataProjection: "EPSG:4326",
              featureProjection: "EPSG:3857"
            });
            context.commit(SET_POIS_AOIS, olFeatures);
          }
        })
        .catch(({ response }) => {
          reject(response);
        });
    });
  }
};

const mutations = {
  updateField,
  [SET_POIS_AOIS](state, poisAois) {
    if (state.poisAoisLayer) {
      state.poisAoisLayer.getSource().clear();
      state.poisAoisLayer.getSource().addFeatures(poisAois);

      state.selectedPoisAois = JSON.parse(
        JSON.stringify(state.selectedPoisAois)
      );
    }
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
