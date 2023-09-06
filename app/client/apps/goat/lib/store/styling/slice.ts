import type { PayloadAction } from "@reduxjs/toolkit";
import { createSlice } from "@reduxjs/toolkit";
import { fetchLayerData } from "@/lib/store/styling/actions";

interface IViewState {
  latitude: number;
  longitude: number;
  zoom: number;
  min_zoom: number;
  max_zoom: number;
  bearing: number;
  pitch: number;
}

interface IBasemap {
  value: string;
  url: string;
  title: string;
  subtitle: string;
  thumbnail: string;
}

interface IMarker {
  id: string;
  lat: number;
  long: number;
  iconName: string;
}

interface IMapLayer {
  name: string;
  sources: {
    composite: {
      url: string;
      type: string;
    };
  };
  id: string;
  type:
    | "symbol"
    | "fill"
    | "line"
    | "circle"
    | "background"
    | "raster"
    | "fill-extrusion"
    | "heatmap"
    | "hillshade";
  paint: object;
  layout: object;
  source: string;
  "source-layer": string;
}

export interface IStylingState {
  initialViewState: IViewState;
  tabValue: number;
  basemaps: IBasemap[];
  activeBasemapIndex: number[];
  markers: IMarker[];
  mapLayer: IMapLayer | null;
}

const initialState: IStylingState = {
  initialViewState: {
    latitude: 48.13780235991851,
    longitude: 11.575936741828286,
    zoom: 11,
    min_zoom: 0,
    max_zoom: 20,
    bearing: 0,
    pitch: 0,
  },
  tabValue: 0,
  basemaps: [
    {
      value: "mapbox_streets",
      url: "mapbox://styles/mapbox/streets-v12",
      title: "High Fidelity",
      subtitle: "Great for public presentations",
      thumbnail: "https://i.imgur.com/aVDMUKAm.png",
    },
    {
      value: "mapbox_satellite",
      url: "mapbox://styles/mapbox/satellite-streets-v12",
      title: "Satellite Streets",
      subtitle: "As seen from space",
      thumbnail: "https://i.imgur.com/JoMGuUOm.png",
    },
    {
      value: "mapbox_light",
      url: "mapbox://styles/mapbox/light-v11",
      title: "Light",
      subtitle: "For highlitghting data overlays",
      thumbnail: "https://i.imgur.com/jHFGEEQm.png",
    },
    {
      value: "mapbox_dark",
      url: "mapbox://styles/mapbox/dark-v11",
      title: "Dark",
      subtitle: "For highlighting data overlays",
      thumbnail: "https://i.imgur.com/PaYV5Gjm.png",
    },
    {
      value: "mapbox_navigation",
      url: "mapbox://styles/mapbox/navigation-day-v1",
      title: "Traffic",
      subtitle: "Live traffic data",
      thumbnail: "https://i.imgur.com/lfcARxZm.png",
    },
  ],
  activeBasemapIndex: [4],
  markers: [],
  //todo need get layer from db
  mapLayer: null,
};

const stylingSlice = createSlice({
  name: "styling",
  initialState,
  reducers: {
    setTabValue: (state, action: PayloadAction<number>) => {
      state.tabValue = action.payload;
    },
    setActiveBasemapIndex: (state, action: PayloadAction<number[]>) => {
      state.activeBasemapIndex = action.payload;
    },
    addMarker: (state, action: PayloadAction<IMarker>) => {
      state.markers.push(action.payload);
    },
    editeMarkerPosition: (state, action: PayloadAction<IMarker>) => {
      state.markers = state.markers.map((item) => {
        if (item.id === action.payload.id) {
          return action.payload;
        }
        return item;
      });
    },
    resetStyles: (state): void => {
      state.markers = [];
    },
    saveStyles: (state): void => {
      const jsonData = JSON.stringify(state, null, 2); // Convert state to JSON with pretty formatting
      console.log("Saved jsonData", jsonData);

      // const blob = new Blob([jsonData], { type: 'application/json' });
      // Need Using the FileSaver library to save the JSON data as a file
      // saveAs(blob, 'map_styles.json');
    },
    setLayerFillColor: (state, action: PayloadAction<string>) => {
      if (state.mapLayer?.paint) {
        state.mapLayer.paint["fill-color"] = action.payload;
      }
    },
    setLayerFillOutLineColor: (state, action: PayloadAction<string>) => {
      if (state.mapLayer?.paint) {
        state.mapLayer.paint["fill-outline-color"] = action.payload;
      }
    },
    deleteLayerFillOutLineColor: (state) => {
      if (state.mapLayer?.paint) {
        if ("fill-outline-color" in state.mapLayer.paint) {
          delete state.mapLayer.paint["fill-outline-color"];
        }
      }
    },
    // setLayerIconImage: (state, action: PayloadAction<string>) => {
    //   state.mapLayer.layers[0].layout["icon-image"] = action.payload;
    // },
    // setLayerIconSize: (state, action: PayloadAction<number>) => {
    //   state.mapLayer.layers[0].layout["icon-size"] = action.payload;
    // },
  },
  extraReducers: (builder) => {
    builder.addCase(fetchLayerData.pending, (state) => {
      state.mapLayer = null;
    });
    builder.addCase(fetchLayerData.fulfilled, (state, { payload }) => {
      state.mapLayer = payload as IMapLayer;
    });
    builder.addCase(fetchLayerData.rejected, (state) => {
      state.mapLayer = null;
    });
  },
});

export const {
  setTabValue,
  setActiveBasemapIndex,
  addMarker,
  resetStyles,
  setLayerFillColor,
  setLayerFillOutLineColor,
  saveStyles,
  deleteLayerFillOutLineColor,
} = stylingSlice.actions;

export const stylingReducer = stylingSlice.reducer;
