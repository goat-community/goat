import type { Meta, StoryObj } from "@storybook/react";

import { ThemeProvider } from "../../theme";
import { IconButton } from "../../theme";

const meta: Meta<typeof IconButton> = {
  component: IconButton,
  tags: ["autodocs"],
  argTypes: {
    iconId: {
      options: ["help", "home"],
      control: { type: "radio" },
    },
    className: {
      control: false,
    },
    size: {
      options: ["extra small", "small", "medium", "large", "default"],
      control: {
        type: "select",
      },
    },
    iconClassName: {
      control: false,
    },
    disabled: {
      control: { type: "boolean" },
    },
    autoFocus: {
      control: { type: "boolean" },
    },
    tabIndex: {
      control: { type: "number" },
    },
    name: {
      control: { type: "text" },
    },
    id: {
      control: { type: "text" },
    },
  },
  args: {
    iconId: "help",
    size: "medium",
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
type Story = StoryObj<typeof IconButton>;

export const Default: Story = {
  args: {
    iconId: "help",
    size: "default",
  },
};

export const ExtraSmall: Story = {
  args: {
    iconId: "help",
    size: "extra small",
  },
};

export const Small: Story = {
  args: {
    iconId: "help",
    size: "small",
  },
};

export const Medium: Story = {
  args: {
    iconId: "help",
    size: "medium",
  },
};

export const Large: Story = {
  args: {
    iconId: "help",
    size: "large",
  },
};
