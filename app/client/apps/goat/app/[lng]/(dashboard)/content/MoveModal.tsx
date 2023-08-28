import React from "react";

import { TreeView } from "@p4b/ui/components/DataDisplay";
import { Icon } from "@p4b/ui/components/theme";
import { Button } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

interface MoveModalProps {
  changeState: (value: { name: string; icon: React.ReactNode; value: string } | null) => void;
}

const MoveModal = (props: MoveModalProps) => {
  const { changeState } = props;

  const { classes } = useStyles();

  // Dumb Temporary Data
  const treeData = [
    {
      id: "node_1",
      name: (
        <div className={classes.folder}>
          <Icon iconId="folder" />
          Report_Final_Version
        </div>
      ),
    },
    {
      id: "node_2",
      name: (
        <div className={classes.folder}>
          <Icon iconId="folder" />
          plan_4_better
        </div>
      ),
    },
    {
      id: "node_3",
      name: (
        <div className={classes.folder}>
          <Icon iconId="folder" />
          example_proj
        </div>
      ),
      children: [
        {
          id: "node_3_1",
          name: (
            <div className={classes.folder}>
              <Icon iconId="folder" />
              april_2023
            </div>
          ),
        },
      ],
    },
    {
      id: "node_4",
      name: (
        <div className={classes.folder}>
          <Icon iconId="folder" />
          Report_Final_Version
        </div>
      ),
    },
    {
      id: "node_5",
      name: (
        <div className={classes.folder}>
          <Icon iconId="folder" />
          plan_4_better
        </div>
      ),
    },
    {
      id: "node_6",
      name: (
        <div className={classes.folder}>
          <Icon iconId="folder" />
          example_proj
        </div>
      ),
      children: [
        {
          id: "node_6_1",
          name: (
            <div className={classes.folder}>
              <Icon iconId="folder" />
              april_2023
            </div>
          ),
        },
      ],
    },
  ];

  return (
    <div>
      <TreeView nodes={treeData} className={classes.treeView} />
      <div className={classes.buttons}>
        <Button variant="noBorder" onClick={() => changeState(null)}>
          MOVE HERE
        </Button>
        <Button variant="noBorder" onClick={() => changeState(null)}>
          CANCEL
        </Button>
      </div>
    </div>
  );
};

const useStyles = makeStyles({ name: { TreeView } })((theme) => ({
  folder: {
    display: "flex",
    gap: theme.spacing(2),
    padding: `6px 0px`,
  },
  buttons: {
    display: "flex",
    alignItems: "center",
    justifyContent: "end",
    gap: theme.spacing(2),
    marginTop: theme.spacing(3),
  },
  treeView: {
    maxHeight: "150px",
  },
}));

export default MoveModal;
