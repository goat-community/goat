import type { Meta, StoryObj } from "@storybook/react";

import { Switch } from "../../../components/Inputs";
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

export const SimpleSwitch: Story = {
  args: {},
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6570%3A46740&mode=dev",
    },
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6570%3A46740&mode=dev",
    },
  },
};

export const DefaultChecked: Story = {
  args: {
    defaultChecked: true,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6570%3A46740&mode=dev",
    },
  },
};
