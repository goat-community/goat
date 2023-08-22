import { contentReducer } from "@/lib/store/content/slice";
import { mapReducer } from "@/lib/store/map/slice";
import { stylingReducer } from "@/lib/store/styling/slice";
import { configureStore } from "@reduxjs/toolkit";

const store = configureStore({
  reducer: {
    map: mapReducer,
    content: contentReducer,
    styling: stylingReducer,
  },
});

export default store;
