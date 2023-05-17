import type { Meta, StoryObj } from "@storybook/react";

import { TextField } from "../../components/TextField";
import { ThemeProvider } from "../theme";

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

export const Primary: Story = {
  args: {
    // color: "primary",
  },
};

export const Secondary: Story = {
  args: {
    // color: "textPrimary",
  },
};
