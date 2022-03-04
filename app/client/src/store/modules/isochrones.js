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
  selectedThematicData: null,
  // Cancel Request
  cancelReq: undefined
};

const getters = {
  colors: state => state.colors,
  type: state => state.type,
  isochroneLayer: state => state.isochroneLayer,
  selectedThematicData: state => state.selectedThematicData,
  calculations: state => state.calculations,
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
