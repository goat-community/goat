import { Link } from "@mui/material";
import type { PageProps } from "keycloakify/login/pages/PageProps";

import { TextField } from "@p4b/ui/components/Inputs/TextField";

import { makeStyles, Text } from "../../theme";
import { Button } from "@mui/material";
import type { I18n } from "../i18n";
import type { KcContext } from "../kcContext";

export default function LoginResetPassword(
  props: PageProps<Extract<KcContext, { pageId: "login-reset-password.ftl" }>, I18n>
) {
  const { kcContext, i18n, doUseDefaultCss, Template } = props;

  const { url, auth } = kcContext;

  const { msg, msgStr } = i18n;
  const { classes } = useStyles();

  return (
    <Template
      {...{ kcContext, i18n, doUseDefaultCss }}
      displayMessage={false}
      headerNode={msg("emailForgotTitle")}>
      <Text typo="body 2" color="primary">
        {msg("emailForgotInstruction")}
      </Text>
      <div className={classes.root}>
        <form id="kc-reset-password-form" action={url.loginAction} method="post">
          <TextField
            defaultValue={auth !== undefined && auth.showUsername ? auth.attemptedUsername : undefined}
            id="username"
            name="username"
            inputProps_aria-label="username"
            inputProps_tabIndex={1}
            inputProps_autoFocus={true}
            inputProps_spellCheck={false}
            label={msg("email")}
            autoComplete="off"
          />
          <div>
            <div id="kc-form-buttons">
              <Button className={classes.buttonSubmit} type="submit">
                {msgStr("doSubmit")}
              </Button>
            </div>
            <div id="kc-form-options" className={classes.linkToLogin}>
              <Link underline="hover" href={url.loginUrl}>
                {msg("backToLogin")}
              </Link>
            </div>
          </div>
        </form>
      </div>
    </Template>
  );
}

const useStyles = makeStyles({ name: { LoginResetPassword } })((theme) => ({
  root: {
    "& .MuiTextField-root": {
      width: "100%",
      marginTop: theme.spacing(5),
    },
  },
  buttonSubmit: {
    width: "100%",
    marginTop: theme.spacing(6),
  },
  linkToLogin: {
    marginTop: theme.spacing(5),
  },
}));
