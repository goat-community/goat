import { Box } from "@mui/material";
import type { Meta, StoryObj } from "@storybook/react";
import type { ReactNode } from "react";

import { Card } from "../../components/Card";
import { Text } from "../theme";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof Card> = {
  component: Card,
  tags: ["autodocs"],
  argTypes: {
    aboveDivider: {
      control: false,
    },
    children: {
      control: false,
    },
    className: {
      control: false,
    },
  },
  args: {
    children: <h1>Hello</h1>,
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
type Story = StoryObj<typeof Card>;

const imageAboveDevider: ReactNode = (
  <Box
    component="img"
    sx={{
      height: 233,
      width: 350,
      maxHeight: { xs: 233, md: 167 },
      maxWidth: { xs: 350, md: 250 },
    }}
    alt="The house from the offer."
    src="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&w=350&dpr=2"
  />
);

export const Simple: Story = {
  args: {
    children: <Text typo="body 1">Card Content</Text>,
  },
};

export const AboveDivider: Story = {
  args: {
    children: <Text typo="body 1">Smaple Media Card</Text>,
    aboveDivider: imageAboveDevider,
  },
};
