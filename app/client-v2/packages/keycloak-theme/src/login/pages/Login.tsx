/* eslint-disable react/jsx-curly-brace-presence */

/* eslint-disable react/jsx-no-undef */

/* eslint-disable @typescript-eslint/no-non-null-assertion */
// ejected using 'npx eject-keycloak-page'
import FormControlLabel from "@mui/material/FormControlLabel";
import Link from "@mui/material/Link";
import type { PageProps } from "keycloakify/login/pages/PageProps";
import { useConstCallback } from "keycloakify/tools/useConstCallback";
import { useStateRef } from "powerhooks/useStateRef";
import { useState, type FormEventHandler } from "react";

import { Checkbox } from "@p4b/ui/components/Checkbox";
import { TextField } from "@p4b/ui/components/Inputs";

import { makeStyles, Text, Button } from "../../theme";
import type { I18n } from "../i18n";
import type { KcContext } from "../kcContext";

export default function Login(props: PageProps<Extract<KcContext, { pageId: "login.ftl" }>, I18n>) {
  const { kcContext, i18n, doUseDefaultCss, Template, classes: classes_props } = props;

  const { social, realm, url, usernameEditDisabled, login, auth, registrationDisabled } = kcContext;

  const { msg, msgStr } = i18n;

  const [isLoginButtonDisabled, setIsLoginButtonDisabled] = useState(false);

  const onSubmit = useConstCallback<FormEventHandler<HTMLFormElement>>((e) => {
    e.preventDefault();

    setIsLoginButtonDisabled(true);

    const formElement = e.target as HTMLFormElement;

    //NOTE: Even if we login with email Keycloak expect username and password in
    //the POST request.
    formElement.querySelector("input[name='email']")?.setAttribute("name", "username");

    formElement.submit();
  });

  const { classes } = useStyles();

  const usernameInputRef = useStateRef<HTMLInputElement>(null);
  const passwordInputRef = useStateRef<HTMLInputElement>(null);
  const submitButtonRef = useStateRef<HTMLButtonElement>(null);

  return (
    <Template
      {...{ kcContext, i18n, doUseDefaultCss }}
      classes={classes_props}
      displayInfo={social.displayInfo}
      displayWide={realm.password && social.providers !== undefined}
      headerNode={msg("doLogIn")}
      i18n={i18n}
      infoNode={
        realm.password &&
        realm.registrationAllowed &&
        !registrationDisabled && (
          <div className={classes.linkToRegisterWrapper}>
            <Text typo="body 2" color="secondary">
              {msg("noAccount")!}
              <Link href={url.registrationUrl} className={classes.registerLink} underline="hover">
                {msg("doRegister")}
              </Link>
            </Text>
          </div>
        )
      }>
      <div className={classes.root}>
        {realm.password && social.providers !== undefined && (
          <>
            <div>
              <ul className={classes.providers}>
                {social.providers.map((p) => (
                  <li key={p.providerId}>
                    <Button href={p.loginUrl}>{p.displayName}</Button>
                  </li>
                ))}
              </ul>
            </div>
            <LoginDivider className={classes.divider} i18n={i18n} />
          </>
        )}
        <div>
          {realm.password && (
            <form onSubmit={onSubmit} action={url.loginAction} method="post">
              <div>
                <TextField
                  disabled={usernameEditDisabled}
                  defaultValue={login.username ?? ""}
                  id="username"
                  name="username"
                  inputProps_ref={usernameInputRef}
                  inputProps_aria-label="username"
                  inputProps_tabIndex={1}
                  inputProps_spellCheck={false}
                  label={
                    !realm.loginWithEmailAllowed
                      ? msg("username")
                      : !realm.registrationEmailAsUsername
                      ? msg("usernameOrEmail")
                      : msg("email")
                  }
                  autoComplete="off"
                />
              </div>
              <div>
                <TextField
                  type="password"
                  defaultValue={""}
                  id="password"
                  name="password"
                  inputProps_ref={passwordInputRef}
                  inputProps_aria-label="password"
                  inputProps_tabIndex={2}
                  label={msg("password")}
                  autoComplete="off"
                />
              </div>
              <div className={classes.rememberMeForgotPasswordWrapper}>
                <div>
                  {realm.rememberMe && !usernameEditDisabled && (
                    <FormControlLabel
                      control={
                        <Checkbox
                          tabIndex={3}
                          defaultChecked={!!login.rememberMe}
                          name="rememberMe"
                          color="primary"
                        />
                      }
                      label={<Text typo="body 2">{msg("rememberMe")!}</Text>}
                    />
                  )}
                </div>
                <div className={classes.forgotPassword}>
                  {realm.resetPasswordAllowed && (
                    <Link href={url.loginResetCredentialsUrl} underline="hover">
                      {msg("doForgotPassword")}
                    </Link>
                  )}
                </div>
              </div>
              <div className={classes.buttonsWrapper}>
                <input
                  type="hidden"
                  name="credentialId"
                  {...(auth?.selectedCredential !== undefined
                    ? {
                        value: auth.selectedCredential,
                      }
                    : {})}
                />
                <Button
                  ref={submitButtonRef}
                  className={classes.buttonSubmit}
                  name="login"
                  type="submit"
                  disabled={isLoginButtonDisabled}>
                  {msgStr("continue")}
                </Button>
              </div>
            </form>
          )}
        </div>
      </div>
    </Template>
  );
}

const useStyles = makeStyles({ name: { Login } })((theme) => ({
  root: {
    "& .MuiTextField-root": {
      width: "100%",
      marginTop: theme.spacing(5),
    },
  },
  rememberMeForgotPasswordWrapper: {
    display: "flex",
    marginTop: theme.spacing(4),
  },
  forgotPassword: {
    flex: 1,
    display: "flex",
    justifyContent: "flex-end",
    alignItems: "center",
  },
  buttonsWrapper: {
    marginTop: theme.spacing(4),
    display: "flex",
    justifyContent: "flex-end",
  },
  buttonSubmit: {
    width: "100%",
    marginTop: theme.spacing(2),
    marginLeft: theme.spacing(0),
  },
  linkToRegisterWrapper: {
    marginTop: theme.spacing(5),
    textAlign: "center",
    "& > *": {
      display: "inline-block",
    },
  },
  registerLink: {
    paddingLeft: theme.spacing(2),
  },
  divider: {
    ...theme.spacing.topBottom("margin", 5),
  },
  providers: {
    listStyleType: "none",
    padding: 0,
  },
}));

const { LoginDivider } = (() => {
  type Props = {
    className?: string;
    i18n: I18n;
  };

  function LoginDivider(props: Props) {
    const { className, i18n } = props;

    const { msg } = i18n;

    const { classes, cx } = useStyles();

    const separator = <div role="separator" className={classes.separator} />;

    return (
      <div className={cx(classes.root, className)}>
        {separator}
        <Text typo="body 2" color="secondary" className={classes.text}>
          {msg("or")}
        </Text>
        {separator}
      </div>
    );
  }

  const useStyles = makeStyles({ name: { LoginDivider } })((theme) => ({
    root: {
      display: "flex",
      alignItems: "center",
    },
    separator: {
      height: 1,
      backgroundColor: theme.colors.useCases.typography.textSecondary,
      flex: 1,
    },
    text: {
      ...theme.spacing.rightLeft("margin", 2),
      paddingBottom: 2,
    },
  }));

  return { LoginDivider };
})();
