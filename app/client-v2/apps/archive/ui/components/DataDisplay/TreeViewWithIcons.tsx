import ApartmentIcon from "@mui/icons-material/Apartment";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import CreateNewFolderIcon from "@mui/icons-material/CreateNewFolder";
import FolderIcon from "@mui/icons-material/Folder";
import GroupsIcon from "@mui/icons-material/Groups";
import HomeIcon from "@mui/icons-material/Home";
import type { TreeItemProps } from "@mui/lab/TreeItem";
import TreeItem, { treeItemClasses } from "@mui/lab/TreeItem";
import TreeView from "@mui/lab/TreeView";
import Box from "@mui/material/Box";
import type { SvgIconProps } from "@mui/material/SvgIcon";
import Typography from "@mui/material/Typography";
import { styled, useTheme } from "@mui/material/styles";
import * as React from "react";
import { v4 } from "uuid";

declare module "react" {
  interface CSSProperties {
    "--tree-view-color"?: string;
    "--tree-view-bg-color"?: string;
  }
}

type StyledTreeItemProps = TreeItemProps & {
  bgColor?: string;
  bgColorForDarkMode?: string;
  color?: string;
  colorForDarkMode?: string;
  labelIcon: React.ElementType<SvgIconProps>;
  labelInfo?: string;
  labelText: string;
};

interface ITreeViewWithIconsProps {
  homeData: [] | undefined;
  organizationData: [] | undefined;
  teamsData: [] | undefined;
  handleSelectFolder: () => void;
}

const StyledTreeItemRoot = styled(TreeItem)(({ theme }) => ({
  color: theme.palette.text.secondary,
  [`& .${treeItemClasses.content}`]: {
    color: theme.palette.text.secondary,
    borderTopRightRadius: theme.spacing(2),
    borderBottomRightRadius: theme.spacing(2),
    paddingRight: theme.spacing(1),
    fontWeight: theme.typography.fontWeightMedium,
    "&.Mui-expanded": {
      fontWeight: theme.typography.fontWeightRegular,
    },
    "&:hover": {
      backgroundColor: theme.palette.action.hover,
    },
    "&.Mui-focused, &.Mui-selected, &.Mui-selected.Mui-focused": {
      backgroundColor: `var(--tree-view-bg-color, ${theme.palette.action.selected})`,
      color: "var(--tree-view-color)",
    },
    [`& .${treeItemClasses.label}`]: {
      fontWeight: "inherit",
      color: "inherit",
    },
  },
  [`& .${treeItemClasses.group}`]: {
    marginLeft: 0,
    [`& .${treeItemClasses.content}`]: {
      paddingLeft: theme.spacing(2),
    },
  },
  ul: { padding: "0 20px" },
}));

function StyledTreeItem(props: StyledTreeItemProps) {
  const theme = useTheme();
  const {
    bgColor,
    color,
    labelIcon: LabelIcon,
    labelInfo,
    labelText,
    colorForDarkMode,
    bgColorForDarkMode,
    ...other
  } = props;

  const styleProps = {
    "--tree-view-color": theme.palette.mode !== "dark" ? color : colorForDarkMode,
    "--tree-view-bg-color": theme.palette.mode !== "dark" ? bgColor : bgColorForDarkMode,
  };

  return (
    <StyledTreeItemRoot
      label={
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            p: 0.5,
            pr: 0,
            color,
          }}>
          <Box component={LabelIcon} color="inherit" sx={{ mr: 1 }} />
          <Typography variant="body2" sx={{ fontWeight: "inherit", flexGrow: 1 }}>
            {labelText}
          </Typography>
          <Typography variant="caption" color="inherit">
            {labelInfo}
          </Typography>
        </Box>
      }
      style={styleProps}
      {...other}
    />
  );
}

export default function TreeViewWithIcons(props: ITreeViewWithIconsProps) {
  const { homeData, organizationData, teamsData, handleSelectFolder, handleAddFolder } = props;

  return (
    <TreeView
      aria-label="gmail"
      defaultExpanded={["3"]}
      defaultCollapseIcon={<ArrowDropDownIcon />}
      defaultExpandIcon={<ArrowRightIcon />}
      defaultEndIcon={<div style={{ width: 24 }} />}
      sx={{ height: 264, flexGrow: 1, maxWidth: 400, overflowY: "auto" }}>
      <StyledTreeItem nodeId="1" labelText="Home" labelIcon={HomeIcon} color="#2BB381">
        {homeData?.map((item) => {
          return (
            <StyledTreeItem
              key={v4()}
              nodeId={item.id}
              labelText={item.name}
              labelIcon={FolderIcon}
              onClick={() => handleSelectFolder(item)}
              // labelInfo="90"
              color="#2BB381"
            />
          );
        })}
        <StyledTreeItem
          nodeId={v4()}
          labelText="New Folder"
          labelIcon={CreateNewFolderIcon}
          onClick={() => handleAddFolder()}
          // labelInfo="90"
          color="#2BB381"
        />
      </StyledTreeItem>
      <StyledTreeItem nodeId="2" labelText="Organization" labelIcon={ApartmentIcon} color="#2BB381">
        {organizationData?.map(() => {
          <StyledTreeItem
            key={v4()}
            nodeId={item.id}
            labelText={item.name}
            labelIcon={FolderIcon}
            // labelInfo="90"
            color="#2BB381"
          />;
        })}
      </StyledTreeItem>
      <StyledTreeItem nodeId="3" labelText="Teams" labelIcon={GroupsIcon} color="#2BB381">
        {teamsData?.map(() => {
          <StyledTreeItem
            key={v4()}
            nodeId={item.id}
            labelText={item.name}
            labelIcon={FolderIcon}
            // labelInfo="90"
            color="#2BB381"
          />;
        })}
      </StyledTreeItem>
    </TreeView>
  );
}
