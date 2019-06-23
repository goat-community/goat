import axios from "axios";
import { getField, updateField } from "vuex-map-fields";
import { toStringHDMS } from "ol/coordinate";
import maputils from "../../utils/MapUtils";

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
  calculations: [],
  isochroneLayer: null
};

const getters = {
  calculations: state => state.calculations,
  options: state => state.options,
  isochroneLayer: state => state.isochroneLayer,
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
    let isochrones = response.data[0];
    let calculationData = [];

    let olFeatures = maputils.geojsonToFeature(isochrones);

    olFeatures.forEach(feature => {
      let obj = {
        type: feature.getProperties().modus,
        range: "15 min",
        area: "250 km^2",
        visible: true,
        feature: feature
      };
      calculationData.push(obj);
    });

    //TODO: Don't get calculation options from state at this moment.
    const isochroneId = state.calculations.length + 1;
    let transformedData = {
      id: isochroneId,
      name: "Calculation - " + isochroneId,
      time: state.options.minutes + " min",
      position: toStringHDMS(state.position.coordinate),
      speed: state.options.speed + " km/h",
      isExpanded: true,
      data: calculationData
    };

    commit("CALCULATE_ISOCHRONE", transformedData);

    //Add features to isochrone layer
    if (state.isochroneLayer) {
      state.isochroneLayer.getSource().addFeatures(olFeatures);
    }
  },

  removeCalculation({ commit }, calculation) {
    commit("REMOVE_ISOCHRONE_FEATURES", calculation);
    commit("REMOVE_CALCULATION", calculation);
  }
};

const mutations = {
  CALCULATE_ISOCHRONE(state, isochrone) {
    state.calculations.unshift(isochrone);
  },

  UPDATE_POSITION(state, position) {
    Object.assign(state.position, position);
  },
  ADD_ISOCHRONE_LAYER(state, layer) {
    state.isochroneLayer = layer;
  },
  CLEAR_ISOCHRONE_LAYER(state) {
    state.isochroneLayer.getSource().clear();
  },
  REMOVE_CALCULATION(state, calculation) {
    let id = calculation.id;
    state.calculations = state.calculations.filter(
      calculation => calculation.id != id
    );
  },
  REMOVE_ISOCHRONE_FEATURES(state, calculation) {
    var isochrones = calculation.data;
    isochrones.forEach(isochrone => {
      state.isochroneLayer.getSource().removeFeature(isochrone.feature);
    });
  },
  TOGGLE_ISOCHRONE_FEATURE_VISIBILITY() {},
  updateField
};

export default {
  state,
  getters,
  actions,
  mutations
};
