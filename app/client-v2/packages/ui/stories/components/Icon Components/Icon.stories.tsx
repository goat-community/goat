import type { Meta, StoryObj } from "@storybook/react";

import { ThemeProvider } from "../../theme";
import { Icon } from "../../theme";

const meta: Meta<typeof Icon> = {
  component: Icon,
  tags: ["autodocs"],
  argTypes: {
    iconId: {
      options: ["help", "home", "coorperate", "powerOff", "rocketLaunch", "run", "bus", "file"],
      control: {
        type: "select",
      },
    },
    wrapped: {
      options: ["circle", "square"],
      control: {
        type: "select",
      },
    },
    className: {
      control: false,
    },
    size: {
      options: ["small", "default", "extra small", "medium", "large"],
      control: {
        type: "select",
      },
    },
    bgVariant: {
      options: ["focus", "secondary", "gray"],
      control: {
        type: "select",
      },
    },
    iconVariant: {
      options: ["white", "secondary", "focus"],
      control: {
        type: "select",
      },
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
type Story = StoryObj<typeof Icon>;

export const Default: Story = {
  args: {
    iconId: "help",
    size: "default",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6594-47648&t=m1TtlHDKRmJk5wCK-0",
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
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6594-47648&t=m1TtlHDKRmJk5wCK-0",
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
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6594-47648&t=m1TtlHDKRmJk5wCK-0",
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
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6594-47648&t=m1TtlHDKRmJk5wCK-0",
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
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6594-47648&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};
