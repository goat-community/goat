"use client";

import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { TreeView, TreeItem } from "@mui/lab";
import { Checkbox, FormControlLabel } from "@mui/material";
import { styled } from "@mui/material/styles";
import React, { useState, useEffect } from "react";
import { v4 } from "uuid";

import { makeStyles } from "../../lib/ThemeProvider";
import { Text } from "../theme";
import { Tooltip } from "./Tooltip";

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
  selected?: string[];
  changeSelected?: (value: string[]) => void;
}

/**
 * A custom TreeView component with checkboxes.
 * @param {TreeViewProps} props - The props for the TreeView component.
 * @returns The rendered TreeView component.
 */
export const TreeViewWithCheckboxes: React.FC<TreeViewProps> = (props) => {
  const { treeData, selected, changeSelected } = props;
  const { classes } = useStyles();

  // Component State
  const [checked, setChecked] = useState<string[]>([]);

  // functions
  const handleToggle = (_: React.ChangeEvent<HTMLInputElement>, nodeId: string) => {
    if (checked.includes(nodeId)) {
      setChecked(checked.filter((id) => id !== nodeId));
      if (changeSelected) {
        changeSelected(checked.filter((id) => id !== nodeId));
      }
    } else {
      setChecked([...checked, nodeId]);
      if (changeSelected) {
        changeSelected([...checked, nodeId]);
      }
    }
  };

  /**
   * Handles the parent check for a given tree node.
   * If the parent has children, it checks if all the children are already checked.
   * If all children are checked, it unchecks them and updates the selected values accordingly.
   * If not all children are checked, it checks them and updates the selected values accordingly.
   * @param {TreeNode} parent - The parent tree node to handle the check for.
   * @returns None
   */
  const handleParentCheck = (parent: TreeNode) => {
    if ("children" in parent) {
      const checkedChildrenIds = getAllChildrenIds(parent);
      const allChecked = checkedChildrenIds.every((id) => checked.includes(id));

      if (allChecked) {
        setChecked(checked.filter((id) => !checkedChildrenIds.includes(id)));
        if (changeSelected) {
          changeSelected(checked.filter((id) => !checkedChildrenIds.includes(id)));
        }
      } else {
        setChecked([...checked, ...checkedChildrenIds]);
        if (changeSelected) {
          changeSelected([...checked, ...checkedChildrenIds]);
        }
      }
    }
  };

  /**
   * Recursively retrieves the IDs of all children nodes of a given TreeNode.
   * @param {TreeNode} node - The TreeNode object to retrieve children IDs from.
   * @returns {string[]} An array of strings representing the IDs of all children nodes.
   */
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

  const renderTree = (nodes: TreeNode, type: "root" | "child") => (
    <StyledTreeItem
      key={nodes.id}
      className={classes.label}
      nodeId={nodes.id}
      label={
        <FormControlLabel
          className={classes.formLabel}
          control={
            <Checkbox
              checked={checked.includes(nodes.id)}
              indeterminate={
                nodes?.children?.some((child) => checked.includes(child.id)) && !checked.includes(nodes.id)
              }
              onChange={(event) => {
                handleToggle(event, nodes.id);
                handleParentCheck(nodes);
              }}
            />
          }
          label={
            <span style={{ display: "flex", gap: "4px", alignItems: "center" }}>
              <Tooltip title={nodes.name}>
                <Text typo="body 1" className={`tag ${type === "root" ? "nodeTag" : ""}`}>
                  {nodes.name}
                </Text>
              </Tooltip>
              {nodes.count ? (
                <Text typo="body 3" className={classes.count}>
                  {nodes.count}
                </Text>
              ) : null}
            </span>
          }
        />
      }>
      {Array.isArray(nodes.children)
        ? nodes.children.map((childNode) => renderTree(childNode, "child"))
        : null}
    </StyledTreeItem>
  );

  useEffect(() => {
    if (selected !== undefined && !selected.length && checked.length) {
      setChecked([]);
    }
  }, [selected]);

  return (
    <TreeView defaultCollapseIcon={<ExpandMoreIcon />} defaultExpandIcon={<ChevronRightIcon />}>
      {treeData.map((data) => (
        <div key={v4()} className={classes.treeRootNode}>
          {renderTree(data, "root")}
        </div>
      ))}
    </TreeView>
  );
};

const useStyles = makeStyles({ name: { TreeViewWithCheckboxes } })((theme) => ({
  label: {
    "&:hover": {
      background: "transparent",
    },
    flexWrap: "wrap",
  },
  count: {
    fontStyle: "italic",
    color: theme.colors.palette.dark.greyVariant4,
  },
  treeRootNode: {
    marginBottom: theme.spacing(5),
    "& .nodeTag": {
      fontWeight: "800",
    },
    "& .tag": {
      whiteSpace: "nowrap",
      overflow: "hidden",
      textOverflow: "ellipsis",
    },
    "& .css-9se70z-MuiTypography-root": {
      // width: "90%",
    },
    "& .mui-3cdohd-MuiTypography-root": {
      width: "100%",
    },
  },
  formLabel: {
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
    width: "100%",
  },
}));
