import { contentReducer } from "@/lib/store/content/slice";
import { stylingReducer } from "@/lib/store/styling/slice";
import { configureStore } from "@reduxjs/toolkit";

const store = configureStore({
  reducer: {
    content: contentReducer,
    styling: stylingReducer,
  },
});

export default store;
