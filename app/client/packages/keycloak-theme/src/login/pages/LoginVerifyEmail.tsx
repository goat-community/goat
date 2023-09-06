import { Link, Step, StepLabel, Stepper } from "@mui/material";
import type { PageProps } from "keycloakify/login/pages/PageProps";

import { makeStyles } from "../../../src/theme";
import { Button } from "@mui/material";
import type { I18n } from "../i18n";
import type { KcContext } from "../kcContext";

export default function LoginVerifyEmail(
  props: PageProps<Extract<KcContext, { pageId: "login-verify-email.ftl" }>, I18n>
) {
  const { kcContext, i18n, doUseDefaultCss, Template } = props;

  const { msg, msgStr } = i18n;

  const { url } = kcContext;

  const { classes } = useStyles();

  return (
    <Template
      {...{ kcContext, i18n, doUseDefaultCss }}
      displayMessage={false}
      headerNode={msg("verifyEmail")}>
      <Stepper activeStep={2} className={classes.stepper}>
        {[1, 2, 3].map((label) => (
          <Step sx={{ paddingRight: 0 }} key={label}>
            <StepLabel> </StepLabel>
          </Step>
        ))}
      </Stepper>

      <p className="instruction">{msg("emailVerifyInstruction")}</p>
      <div className={classes.actionButtonWrapper}>
        {(() => {
          const button = (
            <Link href={url.loginAction}>
              <Button className={classes.buttonSubmit} type="submit">
                {msgStr("resendEmail")}
              </Button>
            </Link>
          );

          return button;
        })()}
      </div>
    </Template>
  );
}

const useStyles = makeStyles({ name: { LoginVerifyEmail } })((theme) => ({
  root: {
    "& .MuiTextField-root": {
      width: "100%",
      marginTop: theme.spacing(5),
    },
  },
  actionButtonWrapper: {
    marginTop: theme.spacing(2),
    display: "flex",
    justifyContent: "flex-end",
    "& a": {
      width: "100%",
    },
  },
  buttonSubmit: {
    marginTop: theme.spacing(2),
    marginLeft: theme.spacing(0),
    width: "100%",
  },
  stepper: {
    marginBottom: theme.spacing(4),
  },
}));
