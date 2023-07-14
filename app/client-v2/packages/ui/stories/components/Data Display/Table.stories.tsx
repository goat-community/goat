import type { Meta, StoryObj } from "@storybook/react";

import { EnhancedTable, Chip, FileManagementTable } from "../../../components/DataDisplay";
import Table from "../../../components/DataDisplay/Table";
import { ThemeProvider } from "../../theme";
import { Icon } from "../../theme";

// import { EnhancedTable } from '../../../components/DataDisplay/EnhancedTable';

const meta: Meta<typeof Table> = {
  component: Table,
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
type Story = StoryObj<typeof Table>;

export const SimpleTable: Story = {
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

export const EnhancedTableSimple: Story = () => {
  return (
    <EnhancedTable
      columnNames={[
        {
          id: "name",
          label: "Name",
          numeric: false,
        },
        {
          id: "email",
          label: "Email",
          numeric: false,
        },
        {
          id: "role",
          label: "Role",
          numeric: false,
        },
        {
          id: "status",
          label: "Status",
          numeric: false,
        },
        {
          id: "added",
          label: "Added",
          numeric: false,
        },
      ]}
      rows={[
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
      ]}
      dense={false}
      alternativeColors={true}
    />
  );
};

EnhancedTableSimple.args = {};
EnhancedTableSimple.parameters = {
  design: {
    type: "figma",
    url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6594%3A46294&mode=dev",
  },
};

export const EnhancedTableWithoutCheckbox: Story = () => {
  return (
    <EnhancedTable
      columnNames={[
        {
          id: "name",
          label: "Name",
          numeric: false,
        },
        {
          id: "email",
          label: "Email",
          numeric: false,
        },
        {
          id: "role",
          label: "Role",
          numeric: false,
        },
        {
          id: "status",
          label: "Status",
          numeric: false,
        },
        {
          id: "added",
          label: "Added",
          numeric: false,
        },
      ]}
      rows={[
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
      ]}
      dense={false}
      alternativeColors={true}
      checkbox={false}
    />
  );
};

EnhancedTableWithoutCheckbox.args = {};
EnhancedTableWithoutCheckbox.parameters = {
  design: {
    type: "figma",
    url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6594%3A46294&mode=dev",
  },
};

export const EnhancedTableWithoutMoreButton: Story = () => {
  return (
    <EnhancedTable
      columnNames={[
        {
          id: "name",
          label: "Name",
          numeric: false,
        },
        {
          id: "email",
          label: "Email",
          numeric: false,
        },
        {
          id: "role",
          label: "Role",
          numeric: false,
        },
        {
          id: "status",
          label: "Status",
          numeric: false,
        },
        {
          id: "added",
          label: "Added",
          numeric: false,
        },
      ]}
      rows={[
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
      ]}
      dense={false}
      alternativeColors={true}
      more={false}
    />
  );
};

EnhancedTableWithoutMoreButton.args = {};
EnhancedTableWithoutMoreButton.parameters = {
  design: {
    type: "figma",
    url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6594%3A46294&mode=dev",
  },
};

export const EnhancedTableWithoutCheckboxesAndMoreButton: Story = () => {
  return (
    <EnhancedTable
      columnNames={[
        {
          id: "name",
          label: "Name",
          numeric: false,
        },
        {
          id: "email",
          label: "Email",
          numeric: false,
        },
        {
          id: "role",
          label: "Role",
          numeric: false,
        },
        {
          id: "status",
          label: "Status",
          numeric: false,
        },
        {
          id: "added",
          label: "Added",
          numeric: false,
        },
      ]}
      rows={[
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
      ]}
      dense={false}
      alternativeColors={true}
      more={false}
      checkbox={false}
    />
  );
};

EnhancedTableWithoutCheckboxesAndMoreButton.args = {};
EnhancedTableWithoutCheckboxesAndMoreButton.parameters = {
  design: {
    type: "figma",
    url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6594%3A46294&mode=dev",
  },
};

export const TableForFileManagement: Story = () => {
  const rows = [
    {
      name: (
        <span style={{ display: "flex", gap: "8px" }}>
          <span style={{ opacity: 0.5 }}>
            <Icon iconId="folder" />
          </span>
          Actions_files
        </span>
      ),
      type: <Chip label="Layer" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Project_XYZ_Conclusion",
      type: <Chip label="Project" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Data_Analysis_2023_Q1",
      type: <Chip label="Image" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Experiment_Results_Phase2",
      type: <Chip label="Report" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Report_Final_Version",
      type: <Chip label="Layer" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Project_XYZ_Conclusion",
      type: <Chip label="Project" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Data_Analysis_2023_Q1",
      type: <Chip label="Image" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Experiment_Results_Phase2",
      type: <Chip label="Report" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Report_Final_Version",
      type: <Chip label="Layer" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Project_XYZ_Conclusion",
      type: <Chip label="Project" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Data_Analysis_2023_Q1",
      type: <Chip label="Image" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
    {
      name: "Experiment_Results_Phase2",
      type: <Chip label="Report" textDesign="italic" variant="Border" />,
      modified: "23 Jun 19",
      size: "30 kb",
    },
  ];

  const columnNames = [
    {
      id: "name",
      label: "Name",
      numeric: false,
    },
    {
      id: "type",
      label: "Type",
      numeric: false,
    },
    {
      id: "modified",
      label: "Modified",
      numeric: false,
    },
    {
      id: "size",
      label: "Size",
      numeric: false,
    },
  ];

  let currPath = ["home"];

  function setPath(value: string[]) {
    currPath = value;
  }

  return (
    <FileManagementTable
      currPath={currPath}
      setPath={setPath}
      hover={true}
      columnNames={columnNames}
      rows={rows}
    />
  );
};

TableForFileManagement.args = {};
TableForFileManagement.parameters = {
  design: {
    type: "figma",
    url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6594%3A46294&mode=dev",
  },
};
