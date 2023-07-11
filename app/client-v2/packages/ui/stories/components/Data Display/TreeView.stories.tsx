import type { Meta, StoryObj } from "@storybook/react/dist";

import { TreeViewWithCheckboxes } from "../../../components/DataDisplay";
import { ThemeProvider } from "../../theme";

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

export const Warning: Story = {
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
