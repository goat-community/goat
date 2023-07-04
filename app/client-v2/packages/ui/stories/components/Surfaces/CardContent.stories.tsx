import type { Meta, StoryObj } from "@storybook/react";

import { CardContent } from "../../../components/Surfaces";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof CardContent> = {
  component: CardContent,
  tags: ["autodocs"],
  argTypes: {
    className: {
      control: false,
    },
    title: {
      control: { type: "text" },
    },
    description: {
      control: { type: "text" },
    },
    chips: {
      control: { type: "array" },
    },
    info: {
      control: { type: "object" },
    },
    icon: {
      control: false,
    },
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
type Story = StoryObj<typeof CardContent>;

export const FileContent: Story = {
  args: {
    title: "Test 1",
    icon: "file",
    description: "Hello_world.pdf",
    chips: ["hello", "world", "how are you"],
  },
};

export const ProjectContent: Story = {
  args: {
    info: {
      author: "Someone Anyone",
      date: "19 May 2023",
    },
    title: "Test 1",
    chips: ["hello", "world", "how are you"],
  },
};

export const BlogContent: Story = {
  args: {
    info: {
      author: "Someone Anyone",
      date: "19 May 2023",
    },
    title: "Test 1",
    description:
      "It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout.",
    chips: ["hello", "world", "how are you"],
  },
};
