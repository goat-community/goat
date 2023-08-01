import type { Meta, StoryObj } from "@storybook/react";

import XYZLayer from "../../../components/XYZLayer";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof XYZLayer> = {
  component: XYZLayer,
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
type Story = StoryObj<typeof XYZLayer>;

export const XYZMapLayer: Story = {};
