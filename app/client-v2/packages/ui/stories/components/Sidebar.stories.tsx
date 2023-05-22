import type { Meta, StoryObj } from "@storybook/react";

import { Sidebar } from "../../components/Sidebar";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof Sidebar> = {
  component: Sidebar,
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof Sidebar>;

export const Default: Story = {
  args: {
    items: [
      { link: "https://google.com", iconId: "home", placeholder: "Home" },
      { link: "https://google.com", iconId: "folder", placeholder: "Content" },
      { link: "https://google.com", iconId: "settings", placeholder: "Settings" },
      { link: "https://google.com", iconId: "help", placeholder: "Help" },
    ],
  },
};
