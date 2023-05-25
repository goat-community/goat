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
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6557-38545&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const ExtraSmall: Story = {
  args: {
    iconId: "help",
    size: "extra small",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6557-38545&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Small: Story = {
  args: {
    iconId: "help",
    size: "small",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6557-38545&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Medium: Story = {
  args: {
    iconId: "help",
    size: "medium",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6557-38545&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Large: Story = {
  args: {
    iconId: "help",
    size: "large",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6557-38545&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};
