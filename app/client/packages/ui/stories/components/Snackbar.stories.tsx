import type { Meta, StoryObj } from "@storybook/react/dist";

import BasicSnackbar from "../../components/BasicSnackbar";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof BasicSnackbar> = {
  component: BasicSnackbar,
  tags: ["autodocs"],
  argTypes: {
    severity: {
      options: ["warning", "info", "error", "success"],
      control: { type: "radio" },
    },
    hideDuration: {
      control: false,
    },
    open: {
      control: false,
    },
    anchorOrigin: {
      control: { type: "object" },
    },
  },
  args: {
    severity: "info",
    message: "Info",
    open: true,
    anchorOrigin: {
      vertical: "top",
      horizontal: "left",
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
type Story = StoryObj<typeof BasicSnackbar>;

export const Warning: Story = {
  args: {
    severity: "warning",
    message: "Warning",
  },
};

export const Info: Story = {
  args: {
    severity: "info",
    message: "Info",
  },
  parameters: {
    design: {},
  },
};

export const Error: Story = {
  args: {
    severity: "error",
    message: "Error",
  },
  parameters: {
    design: {},
  },
};

export const Success: Story = {
  args: {
    severity: "success",
    message: "Success",
  },
  parameters: {
    design: {},
  },
};
