import React, { useState, useEffect } from "react";

import { EnhancedTable } from "@p4b/ui/components/DataDisplay";
import Modal from "@p4b/ui/components/Modal";
import { Card } from "@p4b/ui/components/Surfaces";
import { IconButton } from "@p4b/ui/components/theme";
import { Text, Button } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

import type { Option } from "./AddTeamModal";
import TeamModalBody from "./TeamModalBody";
import type { Team } from "./Teams";

interface TeamsTableProps {
  rows: Team[];
  editTeam: (value: Team) => void;
}

const TeamsTable = (props: TeamsTableProps) => {
  const { rows, editTeam } = props;

  const [userInDialog, setUserInDialog] = useState<Team | boolean>();
  const [selectedOption, setSelectedOption] = useState<Option[] | null>(null);
  const [teamName, setTeamName] = useState<string | null>(null);

  const { classes } = useStyles();

  const columnNames = [
    {
      id: "1",
      numeric: false,
      label: "Team",
    },
    {
      id: "2",
      numeric: true,
      label: "Users",
    },
    {
      id: "3",
      numeric: true,
      label: "Creation",
    },
  ];

  useEffect(() => {
    if (userInDialog && typeof userInDialog !== "boolean") {
      const team = rows.find((row) => row.name === userInDialog.name);
      setSelectedOption(team ? team.participants : null);
      setTeamName(team ? team.name : "");
    }
  }, [userInDialog]);

  function saveEditTeam() {
    if (userInDialog && typeof userInDialog !== "boolean") {
      const team = rows.find((row) => row.name === userInDialog.name);
      if (team) {
        team.participants = selectedOption;
        team.name = teamName;
        editTeam(team);
        setUserInDialog(false);
      }
    }
  }

  return (
    <Card noHover={true} className={classes.tableCard}>
      <EnhancedTable
        rows={[
          ...rows.map((row) => ({
            name: row.name,
            count: row.participants.length,
            createdAt: row.createdAt,
          })),
        ]}
        dense={false}
        alternativeColors={false}
        columnNames={columnNames}
        openDialog={setUserInDialog}
        action={<IconButton type="submit" iconId="edit" size="medium" iconVariant="focus" />}
        checkbox={false}
        hover={true}
      />
      <Modal
        header={
          <div className={classes.modalHeader}>
            <Text typo="subtitle" className={classes.modalHeadertext}>
              Edit Team
            </Text>
            <IconButton onClick={() => setSelectedOption(null)} iconId="close" />
          </div>
        }
        action={
          <>
            <Button onClick={() => setUserInDialog(false)} variant="noBorder">
              CANCEL
            </Button>
            <Button onClick={saveEditTeam} variant="noBorder">
              SAVE
            </Button>
          </>
        }
        width="444px"
        open={userInDialog ? true : false}
        changeOpen={setUserInDialog}>
        {userInDialog && typeof userInDialog !== "boolean" ? (
          <TeamModalBody
            selectedEditRow={userInDialog}
            selectedOption={selectedOption}
            setSelectedOption={setSelectedOption}
            setTeamName={setTeamName}
          />
        ) : null}
      </Modal>
    </Card>
  );
};

const useStyles = makeStyles({ name: { TeamsTable } })((theme) => ({
  tableCard: {
    padding: theme.spacing(3),
  },
  modalHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  modalHeadertext: {
    fontWeight: "500",
  },
  input: {
    width: "100%",
  },
  label: {
    paddingBottom: theme.spacing(2),
    fontWeight: "bold",
  },
  boxLabel: {
    marginBottom: theme.spacing(5),
  },
  useSelectedWrapper: {
    display: "flex",
    marginTop: theme.spacing(3),
    justifyContent: "space-between",
  },
  userSelected: {
    display: "flex",
    gap: theme.spacing(1),
  },
  italic: {
    fontStyle: "italic",
  },
  orangeButton: {
    "&.MuiButton-text": {
      color: "orange",
      "&:hover": {
        color: "orange",
      },
    },
  },
}));

export default TeamsTable;
