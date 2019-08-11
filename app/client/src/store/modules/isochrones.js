import http from "../../services/http";
import { getField, updateField } from "vuex-map-fields";
import { toStringHDMS } from "ol/coordinate";
import { transform } from "ol/proj.js";

import maputils from "../../utils/MapUtils";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import IsochroneUtils from "../../utils/IsochroneUtils";

const state = {
  position: {
    coordinate: null,
    placeName: ""
  },
  options: {
    minutes: "10",
    speed: "5",
    steps: "2",
    concavityIsochrones: {
      name: "concavity",
      values: [
        { display: "convex", value: "1" },
        { display: "0", value: "0.99" },
        { display: "1", value: "0.98" },
        { display: "2", value: "0.95" },
        { display: "3", value: "0.9" },
        { display: "4", value: "0.8" },
        { display: "5", value: "0.7" }
      ],
      active: "0.99"
    },
    calculationModes: {
      name: "modus",
      values: [
        { display: "Default Network", value: "default" },
        { display: "Modified Network", value: "scenario" },
        {
          display: "Modified Network (Double Calculation)",
          value: "comparison"
        }
      ],
      active: "default"
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
  },
  isThematicDataVisible: false,
  selectedThematicData: null
};

const getters = {
  calculations: state => state.calculations,
  options: state => state.options,
  isochroneLayer: state => state.isochroneLayer,
  styleData: state => state.styleData,
  isThematicDataVisible: state => state.isThematicDataVisible,
  selectedThematicData: state => state.selectedThematicData,
  getField
};

const actions = {
  async calculateIsochrone({ commit, rootState }) {
    //Add center feature to isochrone layer
    let iconMarkerFeature = new Feature({
      geometry: new Point(
        transform(state.position.coordinate, "EPSG:4326", "EPSG:3857") //TODO: Get source projection from the map here.
      ),
      calculationNumber: state.calculations.length + 1
    });
    commit("ADD_ISOCHRONE_FEATURES", [iconMarkerFeature]);

    const isochronesResponse = await http.get("/api/isochrone", {
      params: {
        user_id: rootState.user.userId,
        minutes: state.options.minutes,
        x: state.position.coordinate[0],
        y: state.position.coordinate[1],
        n: state.options.steps,
        concavity: state.options.concavityIsochrones.active,
        speed: state.options.speed,
        modus: state.options.calculationModes.active
      }
    });

    let isochrones = isochronesResponse.data;
    let calculationData = [];

    //TODO: Don't get calculation options from state at this moment.
    const calculationNumber = state.calculations.length + 1;

    let olFeatures = maputils.geojsonToFeature(isochrones);
    //Order features based on id
    olFeatures.sort((a, b) => {
      return a.get("step") - b.get("step");
    });

    olFeatures.forEach(feature => {
      feature.getGeometry().transform("EPSG:4326", "EPSG:3857");
      let color = "";
      let level = feature.get("step");
      let modus = feature.get("modus");

      // If the modus is 1 it is a default isochrone, otherwise is a input or double calculation
      if (modus === 1 || modus === 3) {
        color = state.styleData.defaultIsochroneColors[level];
      } else {
        color = state.styleData.inputIsochroneColors[level];
      }
      let obj = {
        id: feature.getId(),
        type: IsochroneUtils.getIsochroneAliasFromKey(
          feature.getProperties().modus
        ),
        range: feature.getProperties().step + " min",
        color: color,
        area: maputils.getPolygonArea(feature.getGeometry()),
        isVisible: true
      };
      feature.set("isVisible", true);
      feature.set("calculationNumber", calculationNumber);
      feature.set("color", color);

      calculationData.push(obj);
    });

    const isochroneStartingPoint = maputils
      .wktToFeature(olFeatures[0].get("starting_point"), "EPSG:4326")
      .getGeometry()
      .getCoordinates();

    console.log(state.position.placeName);
    let transformedData = {
      id: calculationNumber,
      name: "Calculation - " + calculationNumber,
      time: state.options.minutes + " min",
      position:
        state.position.placeName ||
        toStringHDMS(isochroneStartingPoint || state.position.coordinate),
      speed: state.options.speed + " km/h",
      isExpanded: true,
      isVisible: true,
      data: calculationData
    };

    const transformedPoint = new Point(
      transform(isochroneStartingPoint, "EPSG:4326", "EPSG:3857") //TODO: Get source projection from the map here.
    );
    iconMarkerFeature.setGeometry(transformedPoint);

    if (state.position.placeName) {
      maputils.flyTo(
        transformedPoint.getCoordinates(),
        rootState.map.map,
        function() {}
      );
    }

    commit("CALCULATE_ISOCHRONE", transformedData);
    //Add features to isochrone layer
    commit("ADD_ISOCHRONE_FEATURES", olFeatures);
  },

  removeCalculation({ commit }, calculation) {
    commit("REMOVE_ISOCHRONE_FEATURES", calculation);
    commit("REMOVE_CALCULATION", calculation);
  },

  setSelectedThematicData({ commit, rootState }, thematicDataObject) {
    //Assign Selected Pois from the tree
    thematicDataObject.filterSelectedPois = rootState.pois.selectedPois;
    commit("SET_SELECTED_THEMATIC_DATA", thematicDataObject);
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
  TOGGLE_ISOCHRONE_CALCULATION_VISIBILITY(state, calculation) {
    calculation.isVisible = !calculation.isVisible;

    calculation.data.forEach(isochrone => {
      let featureId = isochrone.id;
      isochrone.isVisible = calculation.isVisible;
      let isochroneFeature = state.isochroneLayer
        .getSource()
        .getFeatureById(featureId);
      if (isochroneFeature) {
        isochroneFeature.set("isVisible", calculation.isVisible);
      }
    });
  },
  ADD_STYLE_IN_CACHE(state, payload) {
    let style = payload.style;
    let isochroneType = payload.isochroneType;
    let styleName = payload.styleName;
    //Adds style into cache based on isochrone type
    state.styleData.styleCache[isochroneType][styleName] = style;
  },
  updateField,
  TOGGLE_THEMATIC_DATA_VISIBILITY(state, isVisible) {
    state.isThematicDataVisible = isVisible;
  },
  SET_SELECTED_THEMATIC_DATA(state, thematicDataObject) {
    state.selectedThematicData = thematicDataObject;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
