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
          weight: 1
        },
        {
          name: "Primary school",
          value: "primary_school",
          icon: "primary_school",
          weight: 1
        },
        {
          name: "Secondary school",
          value: "secondary_school",
          icon: "secondary_school",
          weight: 1
        },
        {
          name: "Library",
          value: "library",
          icon: "library",
          weight: 1
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
          weight: 1
        },
        {
          name: "Biergarten",
          value: "biergarten",
          icon: "biergarten",
          weight: 1
        },
        {
          name: "Café",
          value: "cafe",
          icon: "cafe",
          weight: 1
        },
        {
          name: "Pub",
          value: "pub",
          icon: "pub",
          weight: 1
        },
        {
          name: "Fast food",
          value: "fast_food",
          icon: "fast_food",
          weight: 1
        },
        {
          name: "Ice cream",
          value: "ice_cream",
          icon: "ice_cream",
          weight: 1
        },
        {
          name: "Restaurant",
          value: "restaurant",
          icon: "restaurant",
          weight: 1
        },
        {
          name: "Night-Club",
          value: "nightclub",
          icon: "nightclub",
          weight: 1
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
          weight: 1
        },
        {
          name: "Car sharing",
          value: "car_sharing",
          icon: "car_sharing",
          weight: 1
        },
        {
          name: "Charging station",
          value: "charging_station",
          icon: "charging_station",
          weight: 1
        },
        {
          name: "Bus",
          value: "bus_stop",
          icon: "bus_stop",
          weight: 1
        },
        {
          name: "Tram Stop",
          value: "tram_stop",
          icon: "tram_stop",
          weight: 1
        },
        {
          name: "U-Bahn station",
          value: "subway_entrance",
          icon: "subway_entrance",
          weight: 1
        },
        {
          name: "Rail Station",
          value: "rail_station",
          icon: "rail_station",
          weight: 1
        },
        {
          name: "Taxi",
          value: "taxi",
          icon: "taxi",
          weight: 1
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
          weight: 1
        },
        {
          name: "ATM",
          value: "atm",
          icon: "atm",
          weight: 1
        },
        {
          name: "Bank",
          value: "bank",
          icon: "bank",
          weight: 1
        },
        {
          name: "Dentist",
          value: "dentist",
          icon: "dentist",
          weight: 1
        },
        {
          name: "Doctor",
          value: "doctors",
          icon: "doctors",
          weight: 1
        },
        {
          name: "Pharmacy",
          value: "pharmacy",
          icon: "pharmacy",
          weight: 1
        },
        {
          name: "Post box",
          value: "post_box",
          icon: "post_box",
          weight: 1
        },
        {
          name: "Fuel",
          value: "fuel",
          icon: "fuel",
          weight: 1
        },
        {
          name: "Recycling",
          value: "recycling",
          icon: "recycling",
          weight: 1
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
          weight: 1
        },
        {
          name: "Butcher",
          value: "butcher",
          icon: "butcher",
          weight: 1
        },
        {
          name: "Clothing store",
          value: "clothes",
          icon: "clothes",
          weight: 1
        },
        {
          name: "Convenience store",
          value: "convenience",
          icon: "convenience",
          weight: 1
        },
        {
          name: "Greengrocer",
          value: "greengrocer",
          icon: "greengrocer",
          weight: 1
        },
        {
          name: "Kiosk",
          value: "kiosk",
          icon: "kiosk",
          weight: 1
        },
        {
          name: "Mall",
          value: "mall",
          icon: "mall",
          weight: 1
        },
        {
          name: "Shoes",
          value: "shoes",
          icon: "shoes",
          weight: 1
        },
        {
          name: "Supermarket",
          value: "supermarket",
          icon: "supermarket",
          weight: 1
        },
        {
          name: "Discount Supermarket",
          value: "discount_supermarket",
          icon: "discount_supermarket",
          weight: 1
        },
        {
          name: "International Supermarket",
          value: "international_supermarket",
          icon: "international_supermarket",
          weight: 1
        },
        {
          name: "Hypermarket",
          value: "hypermarket",
          icon: "hypermarket",
          weight: 1
        },
        {
          name: "Chemist",
          value: "chemist",
          icon: "chemist",
          weight: 1
        },
        {
          name: "Organic Food",
          value: "organic",
          icon: "organic",
          weight: 1
        },
        {
          name: "Marketplace",
          value: "marketplace",
          icon: "marketplace",
          weight: 1
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
          weight: 1
        },
        {
          name: "Theatre",
          value: "theatre",
          icon: "theatre",
          weight: 1
        },
        {
          name: "Museum",
          value: "museum",
          icon: "museum",
          weight: 1
        },
        {
          name: "Hotel",
          value: "hotel",
          icon: "hotel",
          weight: 1
        },
        {
          name: "Hostel",
          value: "hostel",
          icon: "hostel",
          weight: 1
        },
        {
          name: "Guest house",
          value: "guest_house",
          icon: "guest_house",
          weight: 1
        },
        {
          name: "Gallery",
          value: "gallery",
          icon: "gallery",
          weight: 1
        }
      ]
    }
  ],
  selectedPois: []
};

const getters = {
  selectedPois: state => state.selectedPois,
  allPois: state => state.allPois
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
