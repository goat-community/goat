import type { Meta, StoryObj } from "@storybook/react/dist";

import { Chip } from "../../../components/DataDisplay";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof Chip> = {
  component: Chip,
  tags: ["autodocs"],
  argTypes: {},
  args: {},
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof Chip>;

export const Filled: Story = {
  args: {
    label: "Filled",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=10520-71026&t=wp26gbfVi2Dqh0qt-0",
    },
  },
};

export const FilledWithBorder: Story = {
  args: {
    label: "Filled",
    variant: "filledWithBorder",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=10520-71026&t=wp26gbfVi2Dqh0qt-0",
    },
  },
};

export const Bordered: Story = {
  args: {
    label: "Bordered",
    variant: "Border",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=10520-71026&t=wp26gbfVi2Dqh0qt-0",
    },
  },
};

export const BorderedItalic: Story = {
  args: {
    label: "Italic",
    variant: "Border",
    textDesign: "italic",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=10520-71026&t=wp26gbfVi2Dqh0qt-0",
    },
  },
};

export const FilledNormal: Story = {
  args: {
    label: "Normal",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=10520-71026&t=wp26gbfVi2Dqh0qt-0",
    },
  },
};
