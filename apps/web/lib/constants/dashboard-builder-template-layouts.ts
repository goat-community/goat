export const basicLayout = {
  settings: {
    basemap: true,
    measure: false,
    toolbar: true,
    location: true,
    scalebar: true,
    fullscreen: true,
    zoom_controls: true,
    find_my_location: false,
  },
  interface: [
    {
      id: "panel-1743756324718",
      type: "panel",
      config: {
        options: { style: "default" },
        position: { spacing: 0, alignItems: "start" },
        appearance: { shadow: 5, opacity: 0.7, backgroundBlur: 15 },
      },
      widgets: [
        {
          id: "widget-173979401723482234234234",
          type: "widget",
          config: {
            type: "layers",
            setup: { title: "Layers" },
            options: { show_search: true, open_legend_by_default: true },
          },
        },
      ],
      position: "left",
    },
  ],
};
