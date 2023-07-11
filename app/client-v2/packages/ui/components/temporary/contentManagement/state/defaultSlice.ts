import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";

export interface DefaultState {
  value: number;
  currentPath: string[];
}

const initialState: DefaultState = {
  value: 0,
  currentPath: ["Home"],
};

export const defaultSlice = createSlice({
  name: "default",
  initialState,
  reducers: {
    changePath: (state, action: PayloadAction<string[]>) => {
      state.currentPath = action.payload;
    },
    pathGoBack: (state) => {
      if (state.currentPath.length > 1) {
        state.currentPath.pop();
      }
    },
    pathEnter: (state, action: PayloadAction<string>) => {
      state.currentPath.push(action.payload);
    },
  },
});

// Action creators are generated for each case reducer function
export const { changePath, pathGoBack, pathEnter } = defaultSlice.actions;

export default defaultSlice.reducer;
