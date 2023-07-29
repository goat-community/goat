import React from "react";

import { TreeViewWithCheckboxes } from "@p4b/ui/components/DataDisplay";
import { Card } from "@p4b/ui/components/Surfaces";
import { Button } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

interface ITreeViewFilterProps {
  data: object;
  selectedFilters: string[];
  setSelectedFilters: (value: string[]) => void;
}

const TreeViewFilter = (props: ITreeViewFilterProps) => {
  const { data, selectedFilters, setSelectedFilters } = props;
  const { classes } = useStyles();

  const typeCount = {};
  data?.items.forEach((item) => {
    const type = item.type;
    if (!typeCount[type]) {
      typeCount[type] = 0;
    }
    typeCount[type]++;
  });

  const outputArr = Object.entries(typeCount).map(([type, count]) => ({
    id: type,
    name: type.toUpperCase(),
    count: `(${count})`,
    // children: [],
  }));

  //todo remove after
  // const treeData = [
  //   {
  //     id: "layers",
  //     name: "Layers",
  //     count: "(100)",
  //     children: [
  //       {
  //         id: "feature",
  //         name: "Feature",
  //         count: "(72)",
  //       },
  //       {
  //         id: "imagery",
  //         name: "Imagery",
  //         count: "(28)",
  //       },
  //     ],
  //   },
  //   {
  //     id: "reports",
  //     name: "Reports",
  //     count: "(43)",
  //   },
  //   {
  //     id: "projects",
  //     name: "Projects",
  //     count: "(10)",
  //     children: [
  //       {
  //         id: "project_one",
  //         name: "Project_one",
  //         count: "(6)",
  //         children: [
  //           {
  //             id: "project_two",
  //             name: "Project_Twosadddsadsdfsaad",
  //             count: "(4)",
  //           },
  //         ],
  //       },
  //     ],
  //   },
  // ];

  // Functions
  function clearFilters() {
    setSelectedFilters([]);
  }

  return (
    <Card className={classes.treeView} noHover={true} width="100%">
      <div className={classes.wrapper}>
        <TreeViewWithCheckboxes
          selected={selectedFilters}
          changeSelected={setSelectedFilters}
          treeData={outputArr}
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
