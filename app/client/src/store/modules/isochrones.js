import http from "../../services/http";
import axios from "axios";

import { getField, updateField } from "vuex-map-fields";
import { toStringHDMS } from "ol/coordinate";
import { transform } from "ol/proj.js";

import {
  geojsonToFeature,
  getPolygonArea,
  wktToFeature,
  flyTo
} from "../../utils/MapUtils";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import IsochroneUtils from "../../utils/IsochroneUtils";

const state = {
  position: {
    coordinate: null,
    placeName: ""
  },
  options: {
    calculationType: "single",
    minutes: "10",
    speed: "5",
    steps: "2",
    concavityIsochrones: {
      name: "concavity",
      values: [
        { display: "0", value: "0.00003" },
        { display: "1", value: "0.000003" },
        { display: "2", value: "0.0000025" },
        { display: "3", value: "0.000002" },
        { display: "4", value: "0.0000017" },
        { display: "5", value: "0.0000015" }
      ],
      active: "0.00003"
    },
    calculationModes: {
      name: "modus",
      values: [
        {
          display: "Default Network",
          name: "defaultNetwork",
          value: "default"
        },
        {
          display: "Modified Network",
          name: "modifiedNetwork",
          value: "scenario"
        },
        {
          display: "Modified Network (Double Calculation)",
          name: "modifiedNetworkDoubleCalc",
          value: "comparison"
        }
      ],
      active: "default"
    },
    alphaShapeParameter: {
      name: "alphashape",
      values: [{ display: "0.00003", value: "0.00003" }],
      active: "0.00003"
    }
  },
  calculations: [],
  multiIsochroneCalculationMethods: {
    name: "multiIsochroneCalculationMethods",
    values: [
      {
        display: "Study Area",
        name: "studyArea",
        value: "study_area"
      },
      {
        display: "Draw Boundary",
        name: "drawBoundary",
        value: "draw"
      }
    ],
    active: null
  },
  isochroneLayer: null,
  selectionLayer: null,
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
  selectionLayer: state => state.selectionLayer,
  styleData: state => state.styleData,
  isThematicDataVisible: state => state.isThematicDataVisible,
  selectedThematicData: state => state.selectedThematicData,
  alphaShapeParameter: state => state.alphaShapeParameter,
  multiIsochroneCalculationMethods: state =>
    state.multiIsochroneCalculationMethods,
  countPois: state => {
    let count = 0;
    if (state.selectionLayer) {
      count = state.selectionLayer
        .getSource()
        .getFeatures()
        .reduce((accumulator, currentValue) => {
          return accumulator + currentValue.get("count_pois");
        }, 0);
    }
    return count;
  },
  getField
};

