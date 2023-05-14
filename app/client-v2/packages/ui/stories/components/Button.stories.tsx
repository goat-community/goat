import type { Meta, StoryObj } from "@storybook/react";

import { ThemeProvider } from "../theme";
import { Button } from "../theme";

const meta: Meta<typeof Button> = {
  component: Button,
  tags: ["autodocs"],
  argTypes: {
    variant: {
      options: ["primary", "secondary", "ternary"],
      control: { type: "radio" },
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
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    children: "Button",
  },
};

export const Secondary: Story = {
  args: {
    ...Primary.args,
  },
};
