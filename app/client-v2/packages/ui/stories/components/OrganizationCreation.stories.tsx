import type { Meta, StoryObj } from "@storybook/react/dist";

import OrganizationCreation from "../../components/temporary/auth/OrganizationCreation";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof OrganizationCreation> = {
  component: OrganizationCreation,
  tags: ["autodocs"],
  argTypes: {},
  title: "Pages/Dashboard/Organization",
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof OrganizationCreation>;

export const Warning: Story = {
  args: {},
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=11487%3A116405&mode=dev",
    },
  },
};
