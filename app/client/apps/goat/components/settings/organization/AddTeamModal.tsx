import TeamModalBody from "./TeamModalBody";
import React, { useState } from "react";

import type { Option } from "@p4b/types/atomicComponents";
import Modal from "@p4b/ui/components/Modal";
import { Button, Text, IconButton } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";
import type {ITeam} from "@/types/dashboard/organization";

interface AddTeamModalProps {
  visibility: boolean;
  setVisibility: (value: boolean) => void;
  addTeam: (value: ITeam) => void;
}

const AddTeamModal = (props: AddTeamModalProps) => {
  const { visibility, setVisibility, addTeam } = props;

  const { classes } = useStyles();

  const [selectedOption, setSelectedOption] = useState<Option[] | undefined>([]);
  const [teamName, setTeamName] = useState<string | null>(null);

  function saveTeam() {
    if (teamName && selectedOption && selectedOption.length) {
      addTeam({
        name: teamName,
        participants: selectedOption,
        createdAt: "23 Jun 19",
      });
      setSelectedOption([]);
      setVisibility(false);
    }
  }

  function handleClose() {
    setVisibility(false);
    setSelectedOption([]);
  }

  return (
    <Modal
      width="444px"
      open={visibility}
      changeOpen={setVisibility}
      action={
        <>
          <Button onClick={handleClose} variant="noBorder">
            CANCEL
          </Button>
          <Button onClick={saveTeam} variant="noBorder">
            SAVE
          </Button>
        </>
      }
      header={
        <div className={classes.modalHeader}>
          <Text typo="subtitle" className={classes.modalHeadertext}>
            New team
          </Text>
          <IconButton onClick={handleClose} iconId="close" />
        </div>
      }>
      <TeamModalBody
        setSelectedOption={setSelectedOption}
        selectedOption={selectedOption}
        setTeamName={setTeamName}
      />
    </Modal>
  );
};

const useStyles = makeStyles({ name: { AddTeamModal } })((theme) => ({
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

export default AddTeamModal;
