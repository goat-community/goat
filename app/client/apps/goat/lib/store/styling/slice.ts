import type { PayloadAction } from "@reduxjs/toolkit";
import { createSlice } from "@reduxjs/toolkit";

type ViewState = {
  latitude: number;
  longitude: number;
  zoom: number;
  min_zoom: number;
  max_zoom: number;
  bearing: number;
  pitch: number;
};

type StylingState = {
  initialViewState: ViewState;
  tabValue: number;
};

const initialState: StylingState = {
  initialViewState: {
    latitude: 48.1502132,
    longitude: 11.5696284,
    zoom: 10,
    min_zoom: 0,
    max_zoom: 20,
    bearing: 0,
    pitch: 0,
  },
  tabValue: 0,
};

const stylingSlice = createSlice({
  name: "styling",
  initialState,
  reducers: {
    setTabValue: (state, action: PayloadAction<number>) => {
      state.tabValue = action.payload;
    },
  },
});

export const { setTabValue } = stylingSlice.actions;
export const stylingReducer = stylingSlice.reducer;
