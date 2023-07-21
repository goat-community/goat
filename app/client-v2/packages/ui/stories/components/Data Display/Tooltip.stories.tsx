import { Typography } from "@mui/material";
import type { Meta, StoryObj } from "@storybook/react";

import { Tooltip } from "../../../components/DataDisplay";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof Tooltip> = {
  component: Tooltip,
  tags: ["autodocs"],
  argTypes: {
    title: {
      control: { type: "text" },
    },
    children: {
      control: false,
    },
    enterDelay: {
      control: { type: "number" },
    },
  },
  args: {
    title: "Tooltip",
    children: (
      <Typography variant="h2" color="#000">
        Make sure to follow us
      </Typography>
    ),
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
type Story = StoryObj<typeof Tooltip>;

export const Simple: Story = {
  args: {
    // color: "primary",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=6590-48770&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};
