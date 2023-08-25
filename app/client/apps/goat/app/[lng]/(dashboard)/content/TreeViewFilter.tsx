import { calculateLayersCountByKey, calculateLayersCountByKeyAndValue } from "@/lib/utils/helpers";
import React from "react";

import { TreeViewWithCheckboxes, Divider } from "@p4b/ui/components/DataDisplay";
import TreeViewWithIcons from "@p4b/ui/components/DataDisplay/TreeViewWithIcons";
import { Button } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";
import type {ISelectedFolder} from "@/types/dashboard/content";

interface ITreeViewFilterProps {
  selectedFilters: string[];
  setSelectedFilters: (value: string[]) => void;
  handleSelectFolder: (value: ISelectedFolder) => void;
  handleAddFolder: () => void;
  folderData: [] | undefined;
  projectData: [] | undefined;
  reportData: [] | undefined;
  layerData: [] | undefined;
  setFolderAnchorData: (args: { anchorEl: EventTarget & HTMLButtonElement; folder: ISelectedFolder }) => void;
  setSelectedFolder: (object) => void;
}

const TreeViewFilter = (props: ITreeViewFilterProps) => {
  const {
    selectedFilters,
    setSelectedFilters,
    projectData,
    reportData,
    layerData,
    folderData,
    handleSelectFolder,
    handleAddFolder,
    setFolderAnchorData,
    setSelectedFolder,
  } = props;
  const { classes } = useStyles();

  const treeData = [
    {
      id: "layers",
      name: "Layers",
      count: `(${layerData?.length || 0})`,
      children: [
        {
          id: "feature",
          name: "Feature",
          count: `(${calculateLayersCountByKey(layerData, "feature_layer_type")})`,
          children: [
            {
              id: "standard",
              name: "Standard",
              count: `(${calculateLayersCountByKeyAndValue(layerData, "feature_layer_type", "standard")})`,
            },
            {
              id: "indicator",
              name: "Indicator",
              count: `(${calculateLayersCountByKeyAndValue(layerData, "feature_layer_type", "indicator")})`,
            },
            {
              id: "scenario",
              name: "Scenario",
              count: `(${calculateLayersCountByKeyAndValue(layerData, "feature_layer_type", "scenario")})`,
            },
          ],
        },
        {
          id: "imagery_layer",
          name: "Imagery",
          count: `(${calculateLayersCountByKeyAndValue(layerData, "type", "imagery_layer")})`,
        },
        {
          id: "tile_layer",
          name: "Tile",
          count: `(${calculateLayersCountByKeyAndValue(layerData, "type", "tile_layer")})`,
        },
        {
          id: "table",
          name: "Table",
          count: `(${calculateLayersCountByKeyAndValue(layerData, "type", "table")})`,
        },
      ],
    },
    {
      id: "project",
      name: "Projects",
      count: `(${projectData?.length || 0})`,
      // children: projectData ?? [],
    },
    {
      id: "report",
      name: "Reports",
      count: `(${reportData?.length || 0})`,
      // children: reportData ?? [],
    },
  ];

  // Functions
  function clearFilters() {
    setSelectedFilters([]);
  }

  return (
    <>
      <div className={classes.wrapper}>
        <div className={classes.folderWrapper}>
          <TreeViewWithIcons
            homeData={folderData || []}
            organizationData={[]}
            teamsData={[]}
            setFolderAnchor={setFolderAnchorData}
            handleSelectFolder={handleSelectFolder}
            handleAddFolder={handleAddFolder}
            setSelectedFolder={setSelectedFolder}
          />
        </div>
        <Divider color="main" width="100%" />
        <div className={classes.filtersWrapper}>
          <TreeViewWithCheckboxes
            selected={selectedFilters}
            changeSelected={setSelectedFilters}
            treeData={treeData}
          />
        </div>
        {selectedFilters.length ? <Button onClick={clearFilters}>Clear Filters</Button> : null}
      </div>
    </>
  );
};

const useStyles = makeStyles({ name: { TreeViewFilter } })(() => ({
  wrapper: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    height: "100%",
  },

  folderWrapper: {
    ul: {
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
      height: "100%",
      gap: "20px",
    },
  },
  filtersWrapper: {
    backgroundColor: "#2BB3810A",
  },
}));

export default TreeViewFilter;
