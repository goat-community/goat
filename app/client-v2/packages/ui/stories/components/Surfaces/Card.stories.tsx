import { Box } from "@mui/material";
import type { Meta, StoryObj } from "@storybook/react/dist";
import type { ReactNode } from "react";

import { Card } from "../../../components/Surfaces";
import { CardContent } from "../../../components/Surfaces";
import { CardMedia } from "../../../components/Surfaces";
import { Text, Button, ThemeProvider } from "../../theme";

const meta: Meta<typeof Card> = {
  component: Card,
  tags: ["autodocs"],
  argTypes: {
    aboveDivider: {
      control: false,
    },
    children: {
      control: false,
    },
    className: {
      control: false,
    },
    width: {
      control: {
        type: "number",
      },
    },
  },
  args: {
    children: <h1>Hello</h1>,
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
type Story = StoryObj<typeof Card>;

const imageAboveDevider: ReactNode = (
  <Box
    component="img"
    sx={{
      height: 233,
      width: 350,
      maxHeight: { xs: 233, md: 167 },
      maxWidth: { xs: 350, md: 250 },
    }}
    alt="The house from the offer."
    src="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&w=350&dpr=2"
  />
);

export const EmptyCard: Story = {
  args: {
    children: "Simple Card",
  },
};

export const EmptyCardWithMedia: Story = {
  args: {
    children: "Simple Card",
    aboveDivider: (
      <CardMedia
        src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQy9x3wyV5OWYWA8XxBJKMlH2QvuSSOIdOItRK1jgXSQ&s"
        alt="sampleCard"
      />
    ),
  },
};

export const CardFile: Story = {
  args: {
    children: (
      <CardContent
        chips={["hello", "wo", "how are you"]}
        description="Hello_world.pdf"
        icon="file"
        title="Test 1"
      />
    ),
    width: 268,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=11581-140623&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const CardProject: Story = {
  args: {
    children: (
      <CardContent
        chips={["hello", "world", "how are you"]}
        info={{
          author: "Someone Anyone",
          date: "19 May 2023",
        }}
        title="Test 1"
      />
    ),
    aboveDivider: (
      <CardMedia
        src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQy9x3wyV5OWYWA8XxBJKMlH2QvuSSOIdOItRK1jgXSQ&s"
        alt="sampleCard"
      />
    ),
    width: 268,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=11581-140621&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const CardBlog: Story = {
  args: {
    children: (
      <CardContent
        chips={["hello", "world", "how are you"]}
        description="It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout."
        info={{
          author: "Someone Anyone",
          date: "19 May 2023",
        }}
        title="Test 1"
      />
    ),
    aboveDivider: (
      <CardMedia
        src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQy9x3wyV5OWYWA8XxBJKMlH2QvuSSOIdOItRK1jgXSQ&s"
        alt="sampleCard"
      />
    ),
    width: 268,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=11581-140622&t=m1TtlHDKRmJk5wCK-0",
    },
  },
};

export const AddCard: Story = {
  args: {
    children: (
      <div style={{ margin: "20px" }}>
        <Button>
          <Text typo="label 1">+</Text>
          <Text typo="label 2">New</Text>
        </Button>
      </div>
    ),
    width: 268,
    transparentBg: true,
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=11581-140620&t=HR0djJcCsGmFmiKK-0",
    },
  },
};
