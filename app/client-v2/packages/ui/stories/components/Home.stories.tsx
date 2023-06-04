import type { Meta, StoryObj } from "@storybook/react/dist";

import Home from "../../components/temporary/Home";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof Home> = {
  component: Home,
  tags: ["autodocs"],
  title: "Pages/Dashboard/Home",
  argTypes: {
    severity: {
      options: ["warning", "info", "error", "success"],
      control: { type: "radio" },
    },
    children: {
      control: false,
    },
    className: {
      control: false,
    },
    classes: {
      control: false,
    },
  },
  args: {
    severity: "info",
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
type Story = StoryObj<typeof Home>;

export const Warning: Story = {
  args: {},
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=11533-159301&t=HR0djJcCsGmFmiKK-0",
    },
  },
};
