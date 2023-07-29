import type { Meta, StoryObj } from "@storybook/react";

import MapByLayer from "../../../components/MapByLayer";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof MapByLayer> = {
  component: MapByLayer,
  argTypes: {
    layer: {
      options: ["Vector tile Point", "Polygon", "Line", "XYZ"],
      control: { type: "radio" },
      mapping: {
        "Vector tile Point": "poi",
        Polygon: "aoi",
        Line: "edge",
        XYZ: "xyz",
      },
    },
  },
  parameters: {
    docs: {
      description: {
        component: "",
      },
    },
  },
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof MapByLayer>;

export const MapLayer: Story = {
  args: { layer: "poi" },
  parameters: {},
};
