import { createSlice } from "@reduxjs/toolkit";
import type { PayloadAction } from "@reduxjs/toolkit";

export interface JobsState {
  runningJobIds: string[];
}

const initialState = {
  runningJobIds: [],
} as JobsState;

const jobsSlice = createSlice({
  name: "jobs",
  initialState: initialState,
  reducers: {
    setRunningJobIds: (state, action: PayloadAction<string[]>) => {
      state.runningJobIds = action.payload;
    },
  },
});

export const { setRunningJobIds } = jobsSlice.actions;

export const jobsReduces = jobsSlice.reducer;