const actions = {
  async calculateIsochrone({ commit, rootState }) {
    //Selected isochrone calculation type. single | multiple
    const calculationType = rootState.isochrones.options.calculationType;
    const sharedParams = {
      user_id: rootState.user.userId,
      minutes: state.options.minutes,
      speed: state.options.speed,
      n: state.options.steps,
      modus: state.options.calculationModes.active
    };
    let isochroneEndpoint;
    let params;

    //Marker Feature for single isochrone calculation;
    let iconMarkerFeature;

    if (calculationType === "single") {
      iconMarkerFeature = new Feature({
        geometry: new Point(
          transform(state.position.coordinate, "EPSG:4326", "EPSG:3857") //TODO: Get source projection from the map here.
        ),
        calculationNumber: state.calculations.length + 1
      });
      commit("ADD_ISOCHRONE_FEATURES", [iconMarkerFeature]);

      params = Object.assign(sharedParams, {
        x: state.position.coordinate[0],
        y: state.position.coordinate[1],
        concavity: state.options.concavityIsochrones.active
      });
      isochroneEndpoint = "isochrone";
    } else {
      const regionType = state.multiIsochroneCalculationMethods.active;
      const regionFeatures = state.selectionLayer.getSource().getFeatures();
      const region = regionFeatures
        .map(feature => {
          if (regionType === "draw") {
            return feature
              .get("regionEnvelope")
              .split(",")
              .map(coord => {
                return `'${coord}'`;
              })
              .toString();
          } else {
            return `'${feature.get("region_name")}'`;
          }
        })
        .toString();

      params = Object.assign(sharedParams, {
        alphashape_parameter: parseFloat(
          state.options.alphaShapeParameter.active
        ),
        region_type: `'${regionType}'`,
        region: region,
        amenities: rootState.pois.selectedPois
          .map(item => {
            return "'" + item.value + "'";
          })
          .toString()
      });
      params.modus = `'${state.options.calculationModes.active}'`;
      isochroneEndpoint = "pois_multi_isochrones";
    }

    const isochronesResponse = await http.post(
      `/api/${isochroneEndpoint}`,
      params
    );
    let isochrones = isochronesResponse.data;
    let calculationData = [];

    //TODO: Don't get calculation options from state at this moment.
    const calculationNumber = state.calculations.length + 1;

    let olFeatures = geojsonToFeature(isochrones);
    //Order features based on id
    olFeatures.sort((a, b) => {
      return a.get("step") - b.get("step");
    });

    olFeatures.forEach(feature => {
      feature.getGeometry().transform("EPSG:4326", "EPSG:3857");
      let color = "";
      let level = feature.get("step");
      let modus = feature.get("modus");

      //Remove coordinates property (multi-isochrones not printing, probably a bug. )
      feature.unset("coordinates");
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
        area: getPolygonArea(feature.getGeometry()),
        isVisible: true
      };
      feature.set("isVisible", true);
      feature.set("calculationNumber", calculationNumber);
      feature.set("color", color);

      calculationData.push(obj);
    });

    let transformedData = {
      id: calculationNumber,
      calculationType: calculationType,
      time: state.options.minutes + " min",
      speed: state.options.speed + " km/h",
      isExpanded: true,
      isVisible: true,
      data: calculationData
    };

    if (calculationType === "single") {
      const isochroneStartingPoint = wktToFeature(
        olFeatures[0].get("starting_point"),
        "EPSG:4326"
      )
        .getGeometry()
        .getCoordinates();
      const transformedPoint = new Point(
        transform(isochroneStartingPoint, "EPSG:4326", "EPSG:3857") //TODO: Get source projection from the map here.
      );
      iconMarkerFeature.setGeometry(transformedPoint);
      if (state.position.placeName) {
        flyTo(
          transformedPoint.getCoordinates(),
          rootState.map.map,
          function() {}
        );
      }
      transformedData.position =
        state.position.placeName ||
        toStringHDMS(isochroneStartingPoint || state.position.coordinate) ||
        "";
    } else {
      commit("RESET_MULTIISOCHRONE_START");
      transformedData.position = "multiIsochroneCalculation";
    }

    commit("CALCULATE_ISOCHRONE", transformedData);
    //Add features to isochrone layer
    commit("ADD_ISOCHRONE_FEATURES", olFeatures);
  },

  async countStudyAreaPois({ commit, rootState }, options) {
    if (!rootState.isochrones.selectionLayer) return;
    const selectedFeatures = rootState.isochrones.selectionLayer
      .getSource()
      .getFeatures();
    if (selectedFeatures.length > 0 || options) {
      const amenities = rootState.pois.selectedPois
        .map(item => {
          return "'" + item.value + "'";
        })
        .toString();
      if (amenities === "") {
        commit(
          "map/TOGGLE_SNACKBAR",
          {
            type: "error",
            message: "selectAmenities",
            state: true
          },
          { root: true }
        );
        //Reset all study area features count_point property to zero.
        selectedFeatures.forEach(feature => {
          feature.set("count_pois", 0);
        });
        return;
      }
      const params = {
        minutes: rootState.isochrones.options.minutes,
        speed: rootState.isochrones.options.speed,
        amenities: amenities
      };
      let promiseArray = [];
      if (options) {
        promiseArray.push(
          http.post(
            "/api/count_pois_multi_isochrones",
            Object.assign(
              {
                region_type: options.regionType,
                region: options.region
              },
              params
            )
          )
        );
      } else {
        const promises = selectedFeatures.map(feature => {
          return http.post(
            "/api/count_pois_multi_isochrones",
            Object.assign(
              {
                region_type: feature.get("region_type"),
                region: feature.get("region")
              },
              params
            )
          );
        });
        promiseArray = [...promises];
      }

      axios.all(promiseArray).then(results => {
        if (!options) {
          rootState.isochrones.selectionLayer.getSource().clear();
        }

        results.map(response => {
          const configData = JSON.parse(response.config.data);
          if (response.data.feature) {
            const olFeatures = geojsonToFeature(response.data.feature);
            olFeatures.forEach(feature => {
              feature.getGeometry().transform("EPSG:4326", "EPSG:3857");
              feature.set("region_type", configData.region_type);
              feature.set("region", configData.region);

              if (configData.region_type === "'draw'") {
                feature.set("regionEnvelope", configData.region);
              }
            });
            commit("ADD_STUDYAREA_FEATURES", olFeatures);
          }
        });
      });
    }
  },
  removeCalculation({ commit }, calculation) {
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
  ADD_SELECTION_LAYER(state, layer) {
    state.selectionLayer = layer;
  },
  RESET_MULTIISOCHRONE_START(state) {
    state.multiIsochroneCalculationMethods.active = null;
  },
  CLEAR_ISOCHRONE_LAYER(state) {
    state.isochroneLayer.getSource().clear();
  },
  REMOVE_CALCULATION(state, calculation) {
    let id = calculation.id;
    state.calculations = state.calculations.filter(
      calculation => calculation.id != id
    );
    state.calculations = state.calculations.map(calculation => {
      if (calculation.id > id) {
        calculation.id = calculation.id - 1;
      }
      return calculation;
    });
    let isochroneSource = state.isochroneLayer.getSource();
    isochroneSource.getFeatures().forEach(isochroneFeature => {
      const isochroneCalculationNr = isochroneFeature.get("calculationNumber");
      if (isochroneCalculationNr === id) {
        isochroneSource.removeFeature(isochroneFeature);
      }
      if (isochroneCalculationNr > id) {
        isochroneFeature.set("calculationNumber", isochroneCalculationNr - 1);
      }
    });
  },
  ADD_ISOCHRONE_FEATURES(state, features) {
    if (state.isochroneLayer) {
      state.isochroneLayer.getSource().addFeatures(features);
    }
  },
  ADD_STUDYAREA_FEATURES(state, features) {
    if (state.selectionLayer) {
      state.selectionLayer.getSource().addFeatures(features);
    }
  },
  REMOVE_STUDYAREA_FEATURES(state) {
    state.selectionLayer.getSource().clear();
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
