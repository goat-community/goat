const state = {
  allPois: [
    {
      name: "Education",
      id: 1,
      children: [
        {
          name: "Kindergarten",
          value: "kindergarten",
          icon: "kindergarten",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Primary school",
          value: "primary_school",
          icon: "primary_school",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Secondary school",
          value: "secondary_school",
          icon: "secondary_school",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Library",
          value: "library",
          icon: "library",
          weight: 1,
          sensitivity: -0.003
        }
      ]
    },
    {
      name: "Food and Drink",
      children: [
        {
          name: "Bar",
          value: "bar",
          icon: "bar",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Biergarten",
          value: "biergarten",
          icon: "biergarten",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Café",
          value: "cafe",
          icon: "cafe",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Pub",
          value: "pub",
          icon: "pub",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Fast food",
          value: "fast_food",
          icon: "fast_food",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Ice cream",
          value: "ice_cream",
          icon: "ice_cream",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Restaurant",
          value: "restaurant",
          icon: "restaurant",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Night-Club",
          value: "nightclub",
          icon: "nightclub",
          weight: 1,
          sensitivity: -0.003
        }
      ]
    },
    {
      name: "Transport",
      children: [
        {
          name: "Bicycle rental",
          value: "bicycle_rental",
          icon: "bicycle_rental",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Car sharing",
          value: "car_sharing",
          icon: "car_sharing",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Charging station",
          value: "charging_station",
          icon: "charging_station",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Bus",
          value: "bus_stop",
          icon: "bus_stop",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Tram Stop",
          value: "tram_stop",
          icon: "tram_stop",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "U-Bahn station",
          value: "subway_entrance",
          icon: "subway_entrance",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Rail Station",
          value: "rail_station",
          icon: "rail_station",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Taxi",
          value: "taxi",
          icon: "taxi",
          weight: 1,
          sensitivity: -0.003
        }
      ]
    },
    {
      name: "Services",
      children: [
        {
          name: "Hairdresser",
          value: "hairdresser",
          icon: "hairdresser",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "ATM",
          value: "atm",
          icon: "atm",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Bank",
          value: "bank",
          icon: "bank",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Dentist",
          value: "dentist",
          icon: "dentist",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Doctor",
          value: "doctors",
          icon: "doctors",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Pharmacy",
          value: "pharmacy",
          icon: "pharmacy",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Post box",
          value: "post_box",
          icon: "post_box",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Fuel",
          value: "fuel",
          icon: "fuel",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Recycling",
          value: "recycling",
          icon: "recycling",
          weight: 1,
          sensitivity: -0.003
        }
      ]
    },
    {
      name: "Shop",
      children: [
        {
          name: "Bakery",
          value: "bakery",
          icon: "bakery",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Butcher",
          value: "butcher",
          icon: "butcher",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Clothing store",
          value: "clothes",
          icon: "clothes",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Convenience store",
          value: "convenience",
          icon: "convenience",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Greengrocer",
          value: "greengrocer",
          icon: "greengrocer",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Kiosk",
          value: "kiosk",
          icon: "kiosk",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Mall",
          value: "mall",
          icon: "mall",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Shoes",
          value: "shoes",
          icon: "shoes",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Supermarket",
          value: "supermarket",
          icon: "supermarket",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Discount Supermarket",
          value: "discount_supermarket",
          icon: "discount_supermarket",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "International Supermarket",
          value: "international_supermarket",
          icon: "international_supermarket",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Hypermarket",
          value: "hypermarket",
          icon: "hypermarket",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Chemist",
          value: "chemist",
          icon: "chemist",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Organic Food",
          value: "organic",
          icon: "organic",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Marketplace",
          value: "marketplace",
          icon: "marketplace",
          weight: 1,
          sensitivity: -0.003
        }
      ]
    },
    {
      name: "Tourism & Leisure",
      children: [
        {
          name: "Cinema",
          value: "cinema",
          icon: "cinema",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Theatre",
          value: "theatre",
          icon: "theatre",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Museum",
          value: "museum",
          icon: "museum",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Hotel",
          value: "hotel",
          icon: "hotel",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Hostel",
          value: "hostel",
          icon: "hostel",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Guest house",
          value: "guest_house",
          icon: "guest_house",
          weight: 1,
          sensitivity: -0.003
        },
        {
          name: "Gallery",
          value: "gallery",
          icon: "gallery",
          weight: 1,
          sensitivity: -0.003
        }
      ]
    }
  ],
  selectedPois: [],
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
    900
  ]
};

const getters = {
  selectedPois: state => state.selectedPois,
  allPois: state => state.allPois,
  dynamicHeatmapTravelTimes: state => state.dynamicHeatmapTravelTimes
};

const actions = {
  updateSelectedPois({ commit, rootState }, selectedPois) {
    commit("UPDATE_SELECTED_POIS", selectedPois);
    if (rootState.isochrones.selectedThematicData) {
      rootState.isochrones.selectedThematicData.filterSelectedPois = selectedPois;
    }
  }
};

const mutations = {
  UPDATE_SELECTED_POIS(state, selectedPois) {
    state.selectedPois = selectedPois;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
