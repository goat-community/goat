import type { TLayer } from '@/lib/store/styling/slice'
import { stylesObj } from "@/lib/utils/mockLayerData";
import { createAsyncThunk } from "@reduxjs/toolkit";

export const layerDataFetcher = (id: string) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(stylesObj[id]);
    }, 1000); // Simulate a 1-second delay
  });
};

export const fetchLayerData = createAsyncThunk(
  "styling/fetchLayerData",
  async (id: string) => {
    try {
      return await layerDataFetcher(id) as TLayer;
    } catch (error) {
      throw error;
    }
  },
);
