import { contentReducer } from "@/lib/store/content/slice";
import { configureStore } from "@reduxjs/toolkit";

import { mapReducer } from "./map/slice";

const store = configureStore({
  reducer: {
    map: mapReducer,
    content: contentReducer,
  },
});

export default store;
