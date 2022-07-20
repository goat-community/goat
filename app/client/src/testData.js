export const dataBuiltInLayers = [
  {
    layers: [
      {
        name: "Voyager",
        type: "tile",
        group: "basemap",
        title: "Voyager",
        url:
          "https://api.maptiler.com/maps/voyager/{z}/{x}/{y}.png?key=5SLMZCpBxmxow9QFVy7M",
        img:
          "https://snazzy-maps-cdn.azureedge.net/assets/102-clean-grey.png?v=20170626083301",
        attribution: `<a href="https://carto.com/" target="_blank">&copy; CARTO</a> <a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>`
      },
      {
        name: "Topographique",
        type: "tile",
        group: "basemap",
        title: "Topographique",
        url:
          "https://api.maptiler.com/maps/topographique/{z}/{x}/{y}.png?key=5SLMZCpBxmxow9QFVy7M",
        img:
          "https://www.worldatlas.com/r/w1200/upload/f4/9a/b2/shutterstock-214460839.jpg",
        attribution: `<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>`
      }
    ]
  },
  {
    layers: [
      {
        name: "DPD Stores ",
        type: "vectortile",
        group: "additional_data",
        format: "geojson",
        title: "DPD Stores ",
        url:
          "https://api.maptiler.com/data/6838bc4e-7a17-41af-a594-6e8d43fb05c5/features.json?key=5SLMZCpBxmxow9QFVy7M",
        img:
          "https://corpassets.what3words.com/wp-content/uploads/2022/02/UK_DPD_Delivery_Courier_hero.jpg",
        attribution: `Rexha Company 2022`
      },
      {
        name: "Munich Info ",
        type: "vectortile",
        format: "geojson",
        group: "additional_data",
        title: "Munich Info",
        url:
          "https://api.maptiler.com/data/4d0102c0-67d7-4fdc-b1d8-9cdd76026380/features.json?key=5SLMZCpBxmxow9QFVy7M",
        img:
          "https://map.viamichelin.com/map/carte?map=viamichelin&z=10&lat=48.13912&lon=11.58022&width=550&height=382&format=png&version=latest&layer=background&debug_pattern=.*",
        attribution: `None 2022`
      }
    ]
  },
  { layers: [] },
  { layers: [] }
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
