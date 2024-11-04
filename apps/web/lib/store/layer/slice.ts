import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";

export interface LayerState {
  activeLayerId: number | null;
}

const initialState = {
  activeLayerId: -1,
} as LayerState;

const layerSlice = createSlice({
  name: "layer",
  initialState: initialState,
  reducers: {
    setActiveLayer: (state, action: PayloadAction<number | null>) => {
      if (action.payload === state.activeLayerId) {
        state.activeLayerId = null;
      } else {
        state.activeLayerId = action.payload;
      }
    },
  },
});

export const { setActiveLayer } = layerSlice.actions;

export const layerReducer = layerSlice.reducer;
