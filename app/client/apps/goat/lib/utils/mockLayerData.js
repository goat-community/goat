export const stylesObj = {
  poi: {
    name: "poi",
    sources: {
      composite: {
        url: "mapbox://eliaspajares.cljxyaynj02532aqi9rh1kz0g-77qff",
        type: "vector",
      },
    },
    id: "cljxz3bl1003v01qy7k5m0apj",
    type: "symbol",
    paint: {},
    source: "composite",
    "source-layer": "poi",
    layout: {
      "icon-image": [
        "match",
        ["get", "category"],
        ["dentist"],
        "dentist-15",
        ["bakery"],
        "bakery-11",
        ["nursery"],
        "hospital-15",
        "",
      ],
    },
  },
  aoi: {
    name: "aoi",
    sources: {
      composite: {
        url: "mapbox://eliaspajares.cljxc2rek01ow2alyl0cy0y2j-63c9z",
        type: "vector",
      },
    },
    id: "cljyel7yl005r01pfcd4h0epj",
    type: "fill",
    paint: {
      "fill-color": "#316940",
      "fill-outline-color": "#000",
      "fill-opacity": 1.0,
      "fill-antialias": true, //
    },
    layout: {},
    source: "composite",
    "source-layer": "aoi",
  },
  edge: {
    name: "edge",
    sources: {
      composite: {
        url: "mapbox://eliaspajares.cljxyjs6x02672oqimtbmde3u-92yjl",
        type: "vector",
      },
    },
    id: "cljxzoemb003y01qr59fx3mpq",
    type: "line",
    layout: {},
    source: "composite",
    "source-layer": "edge",
    paint: {
      "line-color": "#ff003b",
      "line-width": 3,
    },
  },
};
