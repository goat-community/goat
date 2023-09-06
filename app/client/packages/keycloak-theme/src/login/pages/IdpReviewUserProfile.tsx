import type { PageProps } from "keycloakify/login/pages/PageProps";
import { useState } from "react";

import { makeStyles } from "../../theme";
import { Button } from "@mui/material";
import type { I18n } from "../i18n";
import type { KcContext } from "../kcContext";
import { UserProfileFormFields } from "./shared/UserProfileFormFields";

export default function IdpReviewUserProfile(
  props: PageProps<Extract<KcContext, { pageId: "idp-review-user-profile.ftl" }>, I18n>
) {
  const { kcContext, i18n, doUseDefaultCss, Template } = props;

  const { classes } = useStyles();

  const { msg, msgStr } = i18n;

  const { url } = kcContext;

  const [isFomSubmittable, setIsFomSubmittable] = useState(false);

  const getIncrementedTabIndex = (() => {
    let counter = 1;
    return () => counter++;
  })();

  return (
    <Template {...{ kcContext, i18n, doUseDefaultCss }} headerNode={msg("loginIdpReviewProfileTitle")}>
      <form id="kc-idp-review-profile-form" action={url.loginAction} method="post" className={classes.root}>
        <UserProfileFormFields
          kcContext={kcContext}
          onIsFormSubmittableValueChange={setIsFomSubmittable}
          i18n={i18n}
          getIncrementedTabIndex={getIncrementedTabIndex}
        />

        <Button
          className={classes.buttonSubmit}
          type="submit"
          disabled={!isFomSubmittable}
          tabIndex={getIncrementedTabIndex()}>
          {msgStr("doSubmit")}
        </Button>
      </form>
    </Template>
  );
}

const useStyles = makeStyles({ name: { IdpReviewUserProfile } })((theme) => ({
  root: {
    "& .MuiTextField-root": {
      width: "100%",
      marginTop: theme.spacing(5),
    },
  },
  buttonSubmit: {
    width: "100%",
    marginTop: theme.spacing(5),
    marginLeft: theme.spacing(0),
  },
}));
