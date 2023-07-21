import type { Meta, StoryObj } from "@storybook/react/dist";

import { DatePicker } from "../../../components/Inputs";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof DatePicker> = {
  component: DatePicker,
  tags: ["autodocs"],
  argTypes: {},
  args: {},
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof DatePicker>;

export const Small: Story = {
  args: {
    size: "small",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6569%3A39888&mode=dev",
    },
  },
};

export const Medium: Story = {
  args: {
    size: "medium",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6569%3A39888&mode=dev",
    },
  },
};
