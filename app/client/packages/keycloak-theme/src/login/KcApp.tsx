/* eslint-disable @typescript-eslint/no-explicit-any */
import Fallback, { type PageProps } from "keycloakify/login";
import { lazy, Suspense } from "react";

import { makeStyles } from "../theme";
import { useI18n } from "./i18n";
import type { KcContext } from "./kcContext";

const Template = lazy(() => import("./Template"));
const RegisterUserProfile = lazy(() => import("./pages/RegisterUserProfile"));
const UpdateUserProfile = lazy(() => import("./pages/UpdateUserProfile"));
const UpdateEmail = lazy(() => import("./pages/UpdateEmail"));
const IdpReviewUserProfile = lazy(() => import("./pages/IdpReviewUserProfile"));
const SelectAuthenticator = lazy(() => import("./pages/SelectAuthenticator"));
const WebauthnAuthenticate = lazy(() => import("./pages/WebauthnAuthenticate"));
const Login = lazy(() => import("./pages/Login"));
const LoginVerifyEmail = lazy(() => import("./pages/LoginVerifyEmail"));
const LoginConfigTotp = lazy(() => import("./pages/LoginConfigTotp"));
const LoginUpdateProfile = lazy(() => import("./pages/LoginUpdateProfile"));
const LoginOtp = lazy(() => import("./pages/LoginOtp"));
const LoginPassword = lazy(() => import("./pages/LoginPassword"));
const LoginUsername = lazy(() => import("./pages/LoginUsername"));
const LoginResetPassword = lazy(() => import("./pages/LoginResetPassword"));
const LoginUpdatePassword = lazy(() => import("./pages/LoginUpdatePassword"));
const LoginPageExpired = lazy(() => import("./pages/LoginPageExpired"));
const LogoutConfirm = lazy(() => import("./pages/LogoutConfirm"));
const Info = lazy(() => import("./pages/Info"));
const Error = lazy(() => import("./pages/Error"));

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
          case "register-user-profile.ftl":
            return <RegisterUserProfile kcContext={kcContext} {...pageProps} />;
          case "update-user-profile.ftl":
            return <UpdateUserProfile kcContext={kcContext} {...pageProps} />;
          case "update-email.ftl":
            return <UpdateEmail kcContext={kcContext} {...pageProps} />;
          case "idp-review-user-profile.ftl":
            return <IdpReviewUserProfile kcContext={kcContext} {...pageProps} />;
          case "select-authenticator.ftl":
            return <SelectAuthenticator kcContext={kcContext} {...pageProps} />;
          case "webauthn-authenticate.ftl":
            return <WebauthnAuthenticate kcContext={kcContext} {...pageProps} />;
          case "login.ftl":
            return <Login kcContext={kcContext} {...pageProps} />;
          case "login-verify-email.ftl":
            return <LoginVerifyEmail kcContext={kcContext} {...pageProps} />;
          case "login-config-totp.ftl":
            return <LoginConfigTotp kcContext={kcContext} {...pageProps} />;
          case "login-update-profile.ftl":
            return <LoginUpdateProfile kcContext={kcContext} {...pageProps} />;
          case "login-password.ftl":
            return <LoginPassword kcContext={kcContext} {...pageProps} />;
          case "login-username.ftl":
            return <LoginUsername kcContext={kcContext} {...pageProps} />;
          case "login-otp.ftl":
            return <LoginOtp kcContext={kcContext} {...pageProps} />;
          case "login-reset-password.ftl":
            return <LoginResetPassword kcContext={kcContext} {...pageProps} />;
          case "login-update-password.ftl":
            return <LoginUpdatePassword kcContext={kcContext} {...pageProps} />;
          case "login-page-expired.ftl":
            return <LoginPageExpired kcContext={kcContext} {...pageProps} />;
          case "logout-confirm.ftl":
            return <LogoutConfirm kcContext={kcContext} {...pageProps} />;
          case "info.ftl":
            return <Info kcContext={kcContext} {...pageProps} />;
          case "error.ftl":
            return <Error kcContext={kcContext} {...pageProps} />;
          default:
            return (
              <Fallback
                kcContext={kcContext}
                i18n={i18n}
                Template={Template}
                doUseDefaultCss={pageProps.doUseDefaultCss}
              />
            );
        }
      })()}
    </Suspense>
  );
}

const useStyles = makeStyles({ name: { KcApp } })((theme) => ({
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
}));
