import type { Meta, StoryObj } from "@storybook/react";

import MapL from "../../../map";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof MapL> = {
  component: MapL,
  argTypes: {},
  parameters: {
    controls: {
      exclude: /.*/g,
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
type Story = StoryObj<typeof MapL>;

export const WMSMapLayer: Story = {
  args: { layer: "wms" },
};
