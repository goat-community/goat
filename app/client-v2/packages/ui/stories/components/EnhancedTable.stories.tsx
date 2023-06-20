import type { Meta, StoryObj } from "@storybook/react";

import EnhancedTable from "../../components/EnhancedTable";
import { ThemeProvider } from "../theme";

const meta: Meta<typeof EnhancedTable> = {
  component: EnhancedTable,
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
type Story = StoryObj<typeof EnhancedTable>;

export const EnhancedTableFullOption: Story = {
  args: {
    columnNames: [
      {
        id: "name",
        numeric: false,
        label: "Name",
      },
      {
        id: "email",
        numeric: false,
        label: "Email",
      },
      {
        id: "role",
        numeric: false,
        label: "Role",
      },
      {
        id: "status",
        numeric: false,
        label: "Status",
      },
      {
        id: "added",
        numeric: false,
        label: "Added",
      },
    ],
    rows: [
      {
        name: "Luca William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
      {
        name: "Fenix William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
      {
        name: "Adam William Silva",
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

export const EnhancedTableWithoutCheckbox: Story = {
  args: {
    checkbox: false,
    columnNames: [
      {
        id: "name",
        numeric: false,
        label: "Name",
      },
      {
        id: "email",
        numeric: false,
        label: "Email",
      },
      {
        id: "role",
        numeric: false,
        label: "Role",
      },
      {
        id: "status",
        numeric: false,
        label: "Status",
      },
      {
        id: "added",
        numeric: false,
        label: "Added",
      },
    ],
    rows: [
      {
        name: "Luca William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
      {
        name: "Fenix William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
      {
        name: "Adam William Silva",
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

export const EnhancedTableWithoutMoreIcon: Story = {
  args: {
    more: false,
    columnNames: [
      {
        id: "name",
        numeric: false,
        label: "Name",
      },
      {
        id: "email",
        numeric: false,
        label: "Email",
      },
      {
        id: "role",
        numeric: false,
        label: "Role",
      },
      {
        id: "status",
        numeric: false,
        label: "Status",
      },
      {
        id: "added",
        numeric: false,
        label: "Added",
      },
    ],
    rows: [
      {
        name: "Luca William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
      {
        name: "Fenix William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
      {
        name: "Adam William Silva",
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

export const EnhancedTableWithoutMoreIconAndCheckbox: Story = {
  args: {
    more: false,
    checkbox: false,
    columnNames: [
      {
        id: "name",
        numeric: false,
        label: "Name",
      },
      {
        id: "email",
        numeric: false,
        label: "Email",
      },
      {
        id: "role",
        numeric: false,
        label: "Role",
      },
      {
        id: "status",
        numeric: false,
        label: "Status",
      },
      {
        id: "added",
        numeric: false,
        label: "Added",
      },
    ],
    rows: [
      {
        name: "Luca William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
      {
        name: "Fenix William Silva",
        email: "john.wloremipsum@gmail.com",
        role: "Admin",
        status: "Active",
        Added: "23 Jun 19",
      },
      {
        name: "Adam William Silva",
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
