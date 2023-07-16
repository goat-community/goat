import { configureStore } from "@reduxjs/toolkit";

import { mapReducer } from "./map/slice";

const store = configureStore({
  reducer: {
    mapReducer,
  },
});

export default store;
