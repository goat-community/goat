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

export const Warning: Story = {
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
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=11533-159301&t=HR0djJcCsGmFmiKK-0",
    },
  },
};
