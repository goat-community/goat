import axios from "axios";
import { getField, updateField } from "vuex-map-fields";
import { toStringHDMS } from "ol/coordinate";
import { transform } from "ol/proj.js";
import maputils from "../../utils/MapUtils";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";

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
  isochroneLayer: null,
  styleData: {
    styleCache: {
      default: {},
      input: {}
    },
    defaultIsochroneColors: {
      "1": "#ffffe0",
      "2": "#fff2c7",
      "3": "#ffe4b1",
      "4": "#ffd69d",
      "5": "#ffc88e",
      "6": "#ffb981",
      "7": "#ffaa76",
      "8": "#ff9a6e",
      "9": "#fc8968",
      "10": "#f77a63",
      "11": "#f16b5f",
      "12": "#e95d5a",
      "13": "#e14f55",
      "14": "#d8404e",
      "15": "#cd3346",
      "16": "#c2263d",
      "17": "#b61832",
      "18": "#a80c25",
      "19": "#9b0316",
      "20": "#8b0000"
    },
    inputIsochroneColors: {
      "1": "#22D329",
      "2": "#20C830",
      "3": "#1EBD38",
      "4": "#1CB340",
      "5": "#1AA848",
      "6": "#199E50",
      "7": "#179358",
      "8": "#158860",
      "9": "#137E68",
      "10": "#117370",
      "11": "#106977",
      "12": "#0E5E7F",
      "13": "#0C5487",
      "14": "#0A498F",
      "15": "#083E97",
      "16": "#07349F",
      "17": "#0529A7",
      "18": "#031FAF",
      "19": "#0114B7",
      "20": "#000ABF"
    }
  }
};

const getters = {
  calculations: state => state.calculations,
  options: state => state.options,
  isochroneLayer: state => state.isochroneLayer,
  styleData: state => state.styleData,
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

    //Add center feature to isochrone layer
    let iconMarkerFeature = new Feature({
      geometry: new Point(
        transform(state.position.coordinate, "EPSG:4326", "EPSG:3857") //TODO: Get source projection from the map here.
      ),
      calculationNumber: state.calculations.length + 1
    });
    commit("ADD_ISOCHRONE_FEATURES", [iconMarkerFeature]);

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

    //Order features based on id
    isochrones.features.sort((a, b) => {
      return a.properties.id - b.properties.id;
    });

    //TODO: Don't get calculation options from state at this moment.
    const calculationNumber = state.calculations.length + 1;

    let olFeatures = maputils.geojsonToFeature(isochrones);
    olFeatures.forEach(feature => {
      console.log(maputils.getPolygonArea(feature.getGeometry()));
      let obj = {
        id: feature.getId(),
        type: feature.getProperties().modus,
        range: "15 min",
        area: maputils.getPolygonArea(feature.getGeometry()),
        isVisible: true
      };
      feature.set("isVisible", true);
      feature.set("calculationNumber", calculationNumber);
      calculationData.push(obj);
    });

    let transformedData = {
      id: calculationNumber,
      name: "Calculation - " + calculationNumber,
      time: state.options.minutes + " min",
      position: toStringHDMS(state.position.coordinate),
      speed: state.options.speed + " km/h",
      isExpanded: true,
      data: calculationData
    };

    iconMarkerFeature
      .getGeometry()
      .setCoordinates(maputils.getCenter(olFeatures[0].getGeometry()));
    commit("CALCULATE_ISOCHRONE", transformedData);

    //Add features to isochrone layer
    commit("ADD_ISOCHRONE_FEATURES", olFeatures);
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
    let isochronesId = calculation.id;
    let isochroneSource = state.isochroneLayer.getSource();
    isochroneSource.getFeatures().forEach(isochroneFeature => {
      if (isochroneFeature.get("calculationNumber") === isochronesId) {
        isochroneSource.removeFeature(isochroneFeature);
      }
    });
  },
  ADD_ISOCHRONE_FEATURES(state, features) {
    if (state.isochroneLayer) {
      state.isochroneLayer.getSource().addFeatures(features);
    }
  },
  TOGGLE_ISOCHRONE_FEATURE_VISIBILITY(state, feature) {
    let featureId = feature.id;
    feature.isVisible = !feature.isVisible;
    if (featureId) {
      let isochroneFeature = state.isochroneLayer
        .getSource()
        .getFeatureById(featureId);
      if (isochroneFeature) {
        isochroneFeature.set("isVisible", feature.isVisible);
      }
    }
  },
  ADD_STYLE_IN_CACHE(state, payload) {
    let style = payload.style;
    let isochroneType = payload.isochroneType;
    let styleName = payload.styleName;
    //Adds style into cache based on isochrone type
    state.styleData.styleCache[isochroneType][styleName] = style;
  },
  updateField
};

export default {
  state,
  getters,
  actions,
  mutations
};
