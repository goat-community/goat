import { contentApi } from "@/lib/store/content/api";
import { createAsyncThunk } from "@reduxjs/toolkit";

export const getFolders = createAsyncThunk("content/getFolders", async (_, { rejectWithValue }) => {
  try {
    const response = await contentApi.getFolders();

    return response.data;
  } catch (err) {
    return rejectWithValue(err);
  }
});
