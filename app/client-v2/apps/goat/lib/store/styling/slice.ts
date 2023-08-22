import { createSlice } from "@reduxjs/toolkit";

const stylingSlice = createSlice<any>({
  name: "styling",
  initialState: {
    initialViewState: {
      latitude: 48.1502132,
      longitude: 11.5696284,
      zoom: 10,
      min_zoom: 0,
      max_zoom: 20,
      bearing: 0,
      pitch: 0,
    },
  },
  reducers: {},
});

export const stylingReducer = stylingSlice.reducer;
