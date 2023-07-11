import { createSlice } from "@reduxjs/toolkit";

import { LOADING_STATUSES } from "../../utils/constants";
import { getMapData } from "./actions";

const mapSlice = createSlice<any>({
  name: "map",
  initialState: {
    test: false,
    getMapDataStatus: LOADING_STATUSES.idle,
  },
  reducers: {},
  extraReducers: ({ addCase }) => {
    addCase(getMapData.pending, (state) => {
      console.log("state", state);
    });
    addCase(getMapData.fulfilled, (state, { payload }) => {
      console.log("state", state);
      console.log("payload", payload);
    });
    addCase(getMapData.rejected, (state) => {
      console.log("state", state);
    });
  },
});

export const mapReducer = mapSlice.reducer;
