import type { Meta, StoryObj } from "@storybook/react";

import { Tabs } from "../../components/Tabs";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof Tabs> = {
  component: Tabs,
  tags: ["autodocs"],
  argTypes: {
    className: {
      control: false,
    },
    tabs: {
      control: {
        type: "array",
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
type Story = StoryObj<typeof Tabs>;

export const Primary: Story = {
  args: {
    tabs: [
      {
        child: <div>Hello world</div>,
        name: "Hello World",
      },
      {
        child: <div>Hello mars</div>,
        name: "Hello Mars",
      },
      {
        child: <div>Hello mercury</div>,
        name: "Hello Mercury",
      },
    ],
  },
};
