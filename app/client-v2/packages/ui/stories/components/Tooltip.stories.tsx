import { Typography } from "@mui/material";
import type { Meta, StoryObj } from "@storybook/react";

import CustomizedTooltips from "../../components/Tooltip";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof CustomizedTooltips> = {
  component: CustomizedTooltips,
  tags: ["autodocs"],
  argTypes: {
    title: {
      control: { type: "text" },
    },
    placement: {
      options: ["top", "bottom", "left"],
      control: { type: "radio" },
    },
    children: {
      control: false,
    },
  },
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
type Story = StoryObj<typeof CustomizedTooltips>;

export const Top: Story = {
  // diffrent args for each anchor direction
  args: {
    title: "Top tooltip",
    placement: "top",
    arrow: true,
    children: (
      <Typography display="inline" variant="h5" color="primary">
        Top
      </Typography>
    ),
  },
};

export const Left: Story = {
  args: {
    title: "Left tooltip",
    placement: "left",
    arrow: true,
    children: (
      <Typography display="inline" variant="h5" color="primary">
        Left
      </Typography>
    ),
  },
};

export const Bottom: Story = {
  args: {
    title: "Bottom tooltip",
    placement: "bottom",
    arrow: true,
    children: (
      <Typography display="inline" variant="h5" color="primary">
        Bottom
      </Typography>
    ),
  },
};

export const ArrowLess: Story = {
  args: {
    title: "Arrow less tooltip",
    placement: "top",
    children: (
      <Typography display="inline" variant="h5" color="primary">
        Arrow less
      </Typography>
    ),
  },
};
