import type { Meta, StoryObj } from "@storybook/react";

import { Tabs } from "../../../components/Navigation/Tabs";
import { ThemeProvider } from "../../theme";

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
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6579%3A45052&mode=dev",
    },
  },
};
