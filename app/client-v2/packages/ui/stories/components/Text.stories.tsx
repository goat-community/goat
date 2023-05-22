import type { Meta, StoryObj } from "@storybook/react";

import { ThemeProvider } from "../theme";
import { Text } from "../theme";

const meta: Meta<typeof Text> = {
  component: Text,
  tags: ["autodocs"],
  argTypes: {
    className: {
      control: false,
    },
    typo: {
      options: [
        "display heading",
        "page heading",
        "subtitle",
        "section heading",
        "object heading",
        "label 1",
        "label 2",
        "navigation label",
        "body 1",
        "body 2",
        "body 3",
        "caption",
      ],
      control: {
        type: "select",
      },
    },
    color: {
      options: ["primary", "secondary", "disabled", "focus"],
      control: {
        type: "select",
      },
    },
    children: {
      control: false,
    },
    htmlComponent: {
      options: ["h1", "h2", "h3", "h4", "h5", "h6", "p", "span", "div", "a"],
      control: {
        type: "select",
      },
    },
    componentProps: {
      control: false,
    },
    fixedSize_enabled: {
      control: { type: "boolean" },
    },
    fixedSize_content: {
      control: { type: "text" },
    },
    fixedSize_fontWeight: {
      control: { type: "number" },
    },
  },
  args: {
    typo: "subtitle",
    children: "Hello World",
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
type Story = StoryObj<typeof Text>;

export const DisplayHeading: Story = {
  args: {
    typo: "display heading",
    children: "display heading",
  },
};

export const PageHeading: Story = {
  args: {
    typo: "page heading",
    children: "page heading",
  },
};

export const Subtitle: Story = {
  args: {
    typo: "subtitle",
    children: "subtitle",
  },
};

export const SectionHeading: Story = {
  args: {
    typo: "section heading",
    children: "section heading",
  },
};

export const ObjectHeading: Story = {
  args: {
    typo: "object heading",
    children: "object heading",
  },
};

export const Label1: Story = {
  args: {
    typo: "label 1",
    children: "label 1",
  },
};

export const Label2: Story = {
  args: {
    typo: "label 2",
    children: "label 2",
  },
};

export const NavigationLabel: Story = {
  args: {
    typo: "navigation label",
    children: "navigation label",
  },
};

export const Body1: Story = {
  args: {
    typo: "body 1",
    children: "body 1",
  },
};

export const Body2: Story = {
  args: {
    typo: "body 2",
    children: "body 2",
  },
};

export const Body3: Story = {
  args: {
    typo: "body 3",
    children: "body 3",
  },
};

export const Caption: Story = {
  args: {
    typo: "caption",
    children: "caption",
  },
};
