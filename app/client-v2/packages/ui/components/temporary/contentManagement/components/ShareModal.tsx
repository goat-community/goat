import type { Dayjs } from "dayjs";
import React from "react";
import { useState } from "react";

import { makeStyles } from "../../../../lib/ThemeProvider";
import { Divider } from "../../../DataDisplay";
import { Switch, DatePicker, TextField } from "../../../Inputs";
import { Text, Icon, IconButton, Button } from "../../../theme";
import AccessSettings from "./AccessSettings";

interface ShareModalProps {
  name?: React.ReactNode;
  changeState: (value: { name: string; icon: React.ReactNode; value: string } | null) => void;
  modalState: { name: string; icon: React.ReactNode; value: string } | null;
}

const ShareModal = (props: ShareModalProps) => {
  const { name, changeState, modalState } = props;

  const { classes } = useStyles();

  // Component States
  const [checked, setChecked] = useState<boolean>(false);
  const [linkShareStatus, setLinkShareStatus] = useState<boolean>(true);
  const [date, setDate] = useState<Dayjs | null>(null);
  const [password, setPassword] = useState<string | null>(null);
  const [modalView, setModalView] = useState<number>(0);

  // Functions
  function handleSwitch(event: React.ChangeEvent<HTMLInputElement>, checked: boolean) {
    setChecked(checked);
  }

  function handleLinkSHareStatus(event: React.ChangeEvent<HTMLInputElement>, checked: boolean) {
    setLinkShareStatus(checked);
  }

  function enterAccessSettings() {
    setModalView(1);
    if (modalState) {
      const newState = modalState;
      newState.name = "Access Settings";
      changeState({
        name: "Access Settings",
        icon: newState.icon,
        value: newState.value,
      });
    }
  }

  return (
    <div>
      {modalView === 0 ? (
        <div>
          <Text typo="body 2" className={classes.italic}>
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
            <IconButton iconId="edit" type="submit" iconVariant="focus" onClick={enterAccessSettings} />
          </div>
          <Divider width="100%" color="gray" />
          <div className={classes.switcher}>
            <Switch checked={linkShareStatus} onChecked={handleLinkSHareStatus} />
            <Text typo="body 1">Allow link sharing</Text>
          </div>
          <div className={classes.switcher}>
            <Switch checked={checked} onChecked={handleSwitch} />
            <Text typo="body 1">Protected by password</Text>
          </div>
          {checked ? (
            <div style={{ marginTop: "8px" }}>
              <TextField
                label="Set Password"
                size="small"
                className={classes.shareInput}
                onValueBeingTypedChange={({ value }) => setPassword(value)}
              />
            </div>
          ) : null}
          <Divider width="100%" color="gray" />
          <div style={{ paddingBottom: "23px" }}>
            <Text typo="body 1">Set expiration date:</Text>
            <DatePicker
              ClassName={classes.dateInput}
              onChange={setDate}
              value={date}
              label="DD/MM/YY"
              size="small"
            />
          </div>
          <Divider width="100%" color="gray" />
          <div className={classes.shareInputWrapper}>
            <TextField
              defaultValue="https://www.figma.com/file/tu6pPILBRSUuy3Hbu8Lphk/Goat-3.0?type=design&node-id=12355-135723&mode=design&t=0W9nCyQtk2pQyAUU-0"
              size="small"
              className={classes.shareInput}
            />
            <Button>Copy</Button>
          </div>
          <div className={classes.buttons}>
            <Button variant="noBorder" onClick={() => changeState(null)}>
              CANCEL
            </Button>
            <Button variant="noBorder" onClick={() => changeState(null)}>
              SAVE
            </Button>
          </div>
        </div>
      ) : (
        <AccessSettings changeState={changeState} setModalView={setModalView} />
      )}
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
  dateInput: {
    width: "100%",
  },
  shareInput: {
    width: "100%",
  },
  shareInputWrapper: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    gap: theme.spacing(3),
    paddingBottom: "23px",
  },
}));

export default ShareModal;
