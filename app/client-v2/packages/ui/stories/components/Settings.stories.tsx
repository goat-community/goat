import type { Meta, StoryObj } from "@storybook/react/dist";

import Settings from "../../components/temporary/settings/Settings";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof Settings> = {
  component: Settings,
  tags: ["autodocs"],
  title: "Pages/Dashboard/Settings",
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
type Story = StoryObj<typeof Settings>;

export const Warning: Story = {
  args: {},
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=11581%3A140792&mode=dev",
    },
  },
};
