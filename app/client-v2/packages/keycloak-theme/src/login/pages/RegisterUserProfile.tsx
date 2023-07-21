import { Tooltip } from "@mui/material";
import Link from "@mui/material/Link";
import type { PageProps } from "keycloakify/login/pages/PageProps";
import { useRef, useState } from "react";
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import ReCAPTCHA from "react-google-recaptcha";

import { makeStyles, Button, Text } from "../../theme";
import type { I18n } from "../i18n";
import type { KcContext } from "../kcContext";
import { UserProfileFormFields } from "./shared/UserProfileFormFields";

interface Steps {
  [key: number]: string[];
}

const steps: Steps = {
  1: ["firstName", "lastName", "country", "profession", "domain"],
  2: ["email", "username", "password", "password-confirm", "terms_and_conditions", "subscribe_to_newsletter"],
  3: [""], // verify email (last step). This step is not used in this form even though it's shown in the stepper
};

export default function RegisterUserProfile(
  props: PageProps<Extract<KcContext, { pageId: "register-user-profile.ftl" }>, I18n>
) {
  const isDarkModeEnabled = false;
  const { kcContext, i18n, doUseDefaultCss, Template } = props;
  const { url, messagesPerField, recaptchaRequired, recaptchaSiteKey } = kcContext;
  const { msg, msgStr } = i18n;
  const [activeStep, setActiveStep] = useState(0);
  const [isFormSubmittable, setIsFormSubmittable] = useState(false);
  const [isCaptchaValid, setIsCaptchaValid] = useState(false);
  const captchaRef = useRef(null);

  const { classes } = useStyles({
    activeStep,
  });

  const getIncrementedTabIndex = (() => {
    let counter = 1;
    return () => counter++;
  })();

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  return (
    <Template
      {...{ kcContext, i18n, doUseDefaultCss }}
      displayInfo={true}
      displayMessage={messagesPerField.exists("global")}
      displayRequiredFields={false}
      i18n={i18n}
      infoNode={
        <div className={classes.linkToSignInWrapper}>
          <Text typo="body 2" color="secondary">
            {msg("alreadyHaveAccount")}
            <Link href={url.loginUrl} className={classes.linkToSignIn} underline="hover">
              {msg("doLogIn")}
            </Link>
          </Text>
        </div>
      }
      headerNode={msg("doRegister")}>
      <form className={classes.root} action={url.registrationAction} method="post">
        <UserProfileFormFields
          kcContext={kcContext}
          onIsFormSubmittableValueChange={setIsFormSubmittable}
          activeStep={activeStep}
          steps={steps}
          i18n={i18n}
          getIncrementedTabIndex={getIncrementedTabIndex}
        />

        {recaptchaRequired && (
          <div>
            <div>
              <ReCAPTCHA
                id="recaptcha"
                hl={i18n.currentLanguageTag}
                theme={isDarkModeEnabled ? "dark" : "light"}
                className={classes.recaptcha}
                sitekey={recaptchaSiteKey}
                onChange={() => setIsCaptchaValid(true)}
                onExpired={() => setIsCaptchaValid(false)}
                onErrored={() => setIsCaptchaValid(false)}
                ref={captchaRef}
              />
            </div>
          </div>
        )}
        <div className={classes.buttonsWrapper}>
          {(() => {
            const button = (
              <Button
                className={classes.buttonSubmit}
                disabled={!isFormSubmittable || (recaptchaRequired && !isCaptchaValid)}
                type="submit"
                tabIndex={getIncrementedTabIndex()}>
                {msgStr("getStarted")}
              </Button>
            );

            return activeStep == 1 ? (
              isFormSubmittable ? (
                button
              ) : (
                <Tooltip title={msg("formNotFilledProperly")}>
                  <span>{button}</span>
                </Tooltip>
              )
            ) : null;
          })()}
        </div>
      </form>
      {activeStep == 0 && (
        <Button className={classes.buttonNextBack} onClick={handleNext}>
          {msgStr("next")}
        </Button>
      )}
      {activeStep == 1 && (
        <Button className={classes.buttonNextBack} onClick={handleBack} variant="secondary">
          {msgStr("back")}
        </Button>
      )}
    </Template>
  );
}

const useStyles = makeStyles<{ activeStep: number }>({ name: { RegisterUserProfile } })(
  (theme, { activeStep }) => ({
    root: {
      "& .MuiTextField-root": {
        width: "100%",
        marginTop: theme.spacing(5),
      },
    },
    linkToSignInWrapper: {
      marginTop: theme.spacing(5),
      textAlign: "center",
      "& > *": {
        display: "inline-block",
      },
    },
    linkToSignIn: {
      paddingLeft: theme.spacing(2),
    },
    buttonsWrapper: {
      marginTop: theme.spacing(2),
      display: "flex",
      justifyContent: "flex-end",
      "& span": {
        width: "100%",
      },
    },
    buttonNextBack: {
      marginTop: theme.spacing(3),
      width: "100%",
    },
    buttonSubmit: {
      marginTop: theme.spacing(2),
      marginLeft: theme.spacing(0),
      width: "100%",
    },
    recaptcha: {
      marginTop: theme.spacing(2),
      display: activeStep == 1 ? "block" : "none",
    },
  })
);
