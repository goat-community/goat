import type { Meta, StoryObj } from "@storybook/react";

import { Loading } from "../../components/Loading";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof Loading> = {
  component: Loading,
  tags: ["autodocs"],
  argTypes: {
    size: { control: { type: "number" } },
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
type Story = StoryObj<typeof Loading>;

export const Default: Story = {};
