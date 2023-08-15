import type { Meta, StoryObj } from "@storybook/react";

import { SlideShow } from "../../components/SlideShow";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof SlideShow> = {
  component: SlideShow,
  tags: ["autodocs"],
  argTypes: {
    className: {
      control: false,
    },
    images: {
      control: {
        type: "array",
      },
    },
    children: {
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
type Story = StoryObj<typeof SlideShow>;

export const Slideshow: Story = {
  args: {
    images: [
      {
        label: "San Francisco – Oakland Bay Bridge, United States",
        description:
          "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Dolores nulla voluptates, perferendis saepe exercitationem sed quaerat hic ab repudiandae velit ea nemo ut iste laudantium quos voluptatibus ipsa explicabo quae?",
        imgPath:
          "https://images.unsplash.com/photo-1537944434965-cf4679d1a598?auto=format&fit=crop&w=400&h=250&q=60",
      },
      {
        label: "Bird",
        description:
          "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Dolores nulla voluptates, perferendis saepe exercitationem sed quaerat hic ab repudiandae velit ea nemo ut iste laudantium quos voluptatibus ipsa explicabo quae?",
        imgPath:
          "https://images.unsplash.com/photo-1538032746644-0212e812a9e7?auto=format&fit=crop&w=400&h=250&q=60",
      },
      {
        label: "Bali, Indonesia",
        description:
          "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Dolores nulla voluptates, perferendis saepe exercitationem sed quaerat hic ab repudiandae velit ea nemo ut iste laudantium quos voluptatibus ipsa explicabo quae?",
        imgPath:
          "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=400&h=250",
      },
      {
        label: "Goč, Serbia",
        description:
          "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Dolores nulla voluptates, perferendis saepe exercitationem sed quaerat hic ab repudiandae velit ea nemo ut iste laudantium quos voluptatibus ipsa explicabo quae?",
        imgPath:
          "https://images.unsplash.com/photo-1512341689857-198e7e2f3ca8?auto=format&fit=crop&w=400&h=250&q=60",
      },
    ],
    height: 400,
    width: "100%",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=12355%3A135730&mode=dev",
    },
  },
};

export const OnlyTitle: Story = {
  args: {
    images: [
      {
        label: "San Francisco – Oakland Bay Bridge, United States",
        imgPath:
          "https://images.unsplash.com/photo-1537944434965-cf4679d1a598?auto=format&fit=crop&w=400&h=250&q=60",
      },
      {
        label: "Bird",
        imgPath:
          "https://images.unsplash.com/photo-1538032746644-0212e812a9e7?auto=format&fit=crop&w=400&h=250&q=60",
      },
      {
        label: "Bali, Indonesia",
        imgPath:
          "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=400&h=250",
      },
      {
        label: "Goč, Serbia",
        imgPath:
          "https://images.unsplash.com/photo-1512341689857-198e7e2f3ca8?auto=format&fit=crop&w=400&h=250&q=60",
      },
    ],
    height: 400,
    width: "100%",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=12355%3A135730&mode=dev",
    },
  },
};

export const OnlyDescription: Story = {
  args: {
    images: [
      {
        description:
          "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Dolores nulla voluptates, perferendis saepe exercitationem sed quaerat hic ab repudiandae velit ea nemo ut iste laudantium quos voluptatibus ipsa explicabo quae?",
        imgPath:
          "https://images.unsplash.com/photo-1537944434965-cf4679d1a598?auto=format&fit=crop&w=400&h=250&q=60",
      },
      {
        description:
          "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Dolores nulla voluptates, perferendis saepe exercitationem sed quaerat hic ab repudiandae velit ea nemo ut iste laudantium quos voluptatibus ipsa explicabo quae?",
        imgPath:
          "https://images.unsplash.com/photo-1538032746644-0212e812a9e7?auto=format&fit=crop&w=400&h=250&q=60",
      },
      {
        description:
          "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Dolores nulla voluptates, perferendis saepe exercitationem sed quaerat hic ab repudiandae velit ea nemo ut iste laudantium quos voluptatibus ipsa explicabo quae?",
        imgPath:
          "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=400&h=250",
      },
      {
        description:
          "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Dolores nulla voluptates, perferendis saepe exercitationem sed quaerat hic ab repudiandae velit ea nemo ut iste laudantium quos voluptatibus ipsa explicabo quae?",
        imgPath:
          "https://images.unsplash.com/photo-1512341689857-198e7e2f3ca8?auto=format&fit=crop&w=400&h=250&q=60",
      },
    ],
    height: 400,
    width: "100%",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=12355%3A135730&mode=dev",
    },
  },
};

export const PlainSlideshow: Story = {
  args: {
    images: [
      {
        imgPath:
          "https://images.unsplash.com/photo-1537944434965-cf4679d1a598?auto=format&fit=crop&w=400&h=250&q=60",
      },
      {
        imgPath:
          "https://images.unsplash.com/photo-1538032746644-0212e812a9e7?auto=format&fit=crop&w=400&h=250&q=60",
      },
      {
        imgPath:
          "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=400&h=250",
      },
      {
        imgPath:
          "https://images.unsplash.com/photo-1512341689857-198e7e2f3ca8?auto=format&fit=crop&w=400&h=250&q=60",
      },
    ],
    height: 400,
    width: "100%",
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=12355%3A135730&mode=dev",
    },
  },
};
