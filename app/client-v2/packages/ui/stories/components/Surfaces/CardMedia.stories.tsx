import type { Meta, StoryObj } from "@storybook/react";

import { CardMedia } from "../../../components/Surfaces";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof CardMedia> = {
  component: CardMedia,
  tags: ["autodocs"],
  argTypes: {
    className: {
      control: false,
    },
    src: {
      control: {
        type: "text",
      },
    },
    alt: {
      control: {
        type: "text",
      },
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
type Story = StoryObj<typeof CardMedia>;

export const Sample: Story = {
  args: {
    src: "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQy9x3wyV5OWYWA8XxBJKMlH2QvuSSOIdOItRK1jgXSQ&s",
    alt: "Card Media",
  },
};

export const Sample2: Story = {
  args: {
    src: "https://map.viamichelin.com/map/carte?map=viamichelin&z=10&lat=41.95893&lon=19.53383&width=550&height=382&format=png&version=latest&layer=background&debug_pattern=.*",
    alt: "Card Media",
  },
};
