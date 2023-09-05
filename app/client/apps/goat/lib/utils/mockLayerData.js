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
      // "match",
      // ["get", "category"],
      // ["forest", "park"],
      // "hsl(137, 37%, 30%)",
      // "#000000",
      "fill-outline-color": "#000", // Define the color of the stroke
      "fill-opacity": 1.0, // Define the opacity of the fill
      // "fill-outline-opacity": 1.0, // Define the opacity of the stroke
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
      "line-color": [
        "interpolate",
        ["linear"],
        ["get", "class_id"],
        101,
        [
          "match",
          ["get", "class_id"],
          [101, 102, 108, 109],
          "hsl(0, 100%, 47%)",
          [110, 111, 112, 113, 114, 117, 118, 119],
          "hsl(0, 23%, 67%)",
          "#000000",
        ],
        401,
        [
          "match",
          ["get", "class_id"],
          [101, 102, 108, 109],
          "hsl(0, 100%, 47%)",
          [110, 111, 112, 113, 114, 117, 118, 119],
          "hsl(0, 23%, 67%)",
          [120, 122, 123, 124],
          "hsl(58, 100%, 71%)",
          "#000000",
        ],
        701,
        [
          "match",
          ["get", "class_id"],
          [101, 102, 108, 109],
          "hsl(0, 100%, 47%)",
          [110, 111, 112, 113, 114, 117, 118, 119],
          "hsl(0, 23%, 67%)",
          "#000000",
        ],
      ],
      "line-width": [
        "match",
        ["get", "class_id"],
        [101, 102, 108, 109, 110],
        3,
        [111, 112, 113, 114, 117, 118, 119],
        2,
        1,
      ],
    },
  },
};
