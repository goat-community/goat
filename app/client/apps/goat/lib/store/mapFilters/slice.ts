import { createSlice } from "@reduxjs/toolkit";
import type { EmptyObject, PayloadAction } from "@reduxjs/toolkit";
import type { Expression } from "@/types/map/filtering";

interface FilterState {
  filters: { [key: string]: string } | EmptyObject;
  logicalOperator: string;
  expressions: Expression[];
}

const initialState = {
  filters: {},
  logicalOperator: "",
  expressions: [],
} as FilterState;

const filterSlice = createSlice({
  name: "map-filters",
  initialState: initialState,
  reducers: {
    setLogicalOperator(state, action: PayloadAction<string>) {
      state.logicalOperator = action.payload;
    },
    setFilters(
      state,
      action: PayloadAction<{ [key: string]: string } | object>,
    ) {
      state.filters = action.payload;
    },
    addFilter(
      state,
      action: PayloadAction<{ query: string; expression: string }>,
    ) {
      state.filters[action.payload.expression] = action.payload.query;
    },
    removeFilter(state, action: PayloadAction<string>) {
      const filters = state.filters;
      console.log(filters, action.payload);
      delete filters[action.payload];
      console.log(filters);
      // state.filters = state.filters[action.payload]
    },
    addExpression(state, action: PayloadAction<Expression>) {
      const existingExpression = state.expressions.find(
        (expr) => expr.id === action.payload.id,
      );

      if (existingExpression) {
        state.expressions = state.expressions.map((expression) =>
          expression.id === action.payload.id ? action.payload : expression,
        );
      } else {
        state.expressions = [...state.expressions, action.payload];
      }
    },
    clearExpression(state) {
      state.expressions = [];
    },
    setExpression(state, action: PayloadAction<Expression[]>) {
      state.expressions = action.payload;
    },
    getExpressionById(state, action: PayloadAction<string>) {
      state.expressions.find((expr) => expr.id === action.payload);
    },
  },
});

export const {
  setLogicalOperator,
  setFilters,
  addFilter,
  addExpression,
  clearExpression,
  setExpression,
  removeFilter,
} = filterSlice.actions;

export const filtersReducer = filterSlice.reducer;
