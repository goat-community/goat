import type { Meta, StoryObj } from "@storybook/react/dist";

import { SelectField } from "../../../components/Inputs/SelectField";
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
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=11533-159301&t=HR0djJcCsGmFmiKK-0",
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
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=11533-159301&t=HR0djJcCsGmFmiKK-0",
    },
  },
};
