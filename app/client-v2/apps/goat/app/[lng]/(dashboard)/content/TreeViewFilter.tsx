import React from "react";

import { TreeViewWithCheckboxes, TreeView, Divider } from "@p4b/ui/components/DataDisplay";
import { Card } from "@p4b/ui/components/Surfaces";
import { Button } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

interface ITreeViewFilterProps {
  selectedFilters: string[];
  setSelectedFilters: (value: string[]) => void;
  folderData: [] | undefined;
  projectData: [] | undefined;
  reportData: [] | undefined;
  layerData: [] | undefined;
}

const TreeViewFilter = (props: ITreeViewFilterProps) => {
  const { selectedFilters, setSelectedFilters, projectData, reportData, layerData, folderData } = props;
  const { classes } = useStyles();

  const treeData = [
    {
      id: "layer",
      name: "Layers",
      count: `(${layerData?.length || 0})`,
      children: layerData ?? [],
    },
    {
      id: "project",
      name: "Projects",
      count: `(${projectData?.length || 0})`,
      children: projectData ?? [],
    },
    {
      id: "report",
      name: "Reports",
      count: `(${reportData?.length || 0})`,
      children: reportData ?? [],
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
          <TreeView nodes={folderData || []} />
        </div>
        <Divider color="main" />
        <TreeViewWithCheckboxes
          selected={selectedFilters}
          changeSelected={setSelectedFilters}
          treeData={treeData}
        />
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
}));

export default TreeViewFilter;
