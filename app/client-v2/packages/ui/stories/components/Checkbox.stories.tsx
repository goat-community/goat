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
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6543-43052&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Secondary: Story = {
  args: {
    color: "secondary",
    defaultChecked: true,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6543-43052&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Error: Story = {
  args: {
    color: "error",
    defaultChecked: true,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6543-43052&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Info: Story = {
  args: {
    color: "info",
    defaultChecked: true,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6543-43052&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Success: Story = {
  args: {
    color: "success",
    defaultChecked: true,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6543-43052&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Warning: Story = {
  args: {
    color: "warning",
    defaultChecked: true,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6543-43052&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Default: Story = {
  args: {
    color: "default",
    defaultChecked: true,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6543-43052&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};
