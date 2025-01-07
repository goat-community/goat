import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";

import type { ProjectLayer } from "@/lib/validations/project";

export interface LayerState {
  activeLayerId: number | null;
  projectLayers: ProjectLayer[];
}

const initialState = {
  activeLayerId: -1,
  projectLayers: [],
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
    setProjectLayers: (state, action: PayloadAction<ProjectLayer[]>) => {
      state.projectLayers = action.payload;
    },
    updateProjectLayer: (state, action: PayloadAction<{ id: number; changes: Partial<ProjectLayer> }>) => {
      const { id, changes } = action.payload;
      state.projectLayers = state.projectLayers.map((layer) =>
        layer.id === id ? { ...layer, ...changes } : layer
      );
    },
    addProjectLayer: (state, action: PayloadAction<ProjectLayer>) => {
      state.projectLayers.push(action.payload);
    },
    removeProjectLayer: (state, action: PayloadAction<number>) => {
      state.projectLayers = state.projectLayers.filter((layer) => layer.id !== action.payload);
    },
  },
});

export const { setActiveLayer, setProjectLayers, updateProjectLayer, addProjectLayer, removeProjectLayer } =
  layerSlice.actions;

export const layerReducer = layerSlice.reducer;
