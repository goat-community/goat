import { getField, updateField } from "vuex-map-fields";

const state = {
  pt_oev_gueteklasse: {
    config: {
      groups: {
        0: "B",
        1: "A",
        2: "A",
        3: "C",
        4: "B",
        5: "B",
        6: "B",
        7: "B",
        11: "B",
        12: "B"
      },
      time_frequency: [0, 4, 10, 19, 39, 60, 119],
      categories: [
        {
          A: 1,
          B: 1,
          C: 2
        },
        { A: 1, B: 2, C: 3 },
        { A: 2, B: 3, C: 4 },
        { A: 3, B: 4, C: 5 },
        { A: 4, B: 5, C: 6 },
        { A: 5, B: 6, C: 6 }
      ],
      classification: {
        1: { 300: "A", 500: "A", 750: "B", 1000: "C" },
        2: { 300: "A", 500: "B", 750: "C", 1000: "D" },
        3: { 300: "B", 500: "C", 750: "D", 1000: "E" },
        4: { 300: "C", 500: "D", 750: "E", 1000: "F" },
        5: { 300: "D", 500: "E", 750: "F" },
        6: { 300: "E", 500: "F" },
        7: { 300: "F" }
      }
    }
  }
};

const getters = {
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
