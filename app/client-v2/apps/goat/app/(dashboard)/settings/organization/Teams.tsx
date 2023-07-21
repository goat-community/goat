"use client";

import React, { useState } from "react";

import { TextField } from "@p4b/ui/components/Inputs";
import { Button, Icon, Text } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";

import type { Option } from "./AddTeamModal";
import AddTeamModal from "./AddTeamModal";
import TeamsTable from "./TeamsTable";

export interface Team {
  name: string;
  participants: Option[];
  createdAt: string;
}

const Teams = () => {
  const [ismodalVisible, setModalVisible] = useState<boolean>(false);
  const [teams, setTeams] = useState<Team[]>([]);
  const [searchWord, setSearchWord] = useState<string>("");

  const { classes } = useStyles();

  function addTeam(team: Team) {
    setTeams([...teams, team]);
    setSearchWord("");
  }

  function editTeam(team: Team) {
    const updatedTeams = teams.map((singleTeam) => {
      if (singleTeam.name === team.name) {
        return team;
      }
      return singleTeam;
    });

    setTeams([...updatedTeams]);
  }

  return (
    <div>
      <div className={classes.headWrapper}>
        <div className={classes.head}>
          <Icon
            iconId="user"
            wrapped="circle"
            bgVariant="gray2"
            bgOpacity={0.6}
            iconVariant="secondary"
            size="medium"
          />
          <Text typo="body 1" className={classes.name}>
            Organization name
          </Text>
        </div>
        <div className={classes.search}>
          <TextField
            className={classes.searchInput}
            type="text"
            label="Search"
            size="small"
            onValueBeingTypedChange={({ value }) => setSearchWord(value)}
          />
          <Icon iconId="filter" size="medium" iconVariant="gray" />
          <div style={{ position: "relative" }}>
            <Button className={classes.searchButton} onClick={() => setModalVisible(true)}>
              New Team
            </Button>
          </div>
        </div>
        <AddTeamModal visibility={ismodalVisible} setVisibility={setModalVisible} addTeam={addTeam} />
      </div>
      {teams.length ? (
        <TeamsTable rawRows={teams} editTeam={editTeam} searchText={searchWord} />
      ) : (
        <div className={classes.createTeam}>
          <img src="/assets/illustrations/teams.svg" alt="" />
          <Text typo="page heading" color="focus" className={classes.IconText}>
            Create teams to easily manage your projects
          </Text>
        </div>
      )}
      {/* {teams ? teams.map((team) => team.name) : null} */}
    </div>
  );
};

const useStyles = makeStyles({ name: { Teams } })((theme) => ({
  bannerText: {
    color: "white",
    "@media (max-width: 1268px)": {
      fontSize: "14px",
    },
  },
  IconText: {
    fontWeight: "500",
  },
  name: {
    fontWeight: "bold",
  },
  createTeam: {
    marginTop: "22px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  headWrapper: {
    padding: theme.spacing(3),
    paddingTop: "0",
  },
  head: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(2),
    marginBottom: theme.spacing(3),
  },
  buttons: {
    display: "flex",
    alignItems: "center",
    justifyContent: "end",
    gap: theme.spacing(2),
  },
  search: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: theme.spacing(4),
    marginBottom: theme.spacing(3),
  },
  searchButton: {
    width: "131px",
  },
  container: {
    padding: `0px ${theme.spacing(3)}px`,
    marginBottom: theme.spacing(2),
  },
  searchInput: {
    flexGrow: "1",
  },
  tableCard: {
    padding: theme.spacing(3),
    marginBottom: theme.spacing(5),
  },
  userDataContainer: {
    border: `1px solid ${theme.colors.palette[theme.isDarkModeEnabled ? "dark" : "light"].greyVariant1}`,
    padding: theme.spacing(3),
    borderRadius: 4,
  },
  userDataText: {
    display: "flex",
    gap: theme.spacing(1),
    alignItems: "center",
    marginBottom: theme.spacing(2),
  },
  userDataTitle: {
    fontWeight: "800",
  },
  formInputs: {
    // marginTop: theme.spacing(3),
    display: "flex",
    flexDirection: "column",
    gap: theme.spacing(2),
  },
  modalHeader: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(1),
  },
  buttonSmall: {
    padding: "3px 10px",
  },
  switcher: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(1),
  },
}));

export default Teams;
