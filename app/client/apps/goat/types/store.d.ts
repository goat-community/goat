export interface IStore {
  map: object;
  content: {
    folders: [];
    getFoldersStatus: string;
    previewMode: string;
  };
  styling: {
    initialViewState: {
      latitude: number;
      longitude: number;
      zoom: number;
      min_zoom: number;
      max_zoom: number;
      bearing: number;
      pitch: number;
    };
    tabValue: number;
  };
}
