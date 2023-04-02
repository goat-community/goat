import { getField, updateField } from "vuex-map-fields";
import ApiService from "../../services/api.service";
import { GET_POIS_AOIS } from "../actions.type";
import { geobufToFeatures } from "../../utils/MapUtils";
//parts of the data will be loaded dynamically from app conf json

const state = {
  poisAoisLayer: null,
  poisAoisGroupingLayer: null,
  poisAois: {},
  rawPoisAois: {},
  rawGroupPoisAois: {},
  lengthPois: 0,
  selectedPoisAois: [],
  treeViewKey: 0 // Used for re-rendering the tree view
};

const getters = {
  dynamicIndicatorTravelTimes: () => {
    const dynamicIndicatorTravelTimes = [];
    for (let i = 0; i <= 120; i++) {
      dynamicIndicatorTravelTimes.push(i * 10);
    }
    return dynamicIndicatorTravelTimes;
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
  [GET_POIS_AOIS]({ state }) {
    return new Promise((resolve, reject) => {
      ApiService.get_(`/pois-aois/visualization?return_type=geobuf`, {
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

            olFeatures.forEach(oneFeature => {
              if (oneFeature.get("category") in state.rawPoisAois) {
                state.rawPoisAois[oneFeature.get("category")].push(oneFeature);
              } else {
                state.rawPoisAois[oneFeature.get("category")] = [];
              }
            });

            if (olFeatures.length > 45000) {
              state.poisAoisLayer.setMinZoom(14);

              state.poisAoisGroupingLayer.setMinZoom(14);
              state.poisAoisGroupingLayer.setMaxZoom(16);
            }
          }
        })
        .catch(({ response }) => {
          reject(response);
        });
      ApiService.get_(
        `/pois-aois/visualization?return_type=geobuf&grouped_multi_entrance=true`,
        {
          responseType: "arraybuffer",
          headers: {
            Accept: "application/pdf"
          }
        }
      )
        .then(response => {
          resolve(response);
          if (response.data) {
            resolve(response.data);
            const olFeatures = geobufToFeatures(response.data, {
              dataProjection: "EPSG:4326",
              featureProjection: "EPSG:3857"
            });

            olFeatures.forEach(oneFeature => {
              if (oneFeature.get("category") in state.rawGroupPoisAois) {
                state.rawGroupPoisAois[oneFeature.get("category")].push(
                  oneFeature
                );
              } else {
                state.rawGroupPoisAois[oneFeature.get("category")] = [];
              }
            });
          }
        })
        .catch(({ response }) => {
          reject(response);
        });
    });
  }
};

const mutations = {
  updateField
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
