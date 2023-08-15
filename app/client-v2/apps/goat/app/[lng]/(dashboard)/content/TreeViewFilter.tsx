import { calculateLayersCountByKey, calculateLayersCountByKeyAndValue } from "@/lib/utils/helpers";
import React from "react";

import { TreeViewWithCheckboxes, Divider } from "@p4b/ui/components/DataDisplay";
import TreeViewWithIcons from "@p4b/ui/components/DataDisplay/TreeViewWithIcons";
import { Card } from "@p4b/ui/components/Surfaces";
import { Button } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

interface ITreeViewFilterProps {
  selectedFilters: string[];
  setSelectedFilters: (value: string[]) => void;
  handleSelectFolder: (value: object) => void;
  handleAddFolder: (value: object) => void;
  folderData: [] | undefined;
  projectData: [] | undefined;
  reportData: [] | undefined;
  layerData: [] | undefined;
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
    <Card className={classes.treeView} noHover={true} width="100%">
      <div className={classes.wrapper}>
        <div className={classes.folderWrapper}>
          <TreeViewWithIcons
            homeData={folderData || []}
            organizationData={[]}
            teamsData={[]}
            handleSelectFolder={handleSelectFolder}
            handleAddFolder={handleAddFolder}
          />
        </div>
        <Divider color="main" />
        <div className={classes.filtersWrapper}>
          <TreeViewWithCheckboxes
            selected={selectedFilters}
            changeSelected={setSelectedFilters}
            treeData={treeData}
          />
        </div>
        {selectedFilters.length ? <Button onClick={clearFilters}>Clear Filters</Button> : null}
      </div>
    </Card>
  );
};

const useStyles = makeStyles({ name: { TreeViewFilter } })((theme) => ({
  treeView: {
    padding: theme.spacing(3),
  },
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
