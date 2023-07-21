import React, { useState } from "react";

import { TreeViewWithCheckboxes } from "@p4b/ui/components/DataDisplay";
import { Card } from "@p4b/ui/components/Surfaces";
import { Button } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

const TreeViewFilter = () => {
  const { classes } = useStyles();

  // Component States
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);

  const treeData = [
    {
      id: "layers",
      name: "Layers",
      count: "(100)",
      children: [
        {
          id: "feature",
          name: "Feature",
          count: "(72)",
        },
        {
          id: "imagery",
          name: "Imagery",
          count: "(28)",
        },
      ],
    },
    {
      id: "reports",
      name: "Reports",
      count: "(43)",
    },
    {
      id: "projects",
      name: "Projects",
      count: "(10)",
      children: [
        {
          id: "project_one",
          name: "Project_one",
          count: "(6)",
          children: [
            {
              id: "project_two",
              name: "Project_Twosadddsadsdfsaad",
              count: "(4)",
            },
          ],
        },
      ],
    },
  ];

  // Functions
  function clearFilters() {
    setSelectedFilters([]);
  }

  return (
    <Card className={classes.treeView} noHover={true} width="280px">
      <div className={classes.wrapper}>
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
    width: "19%",
    marginLeft: "13%",
    padding: theme.spacing(3),
  },
  wrapper: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    height: "100%",
  },
}));

export default TreeViewFilter;
