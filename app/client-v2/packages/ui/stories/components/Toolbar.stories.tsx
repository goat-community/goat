import type { Meta, StoryObj } from "@storybook/react";

import { Toolbar } from "../../components/Toolbar";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof Toolbar> = {
  component: Toolbar,
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof Toolbar>;

export const Default: Story = {
  args: {
    items: [
      { link: "https://google.com", iconId: "profile" },
      { link: "https://google.com", iconId: "info" },
    ],
  },
};
