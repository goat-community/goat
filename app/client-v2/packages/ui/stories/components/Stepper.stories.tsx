import type { Meta, StoryObj } from "@storybook/react/dist";

import Stepper from "../../components/Stepper";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof Stepper> = {
  component: Stepper,
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
type Story = StoryObj<typeof Stepper>;

export const Simple: Story = {
  args: {
    steps: [
      {
        label: "Select campaign settings",
        child: <div>first</div>,
      },
      {
        label: "Create an ad group",
        child: <div>second</div>,
      },
      {
        label: "Create an ad",
        child: <div>third</div>,
      },
    ],
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=12598%3A134645&mode=dev",
    },
  },
};
