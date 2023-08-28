import type { Meta, StoryObj } from "@storybook/react";

import { TextField } from "../../../components/Inputs";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof TextField> = {
  component: TextField,
  tags: ["autodocs"],
  argTypes: {
    className: {
      control: false,
    },
  },
  args: {
    type: "text",
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
type Story = StoryObj<typeof TextField>;

export const Small: Story = {
  args: {
    // color: "primary",
    size: "small",
    label: "Small",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6570%3A46740&mode=dev",
    },
  },
};

export const Secondary: Story = {
  args: {
    // color: "textPrimary",
    size: "medium",
    label: "medium",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6570%3A46740&mode=dev",
    },
  },
};

export const InputWithSearch: Story = {
  args: {
    // color: "textPrimary",
    size: "small",
    iconId: "search",
    filled: true,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6570%3A46740&mode=dev",
    },
  },
};
