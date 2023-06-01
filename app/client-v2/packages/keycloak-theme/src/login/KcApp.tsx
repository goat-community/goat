/* eslint-disable @typescript-eslint/no-explicit-any */
import Fallback, { type PageProps } from "keycloakify/login";
import { lazy, Suspense } from "react";

import { makeStyles } from "../theme";
import { useI18n } from "./i18n";
import type { KcContext } from "./kcContext";

const Template = lazy(() => import("./Template"));
const DefaultTemplate = lazy(() => import("keycloakify/login/Template"));
const Login = lazy(() => import("./pages/Login"));
const RegisterUserProfile = lazy(() => import("./pages/RegisterUserProfile"));
const LoginVerifyEmail = lazy(() => import("./pages/LoginVerifyEmail"));
const LoginResetPassword = lazy(() => import("./pages/LoginResetPassword"));
const Info = lazy(() => import("./pages/Info"));

export default function KcApp(props: { kcContext: KcContext }) {
  const { kcContext } = props;

  const i18n = useI18n({ kcContext });

  const { classes } = useStyles();

  if (i18n === null) {
    return null;
  }
  const pageProps: Omit<PageProps<any, typeof i18n>, "kcContext"> = {
    i18n,
    Template,
    doUseDefaultCss: false,
    classes: {
      kcHtmlClass: classes.kcHtmlClass,
    },
  };

  return (
    <Suspense>
      {(() => {
        switch (kcContext.pageId) {
          case "login.ftl":
            return <Login kcContext={kcContext} {...pageProps} />;
          case "register-user-profile.ftl":
            return <RegisterUserProfile kcContext={kcContext} {...pageProps} />;
          case "login-verify-email.ftl":
            return <LoginVerifyEmail kcContext={kcContext} {...pageProps} />;
          case "login-reset-password.ftl":
            return <LoginResetPassword kcContext={kcContext} {...pageProps} />;
          case "info.ftl":
            return <Info kcContext={kcContext} {...pageProps} />;
          default:
            return (
              <Fallback
                kcContext={kcContext}
                i18n={i18n}
                Template={DefaultTemplate}
                doUseDefaultCss={true}
                classes={{
                  kcHtmlClass: classes.kcHtmlClass,
                  kcLoginClass: classes.kcLoginClass,
                  kcFormCardClass: classes.kcFormCardClass,
                  kcButtonPrimaryClass: classes.kcButtonPrimaryClass,
                  kcInputClass: classes.kcInputClass,
                }}
              />
            );
        }
      })()}
    </Suspense>
  );
}

const useStyles = makeStyles({ name: { KcApp } })((theme) => ({
  kcLoginClass: {
    "& #kc-locale": {
      zIndex: 5,
    },
  },
  kcHtmlClass: {
    "& body": {
      fontFamily: theme.typography.fontFamily,
    },
    background: `${theme.colors.useCases.surfaces.background}`,
    "& a": {
      color: `${theme.colors.useCases.typography.textFocus}`,
    },
    "& #kc-current-locale-link": {
      color: `${theme.colors.palette.light.greyVariant3}`,
    },
    "& label": {
      fontSize: 14,
      color: theme.colors.palette.light.greyVariant3,
      fontWeight: "normal",
    },
    "& #kc-page-title": {
      ...theme.typography.variants["page heading"].style,
      color: theme.colors.palette.dark.main,
    },
    "& #kc-header-wrapper": {
      visibility: "hidden",
    },
  },
  kcFormCardClass: {
    borderRadius: 10,
  },
  kcButtonPrimaryClass: {
    backgroundColor: "unset",
    backgroundImage: "unset",
    borderColor: `${theme.colors.useCases.typography.textFocus}`,
    borderWidth: "2px",
    borderRadius: `20px`,
    color: `${theme.colors.useCases.typography.textFocus}`,
    textTransform: "uppercase",
  },
  kcInputClass: {
    borderRadius: "unset",
    border: "unset",
    boxShadow: "unset",
    borderBottom: `1px solid ${theme.colors.useCases.typography.textTertiary}`,
    "&:focus": {
      borderColor: "unset",
      borderBottom: `1px solid ${theme.colors.useCases.typography.textFocus}`,
    },
  },
}));
