/**
 *
 * Create a rectangular grid heatmap from a set of travel times.
 */

export function isochroneHeatmap({ cutoff, height, width, surface, project }) {
  console.log(cutoff, height, width, surface, project);
  // loop through the surface and create a heatmap
  const cWidth = width - 1;
  const geojson = {
    type: "FeatureCollection",
    features: []
  };
  for (let origy = 0; origy < height - 1; origy++) {
    for (let origx = 0; origx < width - 1; origx++) {
      const index = origy * cWidth + origx;
      const pos_pixel_cell = [origx, origy];
      // top left
      const pos_cell_tl = project(pos_pixel_cell);
      // top right
      const pos_cell_tr = project([origx + 1, origy]);
      // bottom left
      const pos_cell_bl = project([origx, origy + 1]);
      // bottom right
      const pos_cell_br = project([origx + 1, origy + 1]);
      const feature = {
        type: "Feature",
        properties: {
          cost: surface[index]
        },
        geometry: {
          type: "Polygon",
          coordinates: [
            [pos_cell_tl, pos_cell_tr, pos_cell_br, pos_cell_bl, pos_cell_tl]
          ]
        }
        // 5- Add the travel time to the grid cell
      };
      geojson.features.push(feature);
    }
  }
  return geojson;
}
