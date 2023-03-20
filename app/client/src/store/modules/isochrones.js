import { getField, updateField } from "vuex-map-fields";

const state = {
  type: "single",
  time: 10,
  speed: 5,
  steps: 2,
  routing: "walking_standard",
  // Style
  defaultIsochroneColor: "b",
  scenarioIsochroneColor: "f",
  colors: {
    a: {
      "1": "rgb(254, 202, 232)",
      "2": "rgb(254, 144, 207)",
      "3": "rgb(239, 002, 140)",
      "4": "rgb(179, 001, 103)",
      "5": "rgb(125, 001, 072)"
    },
    b: {
      "1": "rgb(251, 188, 175)",
      "2": "rgb(247, 122, 099)",
      "3": "rgb(234, 049, 012)",
      "4": "rgb(186, 039, 010)",
      "5": "rgb(116, 024, 006)"
    },
    c: {
      "1": "rgb(255, 200, 142)",
      "2": "rgb(255, 171, 079)",
      "3": "rgb(238, 125, 000)",
      "4": "rgb(192, 101, 000)",
      "5": "rgb(126, 066, 000)"
    },
    d: {
      "1": "rgb(254, 229, 168)",
      "2": "rgb(253, 216, 123)",
      "3": "rgb(252, 193, 044)",
      "4": "rgb(231, 166, 003)",
      "5": "rgb(193, 139, 003)"
    },
    e: {
      "1": "rgb(232, 240, 182)",
      "2": "rgb(202, 220, 094)",
      "3": "rgb(182, 206, 044)",
      "4": "rgb(143, 161, 035)",
      "5": "rgb(104, 117, 025)"
    },
    f: {
      "1": "rgb(220, 241, 211)",
      "2": "rgb(173, 223, 153)",
      "3": "rgb(097, 190, 060)",
      "4": "rgb(071, 140, 044)",
      "5": "rgb(054, 105, 033)"
    },
    g: {
      "1": "rgb(201, 237, 236)",
      "2": "rgb(144, 216, 214)",
      "3": "rgb(066, 190, 187)",
      "4": "rgb(052, 152, 150)",
      "5": "rgb(039, 111, 109)"
    },
    h: {
      "1": "rgb(197, 218, 237)",
      "2": "rgb(126, 172, 214)",
      "3": "rgb(066, 133, 194)",
      "4": "rgb(042, 105, 162)",
      "5": "rgb(032, 081, 126)"
    },
    i: {
      "1": "rgb(255, 255, 255)",
      "2": "rgb(207, 207, 207)",
      "3": "rgb(159, 159, 159)",
      "4": "rgb(090, 090, 090)",
      "5": "rgb(000, 000, 000)"
    }
  },
  isochroneLayer: null,
  isochroneRoadNetworkLayer: null,
  multiIsochroneMethod: null,
  multiIsochroneSelectionLayer: null,
  calculations: [],
  isochroneOverlayLayer: null,
  selectedCalculations: [], // Array of selected isochrones
  // Public transport options
  publicTransport: {
    accessMode: "walking",
    weekday: 0,
    egressMode: "walking",
    fromTime: "07:00",
    toTime: "08:00",
    transitModes: []
  },
  chartDatasetType: 0, // 0: population, 1: pois, 2: aois
  isochroneRange: 10, // in minutes
  preDefCalculationColors: [
    "#28364880",
    "#eb391580",
    "#8B939E80",
    "#71BE8E80",
    "#37BCC980",
    "#af838380",
    "#D8812280",
    "#998ec380",
    "#2c7fb880",
    "#5E191680"
  ], // 10 different colors
  calculationColors: [],
  calculationSrokeObjects: [],
  calculationTravelTime: [],
  // Cancel Request
  cancelReq: undefined,
  selectedCalculationChangeColor: null,
  isochroneResultWindow: false,
  transitRouteTypes: {
    tram: 0,
    subway: 1,
    rail: 2,
    bus: 3,
    ferry: 4,
    cable_tram: 5,
    aerial_lift: 6,
    funicular: 7,
    trolleybus: 11,
    monorail: 12,
    railway_service: 100,
    high_speed_rail_service: 101,
    long_distance_trains: 102,
    inter_regional_rail_service: 103
  },
  transitRouteTypeExtensions: [
    {
      type: "high_speed_rail_service",
      color: "#ADD8E6"
    },
    {
      type: "long_distance_trains",
      color: "#849e78"
    },
    {
      type: "inter_regional_rail_service",
      color: "#e055ce"
    }
    /*
    ferry: 4,
    cable_tram: 5,
    aerial_lift: 6,
    funicular: 7,
    trolleybus: 11,
    monorail: 12,
    railway_service: 100,
    high_speed_rail_service: 101,
    long_distance_trains: 102,
    inter_regional_rail_service: 103
    */
  ]
};

const getters = {
  colors: state => state.colors,
  type: state => state.type,
  isochroneLayer: state => state.isochroneLayer,
  selectedCalculations: state => state.selectedCalculations,
  isochroneRange: state => state.isochroneRange,
  calculations: state => state.calculations,
  calculationColors: state => state.calculationColors,
  preDefCalculationColors: state => state.preDefCalculationColors,
  calculationSrokeObjects: state => state.calculationSrokeObjects,
  calculationTravelTime: state => state.calculationTravelTime,
  selectedCalculationChangeColor: state => state.selectedCalculationChangeColor,
  chartDatasetType: state => state.chartDatasetType,
  isochroneResultWindow: state => state.isochroneResultWindow,
  // eslint-disable-next-line no-unused-vars
  timeDelta: (state, getters, rootState) => {
    let time =
      (rootState.app.timeIndicators.endTime -
        rootState.app.timeIndicators.startTime) /
      3600;
    return time;
  },
  // eslint-disable-next-line no-unused-vars
  routingProfiles: (state, getters, rootState, rootGetters) => {
    let routingProfiles = {};
    const routing = rootState.app.appConfig.routing;
    routing.forEach(r => {
      routingProfiles[r.type] = r;
    });
    return routingProfiles;
  },
  transitRouteTypes: state => state.transitRouteTypes,
  // eslint-disable-next-line no-unused-vars
  transitRouteTypesByNr: (state, getters, rootState, rootGetters) => {
    let obj = {};
    const routing = rootState.app.appConfig.routing.filter(
      r => r.type === "transit"
    );
    if (routing.length > 0) {
      const transitModes = [
        ...routing[0].transit_modes,
        ...state.transitRouteTypeExtensions
      ];
      transitModes.forEach(t => {
        const typeNr = state.transitRouteTypes[t.type];
        obj[typeNr] = {
          name: t.type,
          color: t.color,
          icon: t.icon
        };
      });
    }
    return obj;
  },
  transitRouteTypesByName: (state, getters) => {
    const transitRouteTypesByNr = getters.transitRouteTypesByNr;
    let obj = {};
    Object.keys(transitRouteTypesByNr).forEach(nr => {
      const type = transitRouteTypesByNr[nr];
      console.log(type);
      obj[type.name] = {
        id: nr,
        color: type.color,
        icon: type.icon
      };
    });
    return obj;
  },
  getField
};

const actions = {};

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
