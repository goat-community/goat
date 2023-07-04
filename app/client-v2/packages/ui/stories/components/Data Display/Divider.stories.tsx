import type { Meta, StoryObj } from "@storybook/react/dist";

import { Divider } from "../../../components/DataDisplay/Divider";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof Divider> = {
  component: Divider,
  tags: ["autodocs"],
  argTypes: {
    width: {
      control: {
        type: "text",
      },
    },
    color: {
      options: ["main", "light", "gray"],
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
type Story = StoryObj<typeof Divider>;

export const Warning: Story = {
  args: {
    width: "100px",
    color: "main",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6595-48211&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};
