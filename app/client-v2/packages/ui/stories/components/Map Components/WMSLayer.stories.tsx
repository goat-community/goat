import type { Meta, StoryObj } from "@storybook/react";

import WMSLayer from "../../../components/WMSLayer";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof WMSLayer> = {
  component: WMSLayer,
  argTypes: {},
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof WMSLayer>;

export const WMSMapLayer: Story = {};
