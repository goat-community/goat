// For the built in plug in

export const dataBuiltInLayers = [
  {
    type: "wms",
    group: "external_imports",
    title: "Fahrradstatistik Stadtradeln",
    url:
      "https://geoportal.freiburg.de/wms/gdm_fahrrad_stat/gdm_fahrrad_stat?SERVICE=WMS&REQUEST=GetCapabilities",
    img:
      "https://geoportal.freiburg.de/wms/gdm_fahrrad_stat/gdm_fahrrad_stat?LAYERS=avs&VERSION=1.3.0&REQUEST=GetMap&SERVICE=WMS&CRS=EPSG:25832&BBOX=400000,5306000,421000,5325000&WIDTH=1050&HEIGHT=950&FORMAT=image/png&TRANSPARENT=FALSE"
  },
  {
    type: "wms",
    group: "external_imports",
    title: "Points of Interest Freiburg",
    url:
      "https://geoportal.freiburg.de/wms/gdm_poi/gdm_poi?SERVICE=WMS&REQUEST=GetCapabilities",
    img:
      "https://geoportal.freiburg.de/wms/gdm_poi/gdm_poi?LAYERS=gdm_poi&VERSION=1.3.0&REQUEST=GetMap&SERVICE=WMS&CRS=EPSG:25832&BBOX=400000,5306000,421000,5325000&WIDTH=1050&HEIGHT=950&FORMAT=image/png&TRANSPARENT=FALSE"
  }
];

// let newLayer = new TileLayer({
//   source: new TileWMS({
//     url: data.url,
//     params: {
//       layers: data.name
//     },
//     attribution: data.title
//   }),
//   group: "external_imports",
//   name: data.title,
//   visible: true,
//   opacity: 1,
//   type: "wmts"
// });
