import type { Meta, StoryObj } from "@storybook/react/dist";

import { ToggleTabs } from "../../../components/Navigation/ToggleTabs";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof ToggleTabs> = {
  component: ToggleTabs,
  tags: ["autodocs"],
  argTypes: {},
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof ToggleTabs>;

export const Simple: Story = {
  args: {
    tabs: [
      {
        iconId: "formatLeft",
        value: "formatLeft",
      },
      {
        iconId: "viewModul",
        value: "viewModul",
      },
    ],
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6601%3A50950&mode=dev",
    },
  },
};
