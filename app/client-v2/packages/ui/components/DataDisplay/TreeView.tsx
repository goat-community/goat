import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { TreeView, TreeItem } from "@mui/lab";
import { Checkbox, FormControlLabel } from "@mui/material";
import { styled } from "@mui/material/styles";
import React, { useState, useEffect } from "react";

import { makeStyles } from "../../lib/ThemeProvider";
import { Text } from "../theme";

// Custom styled TreeItem to adjust the padding
const StyledTreeItem = styled(TreeItem)(({ theme }) => ({
  "& .MuiTreeItem-content": {
    paddingTop: theme.spacing(0.5),
    paddingBottom: theme.spacing(0.5),
  },
  "& .MuiTreeItem-content:hover, & .MuiTreeItem-content:focus, & .MuiTreeItem-content:active, & .MuiTreeItem-content.Mui-selected":
    {
      backgroundColor: "transparent",
    },
}));

interface TreeNode {
  id: string;
  name: string;
  count?: string;
  children?: TreeNode[];
}

interface TreeViewProps {
  treeData: TreeNode[];
  checkbox?: boolean;
  selected: string[];
  changeSelected: (value: string[]) => void;
}

export const TreeViewWithCheckboxes: React.FC<TreeViewProps> = (props) => {
  const { treeData, checkbox = true, selected, changeSelected } = props;
  const [checked, setChecked] = useState<string[]>([]);

  const { classes } = useStyles();

  useEffect(() => {
    if (!selected.length && checked.length) {
      setChecked([]);
    }
  }, [selected]);

  const handleToggle = (event: React.ChangeEvent<HTMLInputElement>, nodeId: string) => {
    if (checked.includes(nodeId)) {
      setChecked(checked.filter((id) => id !== nodeId));
      changeSelected(checked.filter((id) => id !== nodeId));
    } else {
      setChecked([...checked, nodeId]);
      changeSelected([...checked, nodeId]);
    }
  };

  const handleParentCheck = (parent: TreeNode) => {
    if ("children" in parent) {
      const checkedChildrenIds = getAllChildrenIds(parent);
      const allChecked = checkedChildrenIds.every((id) => checked.includes(id));

      if (allChecked) {
        setChecked(checked.filter((id) => !checkedChildrenIds.includes(id)));
        changeSelected(checked.filter((id) => !checkedChildrenIds.includes(id)));
      } else {
        setChecked([...checked, ...checkedChildrenIds]);
        changeSelected([...checked, ...checkedChildrenIds]);
      }
    }
  };

  const getAllChildrenIds = (node: TreeNode): string[] => {
    let childrenIds: string[] = [];
    if (node.children) {
      childrenIds = node.children.map((child) => child.id).flat();
      node.children.forEach((child) => {
        childrenIds.push(...getAllChildrenIds(child));
      });
    }
    return childrenIds;
  };

  const renderTree = (nodes: TreeNode) => (
    <>
      <StyledTreeItem
        key={nodes.id}
        className={classes.label}
        nodeId={nodes.id}
        label={
          <FormControlLabel
            control={
              <Checkbox
                checked={checked.includes(nodes.id)}
                indeterminate={
                  nodes.children &&
                  nodes.children.some((child) => checked.includes(child.id)) &&
                  !checked.includes(nodes.id)
                }
                onChange={(event) => {
                  handleToggle(event, nodes.id);
                  handleParentCheck(nodes);
                }}
              />
            }
            label={
              <span style={{ display: "flex", gap: "4px", alignItems: "center" }}>
                <Text typo="body 1">{nodes.name}</Text>
                {nodes.count ? (
                  <Text typo="body 3" className={classes.count}>
                    {nodes.count}
                  </Text>
                ) : null}
              </span>
            }
          />
        }>
        {Array.isArray(nodes.children) ? nodes.children.map((childNode) => renderTree(childNode)) : null}
      </StyledTreeItem>
    </>
  );

  return (
    <TreeView defaultCollapseIcon={<ExpandMoreIcon />} defaultExpandIcon={<ChevronRightIcon />}>
      {treeData.map((data) => renderTree(data))}
    </TreeView>
  );
};

const useStyles = makeStyles({ name: { TreeViewWithCheckboxes } })((theme) => ({
  label: {
    "&:hover": {
      background: "transparent",
    },
  },
  count: {
    fontStyle: "italic",
    color: theme.colors.palette.dark.greyVariant4,
  },
}));
