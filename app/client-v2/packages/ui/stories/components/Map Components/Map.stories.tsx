import type { Meta, StoryObj } from "@storybook/react";

import Map from "../../../components/BasicMap";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof Map> = {
  component: Map,
  argTypes: {
    MAP_ACCESS_TOKEN: {
      control: { type: "text" },
    },
    initialViewState: {
      control: { type: "object" },
    },
    mapStyle: {
      control: { type: "text" },
    },
    scaleShow: {
      control: { type: "boolean" },
    },
    navigationControl: {
      control: { type: "boolean" },
    },
  },
  parameters: {},
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof Map>;

export const BasicMap: Story = {
  args: {
    initialViewState: {
      longitude: 11.831704345197693,
      latitude: 48.124458667004006,
      zoom: 10,
      pitch: 0,
      bearing: 0,
      altitude: -1,
    },
    MAP_ACCESS_TOKEN:
      "pk.eyJ1IjoiZWxpYXNwYWphcmVzIiwiYSI6ImNqOW1scnVyOTRxcWwzMm5yYWhta2N2cXcifQ.aDCgidtC9cjf_O75frn9lA",
    mapStyle: "mapbox://styles/mapbox/streets-v11",
    scaleShow: false,
    navigationControl: false,
  },
  parameters: {},
};
