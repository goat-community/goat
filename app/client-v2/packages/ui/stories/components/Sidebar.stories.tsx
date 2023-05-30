import type { Meta, StoryObj } from "@storybook/react";

import { DashboardSidebar } from "../../components/DashboardSidebar";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof DashboardSidebar> = {
  component: DashboardSidebar,
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof DashboardSidebar>;

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
