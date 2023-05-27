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
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6543-36744&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Secondary: Story = {
  args: {
    ...Primary.args,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6543-36744&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};
