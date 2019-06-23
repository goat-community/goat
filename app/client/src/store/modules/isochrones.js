import axios from "axios";
import { getField, updateField } from "vuex-map-fields";

const state = {
  position: {
    coordinate: null,
    city: null
  },
  options: {
    minutes: "10",
    speed: "20",
    steps: "2",
    concavityIsochrones: {
      name: "concavity",
      values: ["convex", "0", "1", "2", "3", "4", "5"],
      active: "0"
    },
    calculationModes: {
      name: "modus",
      values: [
        { display: "Default Network", value: "1" },
        { display: "Modified Network", value: "2" },
        { display: "Modified Network (Double Calculation)", value: "3" }
      ],
      active: "1"
    }
  },
  isochrones: [
    {
      id: 1,
      name: "Calculation1",
      isExpanded: true,
      position: "Müllerstraße 23, 80469 München",
      speed: "40 km/h",
      time: "3 min",
      data: [
        {
          type: "Default",
          range: "15 min",
          area: "250 km^2",
          visible: true,
          feature: {}
        },
        {
          type: "Default",
          range: "30 min",
          area: "500 km^2",
          visible: true,
          feature: {}
        },
        {
          type: "Input",
          range: "15 min",
          area: "250 km^2",
          visible: true,
          feature: {}
        },
        {
          type: "Input",
          range: "30 min",
          area: "503 km^2",
          visible: true,
          feature: {}
        }
      ]
    },
    {
      id: 2,
      name: "Calculation2",
      isExpanded: true,
      position: "Müllerstraße 100, 80468 Berlin",
      speed: "40 km/h",
      time: "3 min",
      data: [
        {
          type: "Default",
          range: "15 min",
          area: "250 km^2",
          visible: true
        },
        {
          type: "Default",
          range: "30 min",
          area: "500 km^2",
          visible: true
        },
        {
          type: "Input",
          range: "15 min",
          area: "250 km^2",
          visible: true
        },
        {
          type: "Input",
          range: "30 min",
          area: "503 km^2",
          visible: true
        }
      ]
    }
  ]
};

const getters = {
  allIsochrones: state => state.isochrones,
  options: state => state.options,
  getField
};

const actions = {
  async calculateIsochrone({ commit }) {
    let viewParams = "";
    //Isochrone Position Param
    if (state.position.coordinate !== null) {
      let x = state.position.coordinate[0];
      let y = state.position.coordinate[1];
      let param = `x:${x};y:${y};`;
      viewParams += param;
    } else {
      return;
    }

    //Isochrone Options Params
    Object.keys(state.options).forEach(key => {
      let value = state.options[key];
      let param;
      if (typeof value === "object") {
        param = value.name + ":" + value.active + ";";
      } else {
        param = key + ":" + value + ";";
      }
      viewParams += param;
    });

    //Temporary
    viewParams +=
      "userid_input:6545766;objectid_input:3194193;parent_id:1&typeNames=cite:save_isochrones";

    //Final URL
    let url = `https://goat.open-accessibility.org/geoserver/wfs?service=WFS&version=1.1.0&request=GetFeature&viewparams=${viewParams}`;
    console.log(url);
    //Request URL

    //Mock API
    const response = await axios.get(
      "http://5d0ba1fc89166d00146e39fb.mockapi.io/api/v2/isochrones"
    );

    //   let transformet = {};
    console.log(response.data);

    commit("CALCULATE_ISOCHRONE", response.data);
  },

  removeIsochrone({ commit }, id) {
    commit("REMOVE_ISOCHRONE", id);
  }
};

const mutations = {
  CALCULATE_ISOCHRONE(state, isochrone) {
    //TODO: ...
    //1- Transform isochrone data here and add it to the state
    //2- Add dada to state
    state.isochrones.unshift(isochrone);
  },
  REMOVE_ISOCHRONE(state, id) {
    state.isochrones = state.isochrones.filter(isochrone => isochrone.id != id);
  },
  UPDATE_POSITION(state, position) {
    Object.assign(state.position, position);
  },
  updateField
};

export default {
  state,
  getters,
  actions,
  mutations
};
