import type { Meta, StoryObj } from "@storybook/react";

import { Checkbox } from "../../components/Checkbox";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof Checkbox> = {
  component: Checkbox,
  tags: ["autodocs"],
  argTypes: {
    color: {
      options: ["primary", "secondary", "error", "info", "success", "warning", "default"],
      control: { type: "radio" },
    },
    checked: {
      control: { type: "boolean" },
    },
    className: {
      control: false,
    },
  },
  args: {
    color: "info",
    defaultChecked: true,
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
type Story = StoryObj<typeof Checkbox>;

export const Primary: Story = {
  args: {
    color: "primary",
    defaultChecked: true,
  },
};

export const Secondary: Story = {
  args: {
    color: "secondary",
    defaultChecked: true,
  },
};

export const Error: Story = {
  args: {
    color: "error",
    defaultChecked: true,
  },
};

export const Info: Story = {
  args: {
    color: "info",
    defaultChecked: true,
  },
};

export const Success: Story = {
  args: {
    color: "success",
    defaultChecked: true,
  },
};

export const Warning: Story = {
  args: {
    color: "warning",
    defaultChecked: true,
  },
};

export const Default: Story = {
  args: {
    color: "default",
    defaultChecked: true,
  },
};
