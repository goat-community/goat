import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { TreeView as MUITreeView, TreeItem } from "@mui/lab";
import * as React from "react";
import { memo } from "react";

import { makeStyles } from "../../lib/ThemeProvider";

export type TreeViewProps = {
  className?: string;
  nodes: TreeNode[];
  getSelected?: (node: TreeNode) => void;
};

interface TreeNode {
  id: string;
  name: React.ReactNode;
  count?: string;
  children?: TreeNode[];
}

/**
 * A memoized component that renders a tree view.
 * @param {TreeViewProps} props - The props for the TreeView component.
 * @returns The rendered TreeView component.
 */

export const TreeView = memo((props: TreeViewProps) => {
  const { className, nodes, getSelected } = props;

  const { classes } = useStyles();

  // functions
  function handleItemClick(node: TreeNode) {
    if (getSelected) {
      getSelected(node);
    }
  }

  /**
   * Recursively renders a list of tree nodes as React components.
   * @param {TreeNode[]} list - The list of tree nodes to render.
   * @returns {React.ReactNode} - The rendered React components.
   */

  function returnItems(list: TreeNode[]): React.ReactNode {
    return (
      <>
        {list.map((item) => (
          <div key={item.id}>
            <TreeItem
              className={classes.treeItem}
              onClick={() => handleItemClick(item)}
              nodeId={item.id}
              label={item.name}
            />
            {item.children ? returnItems(item.children) : null}
          </div>
        ))}
      </>
    );
  }

  return (
    <MUITreeView
      className={className}
      aria-label="file system navigator"
      defaultCollapseIcon={<ExpandMoreIcon />}
      defaultExpandIcon={<ChevronRightIcon />}
      sx={{ maxHeight: 200, flexGrow: 1, maxWidth: 400, overflowY: "auto" }}>
      {nodes.map((node) => (
        <div key={node.id}>
          <TreeItem
            className={classes.treeItem}
            onClick={() => handleItemClick(node)}
            nodeId={node.id}
            label={node.name}>
            {node.children ? returnItems(node.children) : null}
          </TreeItem>
        </div>
      ))}
    </MUITreeView>
  );
});

const useStyles = makeStyles({ name: { TreeView } })((theme) => ({
  treeItem: {
    "& .MuiTreeItem-content:hover, & .MuiTreeItem-content:focus, & .MuiTreeItem-content:active, & .MuiTreeItem-content.Mui-selected":
      {
        background: theme.colors.palette.light.greyVariant1,
      },
    "& .css-1kj19pu-MuiTreeItem-content.Mui-selected:hover, & .css-1kj19pu-MuiTreeItem-content.Mui-selected.Mui-focused ":
      {
        background: theme.colors.palette.light.greyVariant1,
      },
  },
}));

TreeView.displayName = "Stepper";
