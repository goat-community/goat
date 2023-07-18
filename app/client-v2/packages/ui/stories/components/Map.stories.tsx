import type { Meta, StoryObj } from "@storybook/react";

import MapByLayer from "../../components/MapByLayer";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof MapByLayer> = {
  component: MapByLayer,
  tags: ["autodocs"],
  argTypes: {
    layer: {
      options: ["aoi", "poi", "edge"],
      control: false,
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

export const Polygon: Story = {
  args: { layer: "aoi" },
  parameters: {},
};

export const VectorTilePoint: Story = {
  args: { layer: "poi" },
  parameters: {},
};

export const Line: Story = {
  args: { layer: "edge" },
  parameters: {},
};
