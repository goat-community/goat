import { getFolders } from "@/lib/store/content/actions";
import { LOADING_STATUSES } from "@/lib/utils/constants";
import { createSlice } from "@reduxjs/toolkit";

const contentSlice = createSlice<any>({
  name: "map",
  initialState: {
    folder: [],
    getFoldersStatus: LOADING_STATUSES.idle,
  },
  reducers: {},

  extraReducers: ({ addCase }) => {
    // get folders
    addCase(getFolders.pending, (state) => {
      state.getFoldersStatus = LOADING_STATUSES.pending;
    });
    addCase(getFolders.fulfilled, (state, { payload }) => {
      console.log("getFolders succeeded", payload);
      state.getFoldersStatus = LOADING_STATUSES.succeeded;
    });
    addCase(getFolders.rejected, (state, { payload }) => {
      console.log("getFolders failed", payload);
      state.getFoldersStatus = LOADING_STATUSES.failed;
    });
  },
});

export const contentReducer = contentSlice.reducer;
