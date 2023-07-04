import React, { useState } from "react";

import { makeStyles } from "../../../../lib/ThemeProvider";
import { TreeViewWithCheckboxes } from "../../../DataDisplay";
import { Card } from "../../../Surfaces";
import { Button } from "../../../theme";

const TreeViewFilter = () => {
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);
  const { classes } = useStyles();

  const treeData = [
    {
      id: "node1",
      name: "Node 1",
      count: "(100)",
      children: [
        {
          id: "node1-1",
          name: "Node 1.1",
          count: "(72)",
        },
        {
          id: "node1-2",
          name: "Node 1.2",
          count: "(28)",
        },
      ],
    },
    {
      id: "node2",
      name: "Node 2",
      count: "(43)",
    },
    {
      id: "node3",
      name: "Node 3",
      count: "(10)",
      children: [
        {
          id: "node3-1",
          name: "Node 3.1",
          count: "(6)",
          children: [
            {
              id: "node3-1-1",
              name: "Node 3.1.1",
              count: "(4)",
            },
          ],
        },
      ],
    },
  ];

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
