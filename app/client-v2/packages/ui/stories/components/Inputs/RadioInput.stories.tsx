import type { Meta, StoryObj } from "@storybook/react/dist";

import { RadioInput } from "../../../components/Inputs";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof RadioInput> = {
  component: RadioInput,
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
type Story = StoryObj<typeof RadioInput>;

export const Small: Story = {
  args: {},
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6569%3A39888&mode=dev",
    },
  },
};
