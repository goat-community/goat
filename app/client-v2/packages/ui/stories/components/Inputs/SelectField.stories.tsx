import type { Meta, StoryObj } from "@storybook/react/dist";

import { SelectField } from "../../../components/Inputs";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof SelectField> = {
  component: SelectField,
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
type Story = StoryObj<typeof SelectField>;

export const Small: Story = {
  args: {
    options: [
      { name: "Editor", value: "editor" },
      { name: "Admin", value: "admin" },
      { name: "Guest", value: "guest" },
    ],
    label: "Permission",
    defaultValue: "editor",
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
    options: [
      { name: "Editor", value: "editor" },
      { name: "Admin", value: "admin" },
      { name: "Guest", value: "guest" },
    ],
    label: "Permission",
    defaultValue: "editor",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6569%3A39888&mode=dev",
    },
  },
};
