import type { Meta, StoryObj } from "@storybook/react/dist";

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
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6595-48211&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Info: Story = {
  args: {
    ...Warning.args,
    severity: "info",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6595-48211&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Error: Story = {
  args: {
    ...Warning.args,
    severity: "error",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6595-48211&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Success: Story = {
  args: {
    ...Warning.args,
    severity: "success",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6595-48211&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};
