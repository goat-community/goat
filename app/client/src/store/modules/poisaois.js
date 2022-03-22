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
  dynamicHeatmapTravelTimes: [
    0,
    10,
    20,
    30,
    40,
    50,
    60,
    70,
    80,
    90,
    100,
    110,
    120,
    130,
    140,
    150,
    160,
    170,
    180,
    190,
    200,
    210,
    220,
    230,
    240,
    250,
    260,
    270,
    280,
    290,
    300,
    310,
    320,
    330,
    340,
    350,
    360,
    370,
    380,
    390,
    400,
    410,
    420,
    430,
    440,
    450,
    460,
    470,
    480,
    490,
    500,
    510,
    520,
    530,
    540,
    550,
    560,
    570,
    580,
    590,
    600,
    610,
    620,
    630,
    640,
    650,
    660,
    670,
    680,
    690,
    700,
    710,
    720,
    730,
    740,
    750,
    760,
    770,
    780,
    790,
    800,
    810,
    820,
    830,
    840,
    850,
    860,
    870,
    880,
    890,
    900,
    910,
    920,
    930,
    940,
    950,
    960,
    970,
    980,
    990,
    1000,
    1010,
    1020,
    1030,
    1040,
    1050,
    1060,
    1070,
    1080,
    1090,
    1100,
    1110,
    1120,
    1130,
    1140,
    1150,
    1160,
    1170,
    1180,
    1190,
    1200
  ],
  treeViewKey: 0 // Used for re-rendering the tree view
};

const getters = {
  dynamicHeatmapTravelTimes: state => state.dynamicHeatmapTravelTimes,
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
