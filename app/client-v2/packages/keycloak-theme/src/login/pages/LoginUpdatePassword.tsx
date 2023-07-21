import FormControlLabel from "@mui/material/FormControlLabel";
import type { PageProps } from "keycloakify/login/pages/PageProps";

import { Checkbox } from "@p4b/ui/components/Checkbox";
import { TextField } from "@p4b/ui/components/Inputs/TextField";

import { makeStyles, Text, Button } from "../../theme";
import type { I18n } from "../i18n";
import type { KcContext } from "../kcContext";

export default function LoginUpdatePassword(
  props: PageProps<Extract<KcContext, { pageId: "login-update-password.ftl" }>, I18n>
) {
  const { kcContext, i18n, doUseDefaultCss, Template } = props;

  const { msg, msgStr } = i18n;

  const { url, isAppInitiatedAction, username } = kcContext;
  const { classes } = useStyles();
  console.log("classes", classes);
  return (
    <Template {...{ kcContext, i18n, doUseDefaultCss }} headerNode={msg("updatePasswordTitle")}>
      <form id="kc-passwd-update-form" action={url.loginAction} method="post" className={classes.root}>
        <div style={{ display: "none" }}>
          <TextField
            type="text"
            id="username"
            name="username"
            defaultValue={username}
            disabled={true}
            autoComplete="username"
          />
        </div>

        <div style={{ display: "none" }}>
          <TextField type="password" id="password" name="password" autoComplete="current-password" />
        </div>

        <TextField
          type="password"
          id="password-new"
          name="password-new"
          inputProps_aria-label="password-new"
          inputProps_tabIndex={1}
          label={msg("passwordNew")}
          autoComplete="new-password"
        />

        <TextField
          type="password"
          id="password-confirm"
          name="password-confirm"
          inputProps_aria-label="password-confirm"
          inputProps_tabIndex={2}
          label={msg("passwordConfirm")}
          autoComplete="new-password"
        />

        <div>
          <div id="kc-form-options">
            <div>
              {isAppInitiatedAction && (
                <FormControlLabel
                  className={classes.logoutCheckbox}
                  control={
                    <Checkbox
                      tabIndex={3}
                      id="logout-sessions"
                      name="logout-sessions"
                      defaultChecked={true}
                      color="primary"
                    />
                  }
                  label={<Text typo="body 2">{msgStr("logoutOtherSessions")}</Text>}
                />
              )}
            </div>
          </div>

          <div id="kc-form-buttons">
            {isAppInitiatedAction ? (
              <>
                <Button variant="primary" className={classes.buttonSubmit} type="submit">
                  {msgStr("doSubmit")}
                </Button>
                <Button variant="secondary" name="cancel-aia" className={classes.buttonSubmit} type="submit">
                  {msgStr("doCancel")}
                </Button>
              </>
            ) : (
              <Button variant="primary" className={classes.buttonSubmit} type="submit">
                {msgStr("doSubmit")}
              </Button>
            )}
          </div>
        </div>
      </form>
    </Template>
  );
}

const useStyles = makeStyles({ name: { LoginUpdatePassword } })((theme) => ({
  root: {
    "& .MuiTextField-root": {
      width: "100%",
      marginTop: theme.spacing(5),
    },
  },
  logoutCheckbox: {
    marginTop: theme.spacing(2),
  },
  buttonSubmit: {
    width: "100%",
    marginTop: theme.spacing(4),
  },
}));
