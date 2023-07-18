import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import ForwardIcon from "@mui/icons-material/Forward";
import type { Meta, StoryObj } from "@storybook/react";

import { createIcon } from "../../components/Icon/Icon";
import { Toolbar } from "../../components/Toolbar";
import { ThemeProvider } from "../theme";

const { Icon } = createIcon({
  info: ForwardIcon,
  profile: AccountCircleIcon,
});

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
      { link: "https://google.com", icon: () => <Icon iconId="profile" size="medium" iconVariant="gray2" /> },
      { link: "https://google.com", icon: () => <Icon iconId="info" size="medium" iconVariant="gray2" /> },
    ],
    height: 52,
  },
};