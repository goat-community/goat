import type { Meta, StoryObj } from "@storybook/react";

import { ThemeProvider } from "../../theme";
import { Text } from "../../theme";

const meta: Meta<typeof Text> = {
  component: Text,
  tags: ["autodocs"],
  argTypes: {
    className: {
      control: false,
    },
    typo: {
      options: [
        "display heading",
        "page heading",
        "subtitle",
        "section heading",
        "object heading",
        "label 1",
        "label 2",
        "navigation label",
        "body 1",
        "body 2",
        "body 3",
        "caption",
      ],
      control: {
        type: "select",
      },
    },
    color: {
      options: ["primary", "secondary", "disabled", "focus"],
      control: {
        type: "select",
      },
    },
    children: {
      control: false,
    },
    htmlComponent: {
      options: ["h1", "h2", "h3", "h4", "h5", "h6", "p", "span", "div", "a"],
      control: {
        type: "select",
      },
    },
    componentProps: {
      control: false,
    },
    fixedSize_enabled: {
      control: { type: "boolean" },
    },
    fixedSize_content: {
      control: { type: "text" },
    },
    fixedSize_fontWeight: {
      control: { type: "number" },
    },
  },
  args: {
    typo: "subtitle",
    children: "Hello World",
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
type Story = StoryObj<typeof Text>;

export const DisplayHeading: Story = {
  args: {
    typo: "display heading",
    children: "display heading",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6605-52863&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const PageHeading: Story = {
  args: {
    typo: "page heading",
    children: "page heading",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6605-52863&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Subtitle: Story = {
  args: {
    typo: "subtitle",
    children: "subtitle",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6605-52863&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const SectionHeading: Story = {
  args: {
    typo: "section heading",
    children: "section heading",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6605-52863&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const ObjectHeading: Story = {
  args: {
    typo: "object heading",
    children: "object heading",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6605-52863&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Label1: Story = {
  args: {
    typo: "label 1",
    children: "label 1",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6605-52863&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Label2: Story = {
  args: {
    typo: "label 2",
    children: "label 2",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6605-52863&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const NavigationLabel: Story = {
  args: {
    typo: "navigation label",
    children: "navigation label",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6605-52863&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Body1: Story = {
  args: {
    typo: "body 1",
    children: "body 1",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6605-52863&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Body2: Story = {
  args: {
    typo: "body 2",
    children: "body 2",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6605-52863&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Body3: Story = {
  args: {
    typo: "body 3",
    children: "body 3",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6605-52863&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const Caption: Story = {
  args: {
    typo: "caption",
    children: "caption",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6605-52863&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};
