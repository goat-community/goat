import type { Meta, StoryObj } from "@storybook/react";

import Table from "../../components/Table";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof Table> = {
  component: Table,
  decorators: [
    (Story) => (
      <ThemeProvider>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof Table>;

export const Default: Story = {
  args: {
    columnNames: ["Name", "E-mail", "Role", "Status", "Added"],
    rows: [
      {
        name: "John William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
      {
        name: "John William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
      {
        name: "John William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
      {
        name: "John William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
      {
        name: "John William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
      {
        name: "John William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
    ],
  },
};
