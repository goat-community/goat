import type { Meta, StoryObj } from "@storybook/react";

import { DashboardSidebar } from "../../../components/Navigation";
import { ThemeProvider } from "../../theme";

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
      {
        link: "https://google.com",
        icon: "home",
        placeholder: "Home",
      },
      {
        link: "https://google.com",
        icon: "folder",
        placeholder: "Content",
      },
      {
        link: "https://google.com",
        icon: "settingsSuggested",
        placeholder: "Settings",
      },
      {
        link: "https://google.com",
        icon: "help",
        placeholder: "Help",
      },
    ],
    width: 60,
    extended_width: 200,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=12355%3A135784&mode=dev",
    },
  },
};
