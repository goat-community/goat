import { createSlice } from "@reduxjs/toolkit";
import type { EmptyObject, PayloadAction } from "@reduxjs/toolkit";

interface FilterState {
  filters: {[key: string]: string} | EmptyObject;
  logicalOperator: string;
}

const initialState = {
  filters: {},
  logicalOperator: "",
} as FilterState;

const filterSlice = createSlice({
  name: "map-filters",
  initialState: initialState,
  reducers: {
    setLogicalOperator(state, action: PayloadAction<string>) {
      state.logicalOperator = action.payload;
    },
    setFilters(state, action: PayloadAction<{[key: string]: string} | object>) {
      state.filters = action.payload;
    },
    addFilter(state, action: PayloadAction<{query: string, expression: string}>) {
      state.filters[action.payload.expression] = action.payload.query;
    },
  },
});

export const { setLogicalOperator, setFilters, addFilter } = filterSlice.actions;

export const filtersReducer = filterSlice.reducer;
