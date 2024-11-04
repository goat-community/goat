import { createSelector } from "@reduxjs/toolkit";

const selectBasemaps = (state) => state.map.basemaps;
const selectActiveBasemapValue = (state) => state.map.activeBasemap;

export const selectActiveBasemap = createSelector(
  [selectBasemaps, selectActiveBasemapValue],
  (basemaps, activeBasemapValue) => {
    return basemaps.find((basemap) => basemap.value === activeBasemapValue);
  }
);
