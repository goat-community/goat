import type { Option } from "@p4b/types/atomicComponents";
import type {ITeam} from "@/types/dashboard/organization";
import React from "react";
import { v4 } from "uuid";

import { Checkbox } from "@p4b/ui/components/Checkbox";
import { Chip } from "@p4b/ui/components/DataDisplay";
import { TextField } from "@p4b/ui/components/Inputs";
import { Text } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

interface TeamModalBodyProps {
  selectedEditRow?: ITeam;
  setSelectedOption?: (value: Option[]) => void;
  selectedOption?: Option[] | null;
  setTeamName?: (value: string) => void;
}

const TeamModalBody = (props: TeamModalBodyProps) => {
  const { selectedEditRow, setSelectedOption, selectedOption, setTeamName } = props;

  const { classes } = useStyles();

  // const options = [
  //   {
  //     label: "Sumaya Randolph",
  //     value: "sumaya",
  //     selected: false,
  //   },
  //   {
  //     label: "Priya Phelps",
  //     value: "priya",
  //     selected: false,
  //   },
  //   {
  //     label: "Amanda Dickson",
  //     value: "amanda",
  //     selected: false,
  //   },
  //   {
  //     label: "Alia Campbell",
  //     value: "alia",
  //     selected: false,
  //   },
  //   {
  //     label: "Cole Chaney",
  //     value: "cole",
  //     selected: false,
  //   },
  //   {
  //     label: "Idris Lowery",
  //     value: "idris",
  //     selected: false,
  //   },
  // ];

  function changeStatusOfUser(user: Option, status: boolean) {
    if (selectedOption) {
      selectedOption?.forEach((userSelected) => {
        if (userSelected.label === user.label) {
          userSelected.selected = status;
        }
      });
    }

    if (setSelectedOption) {
      setSelectedOption(selectedOption ? [...selectedOption] : []);
    }
  }

  // function removeUser(user: Option) {
  //   const options = selectedOption?.filter(
  //     (userSelected) => userSelected.label !== user.label && userSelected
  //   );
  //   if (setSelectedOption) {
  //     setSelectedOption(options ? [...options] : []);
  //   }
  // }

  return (
    <>
      <div className={classes.boxLabel}>
        <Text typo="body 2" className={classes.label}>
          Team name
        </Text>
        <TextField
          onValueBeingTypedChange={({ value }) => (setTeamName ? setTeamName(value) : null)}
          className={classes.input}
          defaultValue={selectedEditRow ? selectedEditRow.name : ""}
          size="small"
          type="text"
        />
      </div>
      <div className={classes.boxLabel}>
        <Text typo="body 2" className={classes.label}>
          Add users
        </Text>
        {/*<AutoComplete*/}
        {/*  selectedOptions={selectedOption}*/}
        {/*  setSelected={setSelectedOption}*/}
        {/*  multiple={true}*/}
        {/*  className={classes.input}*/}
        {/*  size="small"*/}
        {/*  options={options}*/}
        {/*/>*/}
      </div>
      <div>
        {selectedOption && selectedOption.length ? (
          <>
            <Text typo="body 2" className={classes.label}>
              User list
            </Text>
            {selectedOption.map((option) => (
              <div className={classes.useSelectedWrapper} key={v4()}>
                <div className={classes.userSelected}>
                  <Checkbox
                    checked={typeof option.selected === "boolean" ? option.selected : false}
                    onChange={(_: React.SyntheticEvent, value: boolean) =>
                      changeStatusOfUser(option, value)
                    }
                  />
                  <div>
                    <Text typo="body 2">{option.label}</Text>
                    <Text typo="body 3" className={classes.italic} color="secondary">
                      user@email.com
                    </Text>
                  </div>
                </div>
                <Chip label="invited" />
                {/* <IconButton iconId="edit" type="submit" iconVariant="focus" onClick={enterAccessSettings} /> */}
              </div>
            ))}
          </>
        ) : null}
      </div>
    </>
  );
};

const useStyles = makeStyles({ name: { TeamModalBody } })((theme) => ({
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

export default TeamModalBody;
