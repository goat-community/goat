import type { Meta, StoryObj } from "@storybook/react";

import Switch from "../../../components/Inputs/Switch";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof Switch> = {
  component: Switch,
  tags: ["autodocs"],
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
type Story = StoryObj<typeof Switch>;

export const Small: Story = {
  args: {},
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6570%3A46740&mode=dev",
    },
  },
};
