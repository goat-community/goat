import FolderIcon from "@mui/icons-material/Folder";
import HelpIcon from "@mui/icons-material/Help";
import HomeIcon from "@mui/icons-material/Home";
import SettingsSuggestIcon from "@mui/icons-material/SettingsSuggest";
import type { Meta, StoryObj } from "@storybook/react";

import { DashboardSidebar } from "../../components/DashboardSidebar";
import { createIcon } from "../../components/Icon";
import { ThemeProvider } from "../theme";

const { Icon } = createIcon({
  help: HelpIcon,
  home: HomeIcon,
  settings: SettingsSuggestIcon,
  folder: FolderIcon,
});

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
      { link: "https://google.com", icon: () => <Icon iconId="home" />, placeholder: "Home" },
      { link: "https://google.com", icon: () => <Icon iconId="folder" />, placeholder: "Content" },
      { link: "https://google.com", icon: () => <Icon iconId="settings" />, placeholder: "Settings" },
      { link: "https://google.com", icon: () => <Icon iconId="help" />, placeholder: "Help" },
    ],
    width: 60,
    extended_width: 200,
  },
};
