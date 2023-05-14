import type { Meta, StoryObj } from "@storybook/react";

import { Alert } from "../../components/Alert";
import { Text } from "../theme";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof Alert> = {
  component: Alert,
  tags: ["autodocs"],
  argTypes: {
    severity: {
      options: ["warning", "info", "error", "success"],
      control: { type: "radio" },
    },
    children: {
      control: false,
    },
    className: {
      control: false,
    },
    classes: {
      control: false,
    },
  },
  args: {
    severity: "info",
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
type Story = StoryObj<typeof Alert>;

export const Warning: Story = {
  args: {
    children: <Text typo="body 1">Alert message text</Text>,
    severity: "warning",
  },
};

export const Info: Story = {
  args: {
    ...Warning.args,
    severity: "info",
  },
};

export const Error: Story = {
  args: {
    ...Warning.args,
    severity: "error",
  },
};

export const Success: Story = {
  args: {
    ...Warning.args,
    severity: "success",
  },
};
