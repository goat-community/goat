"use client";

import AddTeamModal from "@/components/settings/organization/AddTeamModal";
import TeamsTable from "@/components/settings/organization/TeamsTable";
import React, { useState } from "react";

import { TextField } from "@p4b/ui/components/Inputs";
import Banner from "@p4b/ui/components/Surfaces/Banner";
import { Button, Icon, Text } from "@p4b/ui/components/theme";
import { makeStyles } from "@p4b/ui/lib/ThemeProvider";
import Image from "next/image";
import type {ITeam} from "@/types/dashboard/organization";

const Teams = () => {
  const [ismodalVisible, setModalVisible] = useState<boolean>(false);
  const [teams, setTeams] = useState<ITeam[]>([]);
  const [searchWord, setSearchWord] = useState<string>("");

  const { classes } = useStyles();

  function addTeam(team: ITeam) {
    setTeams([...teams, team]);
    setSearchWord("");
  }

  function editTeam(team: ITeam) {
    const updatedTeams = teams.map((singleTeam) => {
      if (singleTeam.name === team.name) {
        return team;
      }
      return singleTeam;
    });

    setTeams([...updatedTeams]);
  }

  return (
    <div className={classes.container}>
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
          <Image src="/assets/illustrations/teams.svg" alt="" width={400} height={300}/>
          <Text typo="page heading" color="focus" className={classes.IconText}>
            Create teams to easily manage your projects
          </Text>
        </div>
      )}
      <Banner
        className={classes.banner}
        actions={<Button>Subscribe Now</Button>}
        content={
          <Text className={classes.bannerText} typo="body 1">
            Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean
            massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.{" "}
          </Text>
        }
        image="https://s3-alpha-sig.figma.com/img/630a/ef8f/d732bcd1f3ef5d6fe31bc6f94ddfbca8?Expires=1687132800&Signature=aJvQ22UUlmvNjDlrgzV6MjJK~YgohUyT9mh8onGD-HhU5yMI0~ThWZUGVn562ihhRYqlyiR5Rskno84OseNhAN21WqKNOZnAS0TyT3SSUP4t4AZJOmeuwsl2EcgElMzcE0~Qx2X~LWxor1emexxTlWntivbnUeS6qv1DIPwCferjYIwWsiNqTm7whk78HUD1-26spqW3AXVbTtwqz3B8q791QigocHaK9b4f-Ulrk3lsmp8BryHprwgetHlToFNlYYR-SqPFrEeOKNQuEDKH0QzgGv3TX7EfBNL0kgP3Crued~JNth-lIEPCjlDRnFQyNpSiLQtf9r2tH9xIsKA~XQ__&Key-Pair-Id=APKAQ4GOSFWCVNEHN3O4"
        imageSide="right"
      />
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
    marginBottom: theme.spacing(5) + theme.spacing(3),
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
    paddingTop: theme.spacing(2),
    paddingBottom: theme.spacing(2),
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
  banner: {
    marginTop: theme.spacing(5),
  },
}));

export default Teams;
