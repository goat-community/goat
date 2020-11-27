import { getField, updateField } from "vuex-map-fields";
import { toggleTreeLockState } from "../../utils/PoisUtils";

//parts of the data will be loaded dynamically from app conf json

const state = {
  allPois: [],
  selectedPois: [],
  filters: {},
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
  timeFilter: {
    day: {
      values: [
        { value: 18, display: "monday" },
        { value: 19, display: "tuesday" },
        { value: 20, display: "wednesday" },
        { value: 21, display: "thursday" },
        { value: 22, display: "friday" },
        { value: 23, display: "saturday" },
        { value: 24, display: "sunday" }
      ],
      active: "" //no day
    },
    hour: null //no day
  }
};

const getters = {
  selectedPois: state => state.selectedPois,
  allPois: state => state.allPois,
  disabledPoisOnTimeFilter: state => state.filters.disabledPoisOnTimeFilter,
  disabledPoisOnRoutingProfile: state =>
    state.filters.disabledPoisOnRoutingProfile,
  disabledPoisOnMappingMode: state => state.filters.disabledPoisOnMappingMode,
  dynamicHeatmapTravelTimes: state => state.dynamicHeatmapTravelTimes,
  timeFilter: state => state.timeFilter,
  getField
};

const actions = {
  updateSelectedPoisForThematicData({ rootState }, selectedPois) {
    if (rootState.isochrones.selectedThematicData) {
      rootState.isochrones.selectedThematicData.filterSelectedPois = selectedPois;
    }
  }
};

const mutations = {
  INIT(state, config) {
    if (config && typeof config === "object") {
      for (const key of Object.keys(config)) {
        state[key] = config[key];
      }
    }
  },
  TOGGLE_NODE_STATE(state, payload) {
    const { excluded, nodeState } = payload;
    //Node state can have 2 values (activate / deactivate)

    excluded.forEach(element => {
      const { categoryValue, poisFiltered } = element;
      // setTimeout added to bypass a treeview bug.
      setTimeout(() => {
        state.allPois.forEach(category => {
          if (category.categoryValue === categoryValue) {
            //1- Locks all the category
            if (poisFiltered.length === 1 && poisFiltered[0] === "*") {
              toggleTreeLockState(category, nodeState);
            }
            //2- Locks certain pois in the category
            if (poisFiltered.length >= 1) {
              category.children.forEach(pois => {
                if (poisFiltered.includes(pois.value)) {
                  toggleTreeLockState(pois, nodeState);
                }
              });
            }
          }
        });
      }, 100);

      //Unselect all pois if those are previosly selected and excluded from filters
      if (nodeState === "activate") {
        let _poisFilteredObj = [];
        if (poisFiltered.length === 1 && poisFiltered[0] === "*") {
          _poisFilteredObj = state.allPois.filter(
            el => el.categoryValue === categoryValue
          );

          _poisFilteredObj = _poisFilteredObj[0].children.map(
            item => item.value
          );
        } else {
          _poisFilteredObj = poisFiltered;
        }

        let obj = state.selectedPois.filter(el => {
          return !_poisFilteredObj.includes(el.value);
        });

        state.selectedPois = obj;
      }
    });
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
