import type { Meta, StoryObj } from "@storybook/react/dist";

import Footer from "../../../components/Navigation/Footer";
import { ThemeProvider } from "../../theme";

const meta: Meta<typeof Footer> = {
  component: Footer,
  tags: ["autodocs"],
  argTypes: {},
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof Footer>;

export const Warning: Story = {
  args: {
    text: "Lörem ipsum od ohet dilogi. Bell trabel, samuligt, ohöbel utom diska. Jinesade bel när feras redorade i belogi. FAR paratyp i muvåning, och pesask vyfisat. Viktiga poddradio har un mad och inde.",
    links: [
      {
        header: "Navigate",
        links: [
          {
            name: "Home it work",
          },
          {
            name: "Pricing",
          },
          {
            name: "Blog",
          },
          {
            name: "Demo",
          },
        ],
      },
      {
        header: "Study Areas",
        links: [
          {
            name: "Germany",
          },
          {
            name: "EU",
          },
          {
            name: "UK",
          },
          {
            name: "Asia",
          },
          {
            name: "Americas",
          },
        ],
      },
      {
        header: "Contact ",
        links: [
          {
            name: "+49 89 2000 708 30",
            icon: "phone",
            underline: true,
          },
          {
            name: "info@plan4better.de",
            icon: "email",
            underline: true,
          },
          {
            name: "Am Kartoffelgarten 14 c/o WERK1 81671 München Germany",
            icon: "marker",
            underline: true,
          },
        ],
      },
    ],
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=12355%3A135782&mode=dev",
    },
  },
};
