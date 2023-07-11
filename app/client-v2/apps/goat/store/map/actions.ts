import { createAsyncThunk } from "@reduxjs/toolkit";

import { mapApi } from "./api";

export const getMapData = createAsyncThunk("map/getMapData", async (_, { rejectWithValue }) => {
  try {
    const response = await mapApi.getMap();
    return response.data;
  } catch (err) {
    return rejectWithValue(err);
  }
});
