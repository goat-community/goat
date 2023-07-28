import React from "react";
import { useState } from "react";
import { v4 } from "uuid";

import { makeStyles } from "../../../../lib/ThemeProvider";
import { Avatar } from "../../../Avatar";
import { Divider } from "../../../DataDisplay";
import { RadioInput, SelectField } from "../../../Inputs";
import { Text, Icon, Button } from "../../../theme";
import type { IconId } from "../../../theme";

interface AccessSettingsProps {
  changeState: (value: { name: string; icon: React.ReactNode; value: string } | null) => void;
  setModalView: (value: number) => void;
}

const AccessSettings = (props: AccessSettingsProps) => {
  const { changeState, setModalView } = props;

  const { classes } = useStyles();

  // Component States
  const [settingChecked, setSettingChecked] = useState<string>("private");

  //dumb data
  const organizationPermissions = [
    {
      name: <div>View</div>,
      value: "view",
    },
    {
      name: <div>Edit</div>,
      value: "edit",
    },
    {
      name: <div>Download</div>,
      value: "download",
    },
  ];

  const teams = [
    {
      name: (
        <div className={classes.teamName}>
          {" "}
          <Avatar label="TN" size={24} />
          <Text typo="body 2">Team 1</Text>
        </div>
      ),
      value: "team1",
      permission: "",
    },
    {
      name: (
        <div className={classes.teamName}>
          <Avatar label="TN" size={24} />
          <Text typo="body 2">Team 2</Text>
        </div>
      ),
      value: "team2",
      permission: "",
    },
    {
      name: (
        <div className={classes.teamName}>
          <Avatar label="TN" size={24} />
          <Text typo="body 2">Team 3</Text>
        </div>
      ),
      value: "team3",
      permission: "",
    },
  ];

  const accessSettings: {
    name: string;
    value: string;
    icon: IconId;
    description: string;
    child: React.ReactNode;
  }[] = [
    {
      name: "Private",
      value: "private",
      icon: "lock",
      description: "Only you have access",
      child: <></>,
    },
    {
      name: "Organization",
      value: "organization",
      icon: "coorperate",
      description: "Everyone within your organization have access",
      child: (
        <div className={classes.SettingInputWrapper}>
          <Text typo="body 2">@Organization_name</Text>
          <SelectField
            className={classes.selectField}
            options={organizationPermissions}
            multiple={true}
            checkbox={true}
            label="Permissions"
            size="small"
          />
        </div>
      ),
    },
    {
      name: "Teams",
      value: "teams",
      icon: "team",
      description: "Set permission by teams",
      child: (
        <div>
          <Divider width="100%" color="gray" />
          {teams.map((team) => (
            <>
              <div className={classes.SettingInputWrapper}>
                <Text typo="body 2">{team.name}</Text>
                <SelectField
                  className={classes.selectField}
                  options={organizationPermissions}
                  multiple={true}
                  checkbox={true}
                  label="Permissions"
                  size="small"
                />
              </div>
              <Divider width="100%" className={classes.divider} color="gray" />
            </>
          ))}
        </div>
      ),
    },
  ];

  return (
    <div>
      <div style={{ paddingBottom: "23px" }}>
        {accessSettings.map((setting, index) => (
          <>
            <div key={v4()} className={classes.visibilitySettings}>
              <div className={classes.visibility}>
                <Icon iconId={setting.icon} size="small" />
                <div>
                  <Text typo="body 2">{setting.name}</Text>
                  {settingChecked === setting.value ? (
                    <Text typo="body 3" className={classes.italic} color="secondary">
                      {setting.description}
                    </Text>
                  ) : null}
                </div>
              </div>
              <RadioInput value={setting.value} onCheck={setSettingChecked} selectedValue={settingChecked} />
            </div>
            {settingChecked === setting.value ? setting.child : null}
            {index !== accessSettings.length - 1 ? <Divider width="100%" color="gray" /> : null}
          </>
        ))}
      </div>
      <div className={classes.buttons}>
        <Button variant="noBorder" onClick={() => changeState(null)}>
          CANCEL
        </Button>
        <Button variant="noBorder" onClick={() => setModalView(0)}>
          APPLY
        </Button>
      </div>
    </div>
  );
};

const useStyles = makeStyles({ name: { AccessSettings } })((theme) => ({
  italic: {
    fontStyle: "italic",
  },
  buttons: {
    display: "flex",
    alignItems: "center",
    justifyContent: "end",
    gap: theme.spacing(2),
    marginTop: theme.spacing(3),
  },
  visibilitySettings: {
    display: "flex",
    marginTop: theme.spacing(3),
    justifyContent: "space-between",
    alignItems: "center",
  },
  visibility: {
    display: "flex",
    gap: theme.spacing(1),
  },
  SettingInputWrapper: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: theme.spacing(3),
    marginTop: theme.spacing(3),
  },
  teamName: {
    display: "flex",
    alignItems: "center",
    gap: theme.spacing(3),
  },
  selectField: {
    flexGrow: "1",
  },
  divider: {
    padding: "0",
  },
}));

export default AccessSettings;
