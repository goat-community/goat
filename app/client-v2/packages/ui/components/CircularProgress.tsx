import type { Meta, StoryObj } from "@storybook/react";

import { CircularProgress } from "../../components/CircularProgress";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof CircularProgress> = {
  component: CircularProgress,
  tags: ["autodocs"],
  argTypes: {
    color: {
      options: ["primary", "textPrimary"],
      control: { type: "radio" },
    },
    className: {
      control: false,
    },
    size: { control: { type: "number" } },
  },
  args: {
    color: "primary",
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
type Story = StoryObj<typeof CircularProgress>;

export const Primary: Story = {
  args: {
    color: "primary",
  },
};

export const Secondary: Story = {
  args: {
    color: "textPrimary",
  },
};

export const CustomSize: Story = {
  args: {
    color: "primary",
    size: 20,
  },
};
