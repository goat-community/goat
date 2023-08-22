import type { Meta, StoryObj } from "@storybook/react/dist";

import { TreeViewWithCheckboxes } from "../../../components/DataDisplay";
import { TreeView } from "../../../components/DataDisplay";
import { makeStyles } from "../../../lib/ThemeProvider";
import { ThemeProvider } from "../../theme";
import { Icon } from "../../theme";

const meta: Meta<typeof TreeViewWithCheckboxes> = {
  component: TreeViewWithCheckboxes,
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
type Story = StoryObj<typeof TreeViewWithCheckboxes>;

export const BasicTreeView: Story = () => {
  const treeData = [
    {
      id: "root",
      name: "Parent",
      children: [
        {
          id: "1",
          name: "Child - 1",
        },
        {
          id: "3",
          name: "Child - 3",
          children: [
            {
              id: "4",
              name: "Child - 4",
            },
          ],
        },
      ],
    },
  ];

  return <TreeView nodes={treeData} />;
};

export const FileTreeView: Story = () => {
  const { classes } = useStyles();

  const treeData = [
    {
      id: "node_1",
      name: (
        <div className={classes.folder}>
          <Icon iconId="folder" />
          Report_Final_Version
        </div>
      ),
    },
    {
      id: "node_2",
      name: (
        <div className={classes.folder}>
          <Icon iconId="folder" />
          plan_4_better
        </div>
      ),
    },
    {
      id: "node_3",
      name: (
        <div className={classes.folder}>
          <Icon iconId="folder" />
          example_proj
        </div>
      ),
      children: [
        {
          id: "node_3_1",
          name: (
            <div className={classes.folder}>
              <Icon iconId="folder" />
              april_2023
            </div>
          ),
        },
      ],
    },
  ];

  return <TreeView nodes={treeData} />;
};

BasicTreeView.args = {};
FileTreeView.args = {};

export const TheTreeViewWithCheckboxes: Story = {
  args: {
    treeData: [
      {
        id: "node1",
        name: "Node 1",
        children: [
          {
            id: "node1-1",
            name: "Node 1.1",
          },
          {
            id: "node1-2",
            name: "Node 1.2",
          },
        ],
      },
      {
        id: "node2",
        name: "Node 2",
      },
      {
        id: "node3",
        name: "Node 3",
        children: [
          {
            id: "node3-1",
            name: "Node 3.1",
            children: [
              {
                id: "node3-1-1",
                name: "Node 3.1.1",
              },
            ],
          },
        ],
      },
    ],
  },
  parameters: {
    design: {
      type: "figma",
      url: "https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?node-id=6601%3A51109&mode=dev",
    },
  },
};

const useStyles = makeStyles({ name: { TreeView } })((theme) => ({
  folder: {
    display: "flex",
    gap: theme.spacing(2),
    padding: `6px 0px`,
  },
}));
