import React from "react";
import { useState } from "react";

import { makeStyles } from "../../../../lib/ThemeProvider";
import { Divider } from "../../../DataDisplay";
import Switch from "../../../Inputs/Switch";
import { Text, Icon, IconButton } from "../../../theme";

interface ShareModalProps {
  name?: React.ReactNode;
  changeState: (value: { name: string; icon: React.ReactNode } | null) => void;
}

const ShareModal = (props: ShareModalProps) => {
  const { name } = props;
  const { classes } = useStyles();

  const [checked, setChecked] = useState<boolean>(false);

  function handleSwitch(event: React.ChangeEvent<HTMLInputElement>, checked: boolean) {
    setChecked(checked);
    console.log(checked);
  }

  return (
    <div>
      <Text typo="body 3" className={classes.italic}>
        {name ? name : ""}
      </Text>
      <div className={classes.visibilitySettings}>
        <div className={classes.visibility}>
          <Icon iconId="lock" size="small" />
          <div>
            <Text typo="body 2">Private</Text>
            <Text typo="body 3" className={classes.italic} color="secondary">
              Only you have access
            </Text>
          </div>
        </div>
        <IconButton iconId="edit" type="submit" iconVariant="focus" />
      </div>
      <Divider width="100%" color="gray" />
      <div className={classes.switcher}>
        <Switch checked={checked} onChecked={handleSwitch} />
        <Text typo="body 1">Protected by password</Text>
      </div>
      <Divider width="100%" color="gray" />
      <div>
        <Text typo="body 1">Set expiration date:</Text>
      </div>
    </div>
  );
};

const useStyles = makeStyles({ name: { ShareModal } })((theme) => ({
  selectInput: {
    margin: `${theme.spacing(3)}px 0px`,
  },
  bold: {
    fontWeight: 800,
  },
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
  },
  visibility: {
    display: "flex",
    gap: theme.spacing(1),
  },
  switcher: {
    display: "flex",
    alignItems: "center",
    // gap: theme.spacing(1),
  },
}));

export default ShareModal;
